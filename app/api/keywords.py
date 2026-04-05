from fastapi import APIRouter, Query
from typing import Optional
from app.services.trends import TrendsDataService
import os

router = APIRouter(prefix="/api/keywords", tags=["keywords"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "keywords.jsonl")
trends_service = TrendsDataService(DATA_PATH)

@router.get("/search")
async def search_keywords(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """搜索关键词"""
    all_results = trends_service.search(q, limit=1000)
    return {
        "query": q,
        "results": all_results[:limit],
        "total": len(all_results)
    }

@router.get("/trending")
async def get_trending(limit: int = Query(20, ge=1, le=100)):
    """获取热门趋势"""
    all_trends = trends_service.get_trending(limit=1000)
    return {
        "trends": all_trends[:limit],
        "total": len(all_trends)
    }

@router.get("/rising")
async def get_rising(limit: int = Query(20, ge=1, le=100)):
    """获取上升趋势词"""
    all_rising = trends_service.get_rising(limit=1000)
    return {
        "trends": all_rising[:limit],
        "total": len(all_rising)
    }
