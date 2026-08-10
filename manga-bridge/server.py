import os, re, json, time, hmac, hashlib, base64, asyncio
from urllib.parse import urljoin, urlparse, urlencode

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

app=FastAPI(title="ResenhaFlix Manga Bridge v16")
origin=os.getenv("ALLOWED_ORIGIN","*")
secret=os.getenv("BRIDGE_SECRET","resenhaflix-change-this").encode()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origin=="*" else [origin],
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

client=httpx.AsyncClient(
    follow_redirects=True,
    timeout=httpx.Timeout(9.0,connect=5.0),
    headers={
      "User-Agent":os.getenv("MANGA_USER_AGENT","Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/131 Mobile Safari/537.36"),
      "Accept-Language":"pt-BR,pt;q=0.9,en;q=0.7",
    },
)

class Source(BaseModel):
    id:str=""
    name:str="Fonte"
    lang:str="all"
    homeUrl:str
    extension:str=""
    pkg:str=""
    repo:str=""

class SearchBody(BaseModel):
    source:Source
    query:str=""

class UrlBody(BaseModel):
    source:Source
    url:str

class BatchSearchBody(BaseModel):
    sources:list[Source]
    query:str=""

def host(url):
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

def source_base(source):
    return source.homeUrl.rstrip("/")

def same_source(source,url):
    a=host(source.homeUrl);b=host(url)
    return bool(a and b and (a==b or b.endswith("."+a)))

def text(el):
    return " ".join(el.stripped_strings).strip() if el else ""

def image_attr(img):
    if not img:return ""
    for k in ("data-src","data-lazy-src","data-original","data-url","src"):
        v=(img.get(k) or "").strip()
        if v and not v.startswith("data:"):return v
    return ""

def chapter_number(name):
    s=(name or "").replace(",",".")
    m=re.search(r"(?:cap(?:ítulo|itulo|\.)?|chapter|ch\.?)\s*#?\s*(\d+(?:\.\d+)?)",s,re.I)
    if not m:m=re.search(r"(\d+(?:\.\d+)?)",s)
    return float(m.group(1)) if m else None

async def get_html(url,referer=None,timeout=7):
    headers={"Accept":"text/html,application/xhtml+xml"}
    if referer:headers["Referer"]=referer
    r=await client.get(url,headers=headers,timeout=timeout)
    if r.status_code>=400:raise HTTPException(502,f"Fonte HTTP {r.status_code}")
    return r.text,str(r.url)

async def post_form(url,data,referer=None,timeout=7):
    headers={"Accept":"text/html,*/*","X-Requested-With":"XMLHttpRequest"}
    if referer:headers["Referer"]=referer
    r=await client.post(url,data=data,headers=headers,timeout=timeout)
    if r.status_code>=400:raise HTTPException(r.status_code,f"Fonte HTTP {r.status_code}")
    return r.text,str(r.url)

def source_dict(source):
    return source.model_dump()

def adapter_name(source):
    p=(source.pkg or "").lower()
    h=host(source.homeUrl)
    if p.endswith(".saikaiscan") or "housesaikai" in h or source.name.lower()=="saikai scan":
        return "saikai"
    if p.endswith(".lermangas"):
        return "madara"
    if p.endswith(".mangotoons"):
        return "login-required"
    return "auto"

# ---------- signed image proxy ----------
def sign_image(url,referer):
    payload=json.dumps({"u":url,"r":referer,"e":int(time.time())+3600},separators=(",",":")).encode()
    token=base64.urlsafe_b64encode(payload).decode().rstrip("=")
    sig=hmac.new(secret,token.encode(),hashlib.sha256).hexdigest()
    return token,sig

def proxied_image(request,url,referer):
    token,sig=sign_image(url,referer)
    return str(request.base_url).rstrip("/")+"/api/image?"+urlencode({"token":token,"sig":sig})

