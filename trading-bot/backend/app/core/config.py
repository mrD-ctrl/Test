"""
Trading212 Smart Bot - Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Trading212 Smart Bot"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "change-me-in-production"
    API_PREFIX: str = "/api/v1"
    
    # Broker Settings
    TRADING212_API_KEY: str = ""
    TRADING212_ACCOUNT_TYPE: str = "isa"  # 'isa' or 'invest'
    TRADING212_PIN: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://trading_bot:password@localhost:5432/trading_bot_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    ENCRYPTION_KEY: str = "32_byte_encryption_key_here!!!"
    JWT_EXPIRE_MINUTES: int = 1440
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # ML & Self-Learning
    MODEL_PATH: str = "./models/latest_model.pkl"
    MODEL_BACKUP_PATH: str = "./models/backups/"
    RETRAIN_INTERVAL_HOURS: int = 24
    MIN_TRADES_FOR_RETRAIN: int = 50
    LEARNING_RATE: float = 0.001
    EXPLORATION_RATE: float = 0.1
    DISCOUNT_FACTOR: float = 0.99
    
    # Risk Management
    MAX_POSITION_SIZE_PERCENT: float = 5.0
    MAX_DAILY_LOSS_PERCENT: float = 3.0
    MAX_PORTFOLIO_RISK_PERCENT: float = 15.0
    STOP_LOSS_PERCENT: float = 2.0
    TAKE_PROFIT_PERCENT: float = 5.0
    MAX_OPEN_POSITIONS: int = 10
    MIN_LIQUIDITY_USD: float = 100000
    
    # Data Sources - Free
    YAHOO_FINANCE_ENABLED: bool = True
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    GOOGLE_NEWS_ENABLED: bool = True
    
    # Data Sources - Premium (Optional)
    EODHD_API_KEY: Optional[str] = None
    EODHD_ENABLED: bool = False
    FINNHUB_API_KEY: Optional[str] = None
    FINNHUB_ENABLED: bool = False
    POLYGON_API_KEY: Optional[str] = None
    POLYGON_ENABLED: bool = False
    
    # News & Sentiment
    NEWS_UPDATE_INTERVAL_MINUTES: int = 15
    SENTIMENT_THRESHOLD: float = 0.3
    NEWS_SOURCES: str = "yahoo,google,reddit_wallsbets"
    ENABLE_NLP_SENTIMENT: bool = True
    
    # Trading Strategy
    DEFAULT_STRATEGY: str = "momentum"
    STRATEGY_PARAMETERS: dict = {"lookback_period": 20, "rsi_oversold": 30, "rsi_overbought": 70}
    BACKTEST_START_DATE: str = "2020-01-01"
    BACKTEST_END_DATE: str = "2024-01-01"
    INITIAL_CAPITAL: float = 10000
    
    # Execution
    EXECUTION_MODE: str = "paper"  # 'paper' or 'live'
    PAPER_TRADING_INITIAL_BALANCE: float = 10000
    ORDER_TYPE: str = "market"
    SLIPPAGE_TOLERANCE_PERCENT: float = 0.5
    MAX_ORDER_VALUE_GBP: float = 50000
    
    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/trading_bot.log"
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    
    # Notifications
    EMAIL_NOTIFICATIONS_ENABLED: bool = False
    EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # ISA Specific (UK)
    ISA_ANNUAL_LIMIT: float = 20000
    TRACK_ISA_CONTRIBUTIONS: bool = True
    TAX_YEAR_START_DATE: str = "04-06"
    CAPITAL_GAINS_TRACKING: bool = True
    
    # Backup & Recovery
    AUTO_BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 6
    BACKUP_RETENTION_DAYS: int = 30
    DATA_EXPORT_FORMAT: str = "csv,json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
