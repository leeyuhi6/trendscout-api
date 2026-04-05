from fastapi import APIRouter, Query
from typing import List, Optional
from app.services.trends import TrendsDataService
import os

router = APIRouter(prefix="/api/keywords", tags=["keywords"])

# 相对路径，兼容本地和 Railway 部署
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "keywords.jsonl")
trends_service = TrendsDataService(DATA_PATH)

@router.get("/search")
async def search_keywords(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """搜索关键词"""
    results = trends_service.search(q, limit)
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@router.get("/trending")
async def get_trending(limit: int = Query(20, ge=1, le=100)):
    """获取热门趋势"""
    trends = trends_service.get_trending(limit)
    return {
        "trends": trends,
        "total": len(trends)
    }

@router.get("/rising")
async def get_rising(limit: int = Query(20, ge=1, le=100)):
    """获取上升趋势词（growth_rate > 20%）"""
    rising = trends_service.get_rising(limit)
    return {
        "trends": rising,
        "total": len(rising)
    }
