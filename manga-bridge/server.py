import os, re, asyncio
from urllib.parse import urljoin, urlencode, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

app=FastAPI(title="ResenhaFlix Manga Bridge v15")
origin=os.getenv("ALLOWED_ORIGIN","*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origin=="*" else [origin],
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

UA=os.getenv("MANGA_USER_AGENT","Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/131 Mobile Safari/537.36")
client=httpx.AsyncClient(
    follow_redirects=True,
    timeout=httpx.Timeout(8.0,connect=5.0),
    headers={"User-Agent":UA,"Accept-Language":"pt-BR,pt;q=0.9,en;q=0.6"},
)

class Source(BaseModel):
    id:str=""
    name:str="Fonte"
    lang:str="all"
    homeUrl:str
    extension:str=""

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

def same_source(source,url):
    a=host(source.homeUrl);b=host(url)
    return bool(a and b and (a==b or b.endswith("."+a)))

async def fetch_html(url,referer=None,timeout=7):
    headers={"Accept":"text/html,application/xhtml+xml"}
    if referer:headers["Referer"]=referer
    r=await client.get(url,headers=headers,timeout=timeout)
    if r.status_code>=400:raise HTTPException(502,f"Fonte HTTP {r.status_code}")
    return r.text,str(r.url)

def txt(el):
    return " ".join(el.stripped_strings).strip() if el else ""

def img_url(img):
    if not img:return ""
    for k in ("data-src","data-lazy-src","data-original","src"):
        x=(img.get(k) or "").strip()
        if x and not x.startswith("data:"):return x
    return ""

def chapter_number(name):
    s=(name or "").replace(",",".")
    m=re.search(r"(?:cap(?:ítulo|itulo|\.)?|chapter|ch\.?)\s*#?\s*(\d+(?:\.\d+)?)",s,re.I)
    if not m:m=re.search(r"(\d+(?:\.\d+)?)",s)
    return float(m.group(1)) if m else None

def parse_cards(html,base,source):
    soup=BeautifulSoup(html,"html.parser")
    selectors=[
        ".c-tabs-item__content",".page-item-detail",".row.c-tabs-item__content",
        ".bs .bsx",".listupd .bs",".manga__item",".manga-item",
        ".page-listing-item",".row.item-summary"
    ]
    out=[];seen=set()
    for sel in selectors:
        for el in soup.select(sel):
            a=el.select_one("a[href]");im=el.select_one("img")
            if not a:continue
            title=txt(el.select_one("h3,h4,.post-title,.tab-summary,.tt,.manga-name")) or (a.get("title") or "").strip() or (im.get("alt","").strip() if im else "")
            url=urljoin(base,a.get("href",""))
            if len(title)<2 or not url or url in seen:continue
            seen.add(url)
            out.append({
                "title":title,"url":url,
                "thumbnail":urljoin(base,img_url(im)),
                "source":source.model_dump()
            })
        if len(out)>=24:break
    return out[:24]

def search_urls(base,q):
    b=base.rstrip("/")
    return [
        f"{b}/?{urlencode({'s':q,'post_type':'wp-manga'})}",
        f"{b}/?{urlencode({'s':q})}",
        f"{b}/search?{urlencode({'q':q})}",
        f"{b}/buscar?{urlencode({'q':q})}",
        f"{b}/busca?{urlencode({'q':q})}",
    ]

async def search_source(source,query):
    last=None
    for url in search_urls(source.homeUrl,query):
        try:
            html,final=await fetch_html(url,source.homeUrl,6)
            items=parse_cards(html,final,source)
            if items:return {"source":source.model_dump(),"items":items,"ok":True}
        except Exception as e:last=e
    return {"source":source.model_dump(),"items":[],"ok":False,"error":str(last or "sem resultados")}

@app.get("/api/health")
async def health():
    return {"ok":True,"name":"ResenhaFlix Manga Bridge v15"}

@app.post("/api/search")
async def search(body:SearchBody):
    r=await search_source(body.source,body.query)
    return {"items":r["items"],"ok":r["ok"]}

@app.post("/api/batch/search")
async def batch_search(body:BatchSearchBody):
    ordered=sorted(body.sources[:8],key=lambda s:(0 if s.lang.lower().startswith("pt") else 1,s.name.lower()))
    tasks=[asyncio.wait_for(search_source(s,body.query),timeout=6.5) for s in ordered]
    raw=await asyncio.gather(*tasks,return_exceptions=True)
    results=[]
    for i,x in enumerate(raw):
        if isinstance(x,Exception):
            results.append({"source":ordered[i].model_dump(),"items":[],"ok":False,"error":str(x)})
        else:results.append(x)
    return {"results":results}

@app.post("/api/popular")
async def popular(body:SearchBody):
    html,final=await fetch_html(body.source.homeUrl,body.source.homeUrl,7)
    return {"items":parse_cards(html,final,body.source)}

@app.post("/api/manga")
async def manga(body:UrlBody):
    if not same_source(body.source,body.url):raise HTTPException(400,"URL fora da fonte")
    html,final=await fetch_html(body.url,body.source.homeUrl,7)
    soup=BeautifulSoup(html,"html.parser")
    title=txt(soup.select_one("h1,.post-title h1,.manga-title h1,.post-title")) or "Mangá"
    cover=urljoin(final,img_url(soup.select_one(".summary_image img,.manga-thumb img,.tab-summary img,.summary-image img")))
    desc=txt(soup.select_one(".summary__content,.description-summary,.manga-excerpt,.description,.manga-summary"))
    chapters=[];seen=set()
    for a in soup.select(".wp-manga-chapter a,.chapter-link-item a,.chapter-name a,.eph-num a,a[href*='/capitulo'],a[href*='/chapter']"):
        u=urljoin(final,a.get("href",""));name=txt(a)
        if not u or not name or u in seen or not same_source(body.source,u):continue
        seen.add(u);chapters.append({"name":name,"url":u,"number":chapter_number(name)})
    chapters.sort(key=lambda x:(x["number"] is None,x["number"] if x["number"] is not None else 999999))
    return {"title":title,"cover":cover,"description":desc,"url":final,"chapters":chapters,"source":body.source.model_dump()}

@app.post("/api/chapter")
async def chapter(body:UrlBody,request:Request):
    if not same_source(body.source,body.url):raise HTTPException(400,"URL fora da fonte")
    html,final=await fetch_html(body.url,body.source.homeUrl,8)
    soup=BeautifulSoup(html,"html.parser")
    pages=[];seen=set()
    for im in soup.select(".reading-content img,.page-break img,.reader-area img,.chapter-content img,.container-chapter-reader img"):
        u=urljoin(final,img_url(im))
        if not u or u in seen:continue
        seen.add(u)
        proxy=str(request.base_url).rstrip("/")+"/api/image?url="+httpx.QueryParams({"url":u,"referer":final})["url"] if False else None
        # Return original plus proxy fields. Frontend uses image.
        pages.append({"image":str(request.base_url).rstrip("/")+"/api/image?"+urlencode({"url":u,"referer":final}),"original":u})
    if not pages:raise HTTPException(422,"Nenhuma página encontrada")
    return {"pages":pages}

@app.get("/api/image")
async def image(url:str,referer:str=""):
    if not url.startswith(("http://","https://")):raise HTTPException(400,"URL inválida")
    headers={"Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"}
    if referer:headers["Referer"]=referer
    r=await client.get(url,headers=headers,timeout=10)
    if r.status_code>=400:raise HTTPException(502,f"Imagem HTTP {r.status_code}")
    return Response(r.content,media_type=r.headers.get("content-type","image/jpeg"),headers={"Cache-Control":"public,max-age=1800"})

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
