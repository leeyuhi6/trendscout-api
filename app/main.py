import os
import urllib.request
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import keywords, subscribe

app = FastAPI(title="TrendScout API", version="2.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://www.trendscout.dev",
        "https://trendscout.dev",
        "https://trendscout-sepia.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(keywords.router)
app.include_router(subscribe.router)

@app.on_event("startup")
async def startup_event():
    """启动时检查数据文件，不存在则从 GitHub 下载"""
    from app.api.keywords import trends_service, DATA_PATH
    data_path = Path(DATA_PATH)
    
    if not data_path.exists() or data_path.stat().st_size < 10000:
        print(f"[STARTUP] Data file missing or too small, downloading...")
        data_path.parent.mkdir(parents=True, exist_ok=True)
        url = "https://raw.githubusercontent.com/leeyuhi6/trendscout-api/master/data/keywords.jsonl"
        try:
            urllib.request.urlretrieve(url, str(data_path))
            print(f"[STARTUP] Downloaded {data_path.stat().st_size} bytes")
            trends_service.load_data()
        except Exception as e:
            print(f"[STARTUP] Download failed: {e}")
    
    print(f"[STARTUP] Loaded {len(trends_service.keywords)} keywords")

@app.get("/")
def root():
    return {"message": "TrendScout API", "version": "2.2.0"}

@app.get("/health")
def health():
    from app.api.keywords import trends_service
    return {"status": "ok", "keywords": len(trends_service.keywords)}
