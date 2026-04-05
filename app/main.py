from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import keywords, subscribe

app = FastAPI(title="TrendScout API", version="1.0.0")

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

@app.get("/")
def root():
    return {"message": "TrendScout API"}

@app.get("/health")
def health():
    return {"status": "ok"}
