import os, re, time, json, hmac, hashlib, base64, socket, ipaddress
from urllib.parse import urljoin, urlparse, urlencode

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

APP_NAME = "ResenhaFlix Manga Bridge"
REPO_MIN = os.getenv("MANGA_REPO", "https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
SECRET = os.getenv("BRIDGE_SECRET", "change-me-in-production").encode()
TEST_HOSTS = {x.strip().lower() for x in os.getenv("ALLOW_TEST_HOSTS","").split(",") if x.strip()}
UA = os.getenv("MANGA_USER_AGENT", "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/131 Mobile Safari/537.36")

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOWED_ORIGIN == "*" else [ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

client = httpx.AsyncClient(
    follow_redirects=True,
    timeout=httpx.Timeout(12.0, connect=6.0),
    headers={"User-Agent":UA,"Accept-Language":"pt-BR,pt;q=0.9,en;q=0.6"},
)

ALLOWED_HOSTS=set()
CACHE={}
CACHE_TTL=300

class Source(BaseModel):
    id: str = ""
    name: str = "Fonte"
    lang: str = "all"
    homeUrl: str
    extension: str = ""

class SearchBody(BaseModel):
    source: Source
    query: str = ""

class UrlBody(BaseModel):
    source: Source
    url: str

def host(url: str):
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

def private_host(h: str):
    if h in TEST_HOSTS:
        return False
    try:
        infos=socket.getaddrinfo(h,None)
        for info in infos:
            ip=ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
    except Exception:
        pass
    return False

async def refresh_allowlist():
    global ALLOWED_HOSTS
    if ALLOWED_HOSTS:
        return
    urls=[REPO_MIN]
    if REPO_MIN.endswith("index.min.json"):
        urls.append(REPO_MIN[:-len("index.min.json")]+"index.json")
    for u in urls:
        try:
            r=await client.get(u)
            if r.status_code!=200:
                continue
            data=r.json()
            raw=data if isinstance(data,list) else data.get("extensionList",{}).get("extensions",[])
            found=set()
            for ext in raw:
                for s in ext.get("sources",[]) or []:
                    h=host(s.get("homeUrl") or s.get("baseUrl") or "")
                    if h: found.add(h)
            if len(found)>10:
                ALLOWED_HOSTS=found|TEST_HOSTS
                return
        except Exception:
            continue
    ALLOWED_HOSTS |= TEST_HOSTS

async def validate_source(source: Source):
    await refresh_allowlist()
    h=host(source.homeUrl)
    if not h or private_host(h):
        raise HTTPException(400,"Host de fonte inválido")
    if ALLOWED_HOSTS and h not in ALLOWED_HOSTS and h not in TEST_HOSTS:
        raise HTTPException(403,"Fonte não pertence ao repositório permitido")
    return h

def validate_same_source(source: Source, url: str):
    sh=host(source.homeUrl); uh=host(url)
    if not uh or (uh!=sh and not uh.endswith("."+sh)):
        raise HTTPException(400,"URL fora do domínio da fonte")

def cache_get(key):
    x=CACHE.get(key)
    if not x:return None
    if time.time()-x["at"]>CACHE_TTL:
        CACHE.pop(key,None);return None
    return x["value"]

def cache_set(key,value):
    CACHE[key]={"at":time.time(),"value":value}
    if len(CACHE)>500:
        for k in list(CACHE)[:100]:CACHE.pop(k,None)

async def fetch_html(url, referer=None):
    headers={"Accept":"text/html,application/xhtml+xml"}
    if referer:headers["Referer"]=referer
    r=await client.get(url,headers=headers)
    if r.status_code>=400:
        raise HTTPException(502,f"Fonte respondeu HTTP {r.status_code}")
    return r.text, str(r.url)

def text(el):
    return " ".join(el.stripped_strings).strip() if el else ""

def attr_img(img):
    if not img:return ""
    for k in ("data-src","data-lazy-src","data-original","data-url","src"):
        v=(img.get(k) or "").strip()
        if v and not v.startswith("data:"):return v
    return ""

def parse_number(name):
    s=(name or "").replace(",",".")
    m=re.search(r"(?:cap(?:ítulo|itulo|\.)?|chapter|ch\.?)\s*#?\s*(\d+(?:\.\d+)?)",s,re.I)
    if not m:m=re.search(r"(\d+(?:\.\d+)?)",s)
    return float(m.group(1)) if m else None

SEARCH_SELECTORS=[
    ".c-tabs-item__content",".page-item-detail",".row.c-tabs-item__content",
    ".bs .bsx",".listupd .bs",".manga__item",".manga-item",".page-listing-item"
]
def parse_cards(html, base, source):
    soup=BeautifulSoup(html,"html.parser");out=[];seen=set()
    for sel in SEARCH_SELECTORS:
        for el in soup.select(sel):
            a=el.select_one("a[href]");img=el.select_one("img")
            if not a:continue
            title=text(el.select_one("h3,h4,.post-title,.tab-summary,.tt,.manga-name")) or (a.get("title") or "").strip() or (img.get("alt","").strip() if img else "")
            url=urljoin(base,a.get("href",""));thumb=urljoin(base,attr_img(img))
            if len(title)<2 or not url or url in seen:continue
            seen.add(url);out.append({"title":title,"url":url,"thumbnail":thumb,"source":source.model_dump()})
        if len(out)>=24:break
    return out[:24]

def search_urls(base,q):
    base=base.rstrip("/");qq=urlencode({"s":q})
    return [
        f"{base}/?s={httpx.QueryParams({'s':q,'post_type':'wp-manga'})}",
        f"{base}/?{qq}",
        f"{base}/search?{urlencode({'q':q})}",
        f"{base}/buscar?{urlencode({'q':q})}",
        f"{base}/busca?{urlencode({'q':q})}",
    ]

def sign_image(url,referer):
    payload=json.dumps({"url":url,"referer":referer,"exp":int(time.time())+3600},separators=(",",":")).encode()
    token=base64.urlsafe_b64encode(payload).decode().rstrip("=")
    sig=hmac.new(SECRET,token.encode(),hashlib.sha256).hexdigest()
    return token,sig

def proxy_url(req:Request,url,referer):
    token,sig=sign_image(url,referer)
    return str(req.base_url).rstrip("/")+f"/api/image?token={token}&sig={sig}"

@app.get("/api/health")
async def health():
    await refresh_allowlist()
    return {"ok":True,"name":APP_NAME,"allowedHosts":len(ALLOWED_HOSTS)}

@app.post("/api/search")
async def search(body:SearchBody):
    await validate_source(body.source)
    key=("search",body.source.homeUrl,body.query.lower())
    hit=cache_get(key)
    if hit is not None:return {"items":hit,"cached":True}
    last=None
    for url in search_urls(body.source.homeUrl,body.query):
        try:
            html,final=await fetch_html(url,body.source.homeUrl)
            items=parse_cards(html,final,body.source)
            if items:
                cache_set(key,items);return {"items":items,"cached":False}
        except Exception as e:last=e
    if isinstance(last,HTTPException):raise last
    return {"items":[]}

@app.post("/api/popular")
async def popular(body:SearchBody):
    await validate_source(body.source)
    key=("popular",body.source.homeUrl)
    hit=cache_get(key)
    if hit is not None:return {"items":hit,"cached":True}
    html,final=await fetch_html(body.source.homeUrl,body.source.homeUrl)
    items=parse_cards(html,final,body.source)
    cache_set(key,items)
    return {"items":items,"cached":False}

@app.post("/api/manga")
async def manga(body:UrlBody, request:Request):
    await validate_source(body.source);validate_same_source(body.source,body.url)
    key=("manga",body.url);hit=cache_get(key)
    if hit is not None:return hit
    html,final=await fetch_html(body.url,body.source.homeUrl);soup=BeautifulSoup(html,"html.parser")
    title=text(soup.select_one("h1,.post-title h1,.manga-title h1,.post-title")) or "Mangá"
    cover_el=soup.select_one(".summary_image img,.manga-thumb img,.tab-summary img,.summary-image img")
    cover=urljoin(final,attr_img(cover_el))
    desc=text(soup.select_one(".summary__content,.description-summary,.manga-excerpt,.description,.manga-summary"))
    chapters=[];seen=set()
    selectors=".wp-manga-chapter a,.chapter-link-item a,.chapter-name a,.eph-num a,a[href*='/capitulo'],a[href*='/chapter']"
    for a in soup.select(selectors):
        u=urljoin(final,a.get("href",""));name=text(a)
        if not u or not name or u in seen:continue
        if host(u)!=host(body.source.homeUrl) and not host(u).endswith("."+host(body.source.homeUrl)):continue
        seen.add(u);chapters.append({"name":name,"url":u,"number":parse_number(name)})
    chapters.sort(key=lambda x:(x["number"] is None,x["number"] if x["number"] is not None else 999999))
    result={"title":title,"cover":cover,"description":desc,"url":final,"chapters":chapters,"source":body.source.model_dump()}
    cache_set(key,result);return result

@app.post("/api/chapter")
async def chapter(body:UrlBody, request:Request):
    await validate_source(body.source);validate_same_source(body.source,body.url)
    key=("chapter",body.url);hit=cache_get(key)
    if hit is not None:return hit
    html,final=await fetch_html(body.url,body.source.homeUrl);soup=BeautifulSoup(html,"html.parser")
    selectors=".reading-content img,.page-break img,.reader-area img,.chapter-content img,.reading-content .page-break img,.container-chapter-reader img"
    pages=[];seen=set()
    for img in soup.select(selectors):
        raw=attr_img(img);u=urljoin(final,raw)
        if not u or u in seen:continue
        low=u.lower()
        if any(x in low for x in ("logo","avatar","icon","banner")):continue
        seen.add(u);pages.append({"image":proxy_url(request,u,final),"original":u})
    if not pages:
        candidates=re.findall(r'https?://[^"\'<>\s]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\'<>\s]*)?',html,re.I)
        for u in candidates:
            if u in seen:continue
            seen.add(u);pages.append({"image":proxy_url(request,u,final),"original":u})
            if len(pages)>=100:break
    if not pages:raise HTTPException(422,"Nenhuma página foi encontrada por este adaptador genérico")
    result={"pages":pages}
    cache_set(key,result);return result

@app.get("/api/image")
async def image(token:str,sig:str):
    expected=hmac.new(SECRET,token.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,sig):raise HTTPException(403,"Assinatura inválida")
    try:
        pad="="*((4-len(token)%4)%4);data=json.loads(base64.urlsafe_b64decode(token+pad))
    except Exception:raise HTTPException(400,"Token inválido")
    if int(data.get("exp",0))<time.time():raise HTTPException(403,"Token expirado")
    url=data.get("url","");referer=data.get("referer","")
    if not url.startswith(("http://","https://")):raise HTTPException(400,"URL inválida")
    r=await client.get(url,headers={"Referer":referer,"Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
    if r.status_code>=400:raise HTTPException(502,f"Imagem HTTP {r.status_code}")
    ct=r.headers.get("content-type","image/jpeg")
    return Response(r.content,media_type=ct,headers={"Cache-Control":"public,max-age=3600"})

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
