"""Analytics Routes - Performance tracking and reporting"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard():
    """Main dashboard data"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
