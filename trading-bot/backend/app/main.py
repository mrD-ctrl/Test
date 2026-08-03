"""
Trading212 Smart Bot - Main Application Entry Point
FastAPI backend for trading bot operations
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from loguru import logger
import sys

from app.core.config import settings
from app.api.routes import auth, trading, portfolio, strategies, analytics, news
from app.db.database import init_db
from app.services.ml_engine import MLEngine
from app.services.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Trading212 Smart Bot...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize ML engine
    ml_engine = MLEngine()
    await ml_engine.load_model()
    logger.info("ML engine loaded")
    
    # Start data collection
    data_collector = DataCollector()
    await data_collector.start_background_tasks()
    logger.info("Data collector started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trading212 Smart Bot...")
    await data_collector.stop()
    ml_engine.save_model()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered trading bot for Trading212 UK (ISA and Invest accounts)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to get current authenticated user"""
    # TODO: Implement JWT token validation
    return {"user_id": "demo_user", "account_type": settings.TRADING212_ACCOUNT_TYPE}

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(trading.router, prefix=f"{settings.API_PREFIX}/trading", tags=["Trading"])
app.include_router(portfolio.router, prefix=f"{settings.API_PREFIX}/portfolio", tags=["Portfolio"])
app.include_router(strategies.router, prefix=f"{settings.API_PREFIX}/strategies", tags=["Strategies"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(news.router, prefix=f"{settings.API_PREFIX}/news", tags=["News & Sentiment"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Trading212 Smart Bot",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_engine": "loaded",
        "data_collector": "running"
    }

@app.get("/api/v1/license")
async def license_info():
    """License and purchase information"""
    return {
        "license_type": "One-Time Purchase",
        "tiers": [
            {
                "name": "Basic",
                "price_gbp": 99,
                "features": [
                    "Single account support",
                    "Yahoo Finance data only",
                    "Basic strategies",
                    "Manual execution mode",
                    "Community support"
                ]
            },
            {
                "name": "Pro",
                "price_gbp": 199,
                "features": [
                    "Unlimited accounts (ISA + Invest)",
                    "All free data sources",
                    "Advanced strategies + ML optimization",
                    "Auto-execution",
                    "Email support",
                    "Backtesting module"
                ]
            },
            {
                "name": "Enterprise",
                "price_gbp": 399,
                "features": [
                    "Everything in Pro",
                    "Premium API integrations (user provides keys)",
                    "Custom strategy development",
                    "Priority support",
                    "White-label options",
                    "Advanced analytics"
                ]
            }
        ],
        "disclaimer": "This software is for educational purposes. Trading involves risk. Not financial advice."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
