"""
Configuration Settings for Trading Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR = BASE_DIR / "storage"
    STRATEGIES_DIR = STORAGE_DIR / "strategies"
    LOGS_DIR = STORAGE_DIR / "logs"
    DATA_CACHE_DIR = STORAGE_DIR / "data"
    
    # Ensure directories exist
    for directory in [STORAGE_DIR, STRATEGIES_DIR, LOGS_DIR, DATA_CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Operating Mode
    MODE = os.getenv("MODE", "shadow")  # shadow, live, hybrid
    
    # Trading 212 API
    TRADING212_API_KEY = os.getenv("TRADING212_API_KEY", "")
    TRADING212_ENV = os.getenv("TRADING212_ENV", "demo")
    TRADING212_ACCOUNT_TYPE = os.getenv("TRADING212_ACCOUNT_TYPE", "INVEST")
    
    # API URLs based on environment
    @property
    def TRADING212_BASE_URL(self):
        if self.TRADING212_ENV == "live":
            return "https://api.trading212.com"
        return "https://demo-api.trading212.com"
    
    # Premium Data Providers
    EODHD_API_KEY = os.getenv("EODHD_API_KEY", "")
    FINHUB_API_KEY = os.getenv("FINHUB_API_KEY", "")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    # Dashboard Settings
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "5000"))
    DASHBOARD_DEBUG = os.getenv("DASHBOARD_DEBUG", "false").lower() == "true"
    
    # Learning Parameters
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.01"))
    BACKTEST_DAYS = int(os.getenv("BACKTEST_DAYS", "365"))
    SHADOW_TRADES_PER_DAY = int(os.getenv("SHADOW_TRADES_PER_DAY", "100"))
    OPTIMIZATION_INTERVAL_HOURS = int(os.getenv("OPTIMIZATION_INTERVAL_HOURS", "6"))
    
    # Risk Management
    MAX_POSITION_SIZE_PERCENT = float(os.getenv("MAX_POSITION_SIZE_PERCENT", "5.0"))
    STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "2.0"))
    TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "5.0"))
    MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "3.0"))
    MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "10"))
    RISK_PER_TRADE_PERCENT = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.0"))
    
    # Watchlist
    WATCHLIST = [
        symbol.strip() 
        for symbol in os.getenv(
            "WATCHLIST", 
            "AAPL,GOOGL,MSFT,TSLA,NVDA,AMZN,META,VOD,LLOY,BP,SHEL,HSBA,GSK,RIO"
        ).split(",")
    ]
    
    # Strategy Settings
    MIN_STRATEGY_PERFORMANCE = float(os.getenv("MIN_STRATEGY_PERFORMANCE", "0.0"))
    MAX_STRATEGIES_DEPLOYED = int(os.getenv("MAX_STRATEGIES_DEPLOYED", "20"))
    STRATEGY_GENERATION_COUNT = int(os.getenv("STRATEGY_GENERATION_COUNT", "10"))
    
    @property
    def is_shadow_mode(self):
        return self.MODE == "shadow"
    
    @property
    def is_live_mode(self):
        return self.MODE == "live"
    
    @property
    def is_hybrid_mode(self):
        return self.MODE == "hybrid"
    
    @property
    def has_trading212_key(self):
        return bool(self.TRADING212_API_KEY and self.TRADING212_API_KEY.strip())
    
    def validate(self):
        """Validate configuration settings."""
        errors = []
        
        if self.MODE not in ["shadow", "live", "hybrid"]:
            errors.append(f"Invalid MODE: {self.MODE}. Must be shadow, live, or hybrid.")
        
        if self.MODE in ["live", "hybrid"] and not self.has_trading212_key:
            errors.append("TRADING212_API_KEY required for live/hybrid mode.")
        
        if self.TRADING212_ENV not in ["demo", "live"]:
            errors.append(f"Invalid TRADING212_ENV: {self.TRADING212_ENV}. Must be demo or live.")
        
        if self.TRADING212_ACCOUNT_TYPE not in ["INVEST", "ISA"]:
            errors.append(f"Invalid TRADING212_ACCOUNT_TYPE: {self.TRADING212_ACCOUNT_TYPE}. Must be INVEST or ISA.")
        
        if self.MAX_POSITION_SIZE_PERCENT <= 0 or self.MAX_POSITION_SIZE_PERCENT > 100:
            errors.append("MAX_POSITION_SIZE_PERCENT must be between 0 and 100.")
        
        if self.STOP_LOSS_PERCENT <= 0 or self.STOP_LOSS_PERCENT > 50:
            errors.append("STOP_LOSS_PERCENT must be between 0 and 50.")
        
        if self.TAKE_PROFIT_PERCENT <= 0 or self.TAKE_PROFIT_PERCENT > 100:
            errors.append("TAKE_PROFIT_PERCENT must be between 0 and 100.")
        
        return errors


# Global settings instance
settings = Settings()