# ---------- Madara ----------
def parse_madara_cards(html,base,source):
    soup=BeautifulSoup(html,"html.parser")
    selectors=[
      "div.c-tabs-item__content",".manga__item",
      "div.page-item-detail",".page-item-detail",
      ".row.c-tabs-item__content"
    ]
    out=[];seen=set()
    for sel in selectors:
        for el in soup.select(sel):
            a=el.select_one("div.post-title a,h3 a,h4 a,a[href]")
            img=el.select_one("img")
            if not a:continue
            title=(a.get_text(" ",strip=True) or a.get("title") or (img.get("alt") if img else "") or "").strip()
            url=urljoin(base,a.get("href",""))
            if len(title)<2 or not url or url in seen:continue
            seen.add(url)
            out.append({"title":title,"url":url,"thumbnail":urljoin(base,image_attr(img)),"source":source_dict(source),"adapter":"madara"})
        if out:break
    return out[:30]

async def madara_search(source,query):
    base=source_base(source)
    urls=[
      f"{base}/?{urlencode({'s':query,'post_type':'wp-manga'})}",
      f"{base}/?{urlencode({'s':query})}",
    ]
    for u in urls:
        try:
            html,final=await get_html(u,base,6)
            items=parse_madara_cards(html,final,source)
            if items:return items
        except Exception:
            pass
    # Madara AJAX load-more search.
    try:
        form={
          "action":"madara_load_more","page":"0",
          "template":"madara-core/content/content-search",
          "vars[paged]":"1","vars[template]":"archive","vars[sidebar]":"right",
          "vars[post_type]":"wp-manga","vars[post_status]":"publish",
          "vars[manga_archives_item_layout]":"big_thumbnail","vars[s]":query,
          "vars[meta_query][0][key]":"_wp_manga_chapter_type",
          "vars[meta_query][0][value]":"manga",
        }
        html,final=await post_form(base+"/wp-admin/admin-ajax.php",form,base,6)
        return parse_madara_cards(html,base,source)
    except Exception:
        return []

async def madara_popular(source):
    base=source_base(source)
    for u in (f"{base}/manga/?m_orderby=views",base):
        try:
            html,final=await get_html(u,base,6)
            items=parse_madara_cards(html,final,source)
            if items:return items
        except Exception:pass
    return []

def parse_madara_chapters(soup,base):
    out=[];seen=set()
    for a in soup.select("li.wp-manga-chapter a,.wp-manga-chapter a,.chapter-link-item a,.chapter-name a,.eph-num a,#chapterlist li a"):
        u=urljoin(base,a.get("href",""));name=text(a)
        if not u or not name or u in seen:continue
        seen.add(u);out.append({"name":name,"url":u,"number":chapter_number(name)})
    return out

async def madara_details(source,url):
    html,final=await get_html(url,source.homeUrl,7)
    soup=BeautifulSoup(html,"html.parser")
    title=text(soup.select_one("div.post-title h1,.post-title h1,h1")) or "Mangá"
    cover=urljoin(final,image_attr(soup.select_one(".summary_image img,.summary-image img,.manga-thumb img,.tab-summary img")))
    desc=text(soup.select_one(".summary__content,.description-summary,.manga-excerpt,.description,.manga-summary"))
    chapters=parse_madara_chapters(soup,final)

    if not chapters:
        holder=soup.select_one("div[id^='manga-chapters-holder']")
        manga_id=(holder.get("data-id") if holder else "") or ""
        if manga_id:
            # Old Madara endpoint, then new endpoint.
            try:
                body,_=await post_form(source_base(source)+"/wp-admin/admin-ajax.php",{"action":"manga_get_chapters","manga":manga_id},final,7)
                chapters=parse_madara_chapters(BeautifulSoup(body,"html.parser"),final)
            except Exception:
                pass
        if not chapters:
            try:
                body,_=await post_form(final.rstrip("/")+"/ajax/chapters",{},final,7)
                chapters=parse_madara_chapters(BeautifulSoup(body,"html.parser"),final)
            except Exception:
                pass

    chapters.sort(key=lambda x:(x["number"] is None,x["number"] if x["number"] is not None else 999999))
    return {"title":title,"cover":cover,"description":desc,"url":final,"chapters":chapters,"source":source_dict(source),"adapter":"madara"}

