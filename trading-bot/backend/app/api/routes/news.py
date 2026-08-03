"""News & Sentiment Routes"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/latest")
async def get_latest_news():
    """Get latest news with sentiment"""
    return {"news": [], "timestamp": datetime.now().isoformat()}
