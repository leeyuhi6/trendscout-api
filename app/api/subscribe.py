from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import json
import os
from datetime import datetime
from pathlib import Path

router = APIRouter()

# 订阅者存储文件（简单 JSON，后续可迁移到数据库）
SUBSCRIBERS_FILE = Path("/app/data/subscribers.json")
SUBSCRIBERS_FILE.parent.mkdir(exist_ok=True)


class SubscribeRequest(BaseModel):
    email: str


def load_subscribers() -> list:
    if SUBSCRIBERS_FILE.exists():
        try:
            return json.loads(SUBSCRIBERS_FILE.read_text())
        except Exception:
            return []
    return []


def save_subscribers(subscribers: list):
    SUBSCRIBERS_FILE.write_text(json.dumps(subscribers, indent=2, ensure_ascii=False))


@router.post("/api/subscribe")
async def subscribe(req: SubscribeRequest):
    email = req.email.strip().lower()

    # 基础校验
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email address")

    subscribers = load_subscribers()

    # 去重
    existing_emails = [s["email"] for s in subscribers]
    if email in existing_emails:
        return {"success": True, "message": "You're already on the list!"}

    # 添加
    subscribers.append({
        "email": email,
        "subscribed_at": datetime.utcnow().isoformat(),
        "source": "homepage",
    })
    save_subscribers(subscribers)

    return {
        "success": True,
        "message": "Successfully subscribed!",
        "count": len(subscribers),
    }


@router.get("/api/subscribers/count")
async def subscriber_count():
    """公开接口：返回订阅人数（用于首页显示社交证明）"""
    subscribers = load_subscribers()
    return {"count": len(subscribers)}