async def madara_pages(source,url,request):
    # Many Madara sites expose all images with style=list.
    target=url
    if "style=" not in target:
        target += ("&" if "?" in target else "?")+"style=list"
    html,final=await get_html(target,source.homeUrl,8)
    soup=BeautifulSoup(html,"html.parser")
    selectors=[
      "div.page-break img","li.blocks-gallery-item img",
      ".reading-content .text-left img",".reading-content img",
      ".reader-area img","#readerarea img",".readercontent img",
      ".chapter-content img",".container-chapter-reader img"
    ]
    pages=[];seen=set()
    for sel in selectors:
        for img in soup.select(sel):
            raw=image_attr(img);u=urljoin(final,raw)
            if not u or u in seen:continue
            low=u.lower()
            if any(x in low for x in ("logo","avatar","icon","banner","ads")):continue
            seen.add(u);pages.append({"image":proxied_image(request,u,final),"original":u})
        if pages:break
    return pages

# ---------- Saikai Scan exact API adapter ----------
def saikai_hosts(source):
    h=host(source.homeUrl)
    return f"https://api.{h}",f"https://s3-beta.{h}"

def saikai_story_item(story,source,storage):
    slug=str(story.get("slug") or "")
    title=str(story.get("title") or "Mangá")
    image=str(story.get("image") or "")
    return {
      "title":title,
      "url":source_base(source)+"/comics/"+slug,
      "thumbnail":storage.rstrip("/")+"/"+image.lstrip("/") if image else "",
      "source":source_dict(source),"adapter":"saikai","slug":slug
    }

async def saikai_json(url,source):
    headers={"Accept":"application/json, text/plain, */*","Origin":source.homeUrl,"Referer":source.homeUrl.rstrip("/")+"/"}
    r=await client.get(url,headers=headers,timeout=8)
    if r.status_code>=400:raise HTTPException(502,f"Saikai HTTP {r.status_code}")
    return r.json()

async def saikai_search(source,query):
    api,storage=saikai_hosts(source)
    params={"format":"2","q":query,"sortProperty":"pageViews","sortDirection":"desc","page":"1","per_page":"24","relationships":"language,type,format"}
    data=await saikai_json(api+"/api/stories?"+urlencode(params),source)
    return [saikai_story_item(x,source,storage) for x in (data.get("data") or [])]

async def saikai_popular(source):
    api,storage=saikai_hosts(source)
    params={"format":"2","sortProperty":"pageviews","sortDirection":"desc","page":"1","per_page":"24","relationships":"language,type,format"}
    data=await saikai_json(api+"/api/stories?"+urlencode(params),source)
    return [saikai_story_item(x,source,storage) for x in (data.get("data") or [])]

async def saikai_details(source,url):
    api,storage=saikai_hosts(source)
    slug=url.rstrip("/").split("/")[-1]
    params={"format":"2","slug":slug,"per_page":"1","relationships":"language,type,format,artists,status,releases"}
    data=await saikai_json(api+"/api/stories?"+urlencode(params),source)
    stories=data.get("data") or []
    if not stories:raise HTTPException(404,"Mangá não encontrado")
    s=stories[0]
    chapters=[]
    for r in s.get("releases") or []:
        if int(r.get("is_active",1) or 1)!=1:continue
        ch=str(r.get("chapter") or "")
        rid=r.get("id")
        rslug=str(r.get("slug") or "")
        name=f"Capítulo {ch}"+(f" - {r.get('title')}" if r.get("title") else "")
        chapters.append({"name":name,"number":float(ch) if re.fullmatch(r"\d+(?:\.\d+)?",ch) else chapter_number(name),"url":source_base(source)+f"/ler/comics/{slug}/{rid}/{rslug}","releaseId":rid})
    chapters.sort(key=lambda x:(x["number"] is None,x["number"] if x["number"] is not None else 999999))
    synopsis=BeautifulSoup(str(s.get("synopsis") or ""),"html.parser").get_text("\n",strip=True)
    image=str(s.get("image") or "")
    return {"title":s.get("title") or "Mangá","cover":storage.rstrip("/")+"/"+image.lstrip("/") if image else "","description":synopsis,"url":url,"chapters":chapters,"source":source_dict(source),"adapter":"saikai"}

async def saikai_pages(source,url,request):
    api,storage=saikai_hosts(source)
    parts=url.rstrip("/").split("/")
    release_id=parts[-2] if len(parts)>=2 else ""
    data=await saikai_json(api+f"/api/releases/{release_id}?relationships=releaseImages",source)
    release=data.get("data") or {}
    pages=[]
    for obj in release.get("release_images") or release.get("releaseImages") or []:
        image=str(obj.get("image") or "")
        if not image:continue
        u=storage.rstrip("/")+"/"+image.lstrip("/")
        pages.append({"image":proxied_image(request,u,source.homeUrl),"original":u})
    return pages

# ---------- Generic fallback ----------
GENERIC_CARD_SELECTORS=[
 ".bs .bsx",".listupd .bs",".manga__item",".page-item-detail",
 ".c-tabs-item__content",".manga-item","article"
]
def generic_cards(html,base,source):
    soup=BeautifulSoup(html,"html.parser");out=[];seen=set()
    for sel in GENERIC_CARD_SELECTORS:
        for el in soup.select(sel):
            a=el.select_one("a[href]");img=el.select_one("img")
            if not a:continue
            title=text(el.select_one("h3,h4,.post-title,.tt,.manga-name")) or (a.get("title") or "") or (img.get("alt") if img else "")
            title=str(title).strip();u=urljoin(base,a.get("href",""))
            if len(title)<2 or not u or u in seen:continue
            seen.add(u);out.append({"title":title,"url":u,"thumbnail":urljoin(base,image_attr(img)),"source":source_dict(source),"adapter":"generic"})
        if out:break
    return out[:30]

async def generic_search(source,query):
    base=source_base(source);q=urlencode({"s":query})
    for u in [f"{base}/?{q}",f"{base}/search?{urlencode({'q':query})}",f"{base}/buscar?{urlencode({'q':query})}"]:
        try:
            h,f=await get_html(u,base,6);items=generic_cards(h,f,source)
            if items:return items
        except Exception:pass
    return []

async def generic_details(source,url):
    html,final=await get_html(url,source.homeUrl,7);soup=BeautifulSoup(html,"html.parser")
    title=text(soup.select_one("h1,.post-title h1,.manga-title h1")) or "Mangá"
    cover=urljoin(final,image_attr(soup.select_one(".summary_image img,.manga-thumb img,.tab-summary img,.thumb img")))
    desc=text(soup.select_one(".summary__content,.description-summary,.description,.entry-content,.manga-summary"))
    chapters=[];seen=set()
    for a in soup.select(".wp-manga-chapter a,.chapter-link-item a,.chapter-name a,.eph-num a,#chapterlist li a,.eplister li a,a[href*='/capitulo'],a[href*='/chapter']"):
        u=urljoin(final,a.get("href",""));name=text(a)
        if not u or not name or u in seen:continue
        seen.add(u);chapters.append({"name":name,"url":u,"number":chapter_number(name)})
    chapters.sort(key=lambda x:(x["number"] is None,x["number"] if x["number"] is not None else 999999))
    return {"title":title,"cover":cover,"description":desc,"url":final,"chapters":chapters,"source":source_dict(source),"adapter":"generic"}

async def generic_pages(source,url,request):
    html,final=await get_html(url,source.homeUrl,8);soup=BeautifulSoup(html,"html.parser")
    pages=[];seen=set()
    for img in soup.select(".reading-content img,.page-break img,.reader-area img,#readerarea img,.readercontent img,.chapter-content img,.container-chapter-reader img"):
        u=urljoin(final,image_attr(img))
        if not u or u in seen:continue
        seen.add(u);pages.append({"image":proxied_image(request,u,final),"original":u})
    return pages

# ---------- routing ----------
async def search_source(source,query,popular=False):
    adapter=adapter_name(source)
    if adapter=="login-required":
        return {"source":source_dict(source),"items":[],"ok":False,"adapter":adapter,"error":"Essa fonte exige login no app original"}
    try:
        if adapter=="saikai":
            items=await (saikai_popular(source) if popular else saikai_search(source,query))
        elif adapter=="madara":
            items=await (madara_popular(source) if popular else madara_search(source,query))
        else:
            # Try Madara first because many Keiyoushi sources use this multisrc.
            items=await (madara_popular(source) if popular else madara_search(source,query))
            if not items:
                items=await generic_search(source,query)
        return {"source":source_dict(source),"items":items,"ok":bool(items),"adapter":adapter}
    except Exception as e:
        return {"source":source_dict(source),"items":[],"ok":False,"adapter":adapter,"error":str(e)}

@app.get("/api/health")
async def health():
    return {"ok":True,"name":"ResenhaFlix Manga Bridge v16","adapters":["madara","saikai","generic"]}

@app.post("/api/search")
async def search(body:SearchBody):
    r=await search_source(body.source,body.query,False)
    return {"items":r["items"],"ok":r["ok"],"adapter":r.get("adapter"),"error":r.get("error")}

@app.post("/api/popular")
async def popular(body:SearchBody):
    r=await search_source(body.source,body.query,True)
    return {"items":r["items"],"ok":r["ok"],"adapter":r.get("adapter"),"error":r.get("error")}

@app.post("/api/batch/search")
async def batch_search(body:BatchSearchBody):
    ordered=sorted(body.sources[:8],key=lambda s:(0 if s.lang.lower().startswith("pt") else 1,s.name.lower()))
    tasks=[asyncio.wait_for(search_source(s,body.query,False),timeout=7.0) for s in ordered]
    raw=await asyncio.gather(*tasks,return_exceptions=True)
    results=[]
    for i,x in enumerate(raw):
        if isinstance(x,Exception):
            results.append({"source":source_dict(ordered[i]),"items":[],"ok":False,"error":str(x)})
        else:results.append(x)
    return {"results":results}

@app.post("/api/manga")
async def manga(body:UrlBody):
    if not same_source(body.source,body.url):raise HTTPException(400,"URL fora da fonte")
    adapter=adapter_name(body.source)
    if adapter=="saikai":return await saikai_details(body.source,body.url)
    if adapter=="madara":return await madara_details(body.source,body.url)
    # auto: Madara parser is more complete; generic is fallback.
    try:
        d=await madara_details(body.source,body.url)
        if d.get("chapters"):return d
    except Exception:pass
    return await generic_details(body.source,body.url)

@app.post("/api/chapter")
async def chapter(body:UrlBody,request:Request):
    if not same_source(body.source,body.url):raise HTTPException(400,"URL fora da fonte")
    adapter=adapter_name(body.source)
    if adapter=="saikai":pages=await saikai_pages(body.source,body.url,request)
    elif adapter=="madara":pages=await madara_pages(body.source,body.url,request)
    else:
        pages=await madara_pages(body.source,body.url,request)
        if not pages:pages=await generic_pages(body.source,body.url,request)
    if not pages:raise HTTPException(422,"Nenhuma página encontrada")
    return {"pages":pages,"adapter":adapter}

@app.get("/api/image")
async def image(token:str,sig:str):
    expected=hmac.new(secret,token.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,sig):raise HTTPException(403,"Assinatura inválida")
    try:
        token+= "="*((4-len(token)%4)%4)
        data=json.loads(base64.urlsafe_b64decode(token))
    except Exception:raise HTTPException(400,"Token inválido")
    if int(data.get("e",0))<time.time():raise HTTPException(403,"Token expirado")
    url=data.get("u","");referer=data.get("r","")
    if not str(url).startswith(("http://","https://")):raise HTTPException(400,"URL inválida")
    headers={"Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"}
    if referer:headers["Referer"]=referer
    r=await client.get(url,headers=headers,timeout=10)
    if r.status_code>=400:raise HTTPException(502,f"Imagem HTTP {r.status_code}")
    return Response(r.content,media_type=r.headers.get("content-type","image/jpeg"),headers={"Cache-Control":"public,max-age=1800"})

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
