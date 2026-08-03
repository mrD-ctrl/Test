"""
Data Providers - Fetch market data from various sources
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class YahooFinanceProvider:
    """Free data provider using Yahoo Finance API."""
    
    def __init__(self):
        self.name = "Yahoo Finance"
        logger.info("Initialized Yahoo Finance data provider")
    
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Ensure column names are lowercase
            df.columns = df.columns.str.lower()
            
            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current/latest price for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                return None
            
            # Handle lowercase column names from yfinance
            data.columns = data.columns.str.lower()
            return data['close'].iloc[-1]
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols."""
        prices = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
        return prices
    
    def get_ticker_info(self, symbol: str) -> Optional[Dict]:
        """Get basic information about a ticker."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            logger.error(f"Error getting info for {symbol}: {str(e)}")
            return None


class NewsProvider:
    """Fetch and analyze financial news."""
    
    def __init__(self):
        self.name = "News Provider"
        logger.info("Initialized News data provider")
    
    def get_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get recent news for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of news articles
        
        Returns:
            List of news articles with title, publisher, timestamp, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            news_items = ticker.news[:limit]
            
            formatted_news = []
            for item in news_items:
                formatted_news.append({
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'timestamp': item.get('providerPublishTime', 0),
                    'type': item.get('type', 'STORY')
                })
            
            logger.info(f"Fetched {len(formatted_news)} news items for {symbol}")
            return formatted_news
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        Analyze sentiment of news articles.
        Simple keyword-based sentiment analysis.
        
        Args:
            news_list: List of news articles
        
        Returns:
            Dictionary with sentiment scores
        """
        positive_words = [
            'growth', 'profit', 'gain', 'rise', 'increase', 'beat', 'outperform',
            'bullish', 'upgrade', 'positive', 'strong', 'record', 'success'
        ]
        negative_words = [
            'loss', 'decline', 'fall', 'drop', 'decrease', 'miss', 'underperform',
            'bearish', 'downgrade', 'negative', 'weak', 'crash', 'failure'
        ]
        
        total_score = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for news in news_list:
            title = news.get('title', '').lower()
            score = 0
            
            for word in positive_words:
                if word in title:
                    score += 1
                    positive_count += 1
            
            for word in negative_words:
                if word in title:
                    score -= 1
                    negative_count += 1
            
            if score > 0:
                total_score += 1
            elif score < 0:
                total_score -= 1
            else:
                neutral_count += 1
        
        total = len(news_list) if news_list else 1
        
        return {
            'overall_sentiment': 'positive' if total_score > 0 else 'negative' if total_score < 0 else 'neutral',
            'sentiment_score': total_score / total,
            'positive_ratio': positive_count / (positive_count + negative_count + neutral_count),
            'negative_ratio': negative_count / (positive_count + negative_count + neutral_count),
            'neutral_ratio': neutral_count / (positive_count + negative_count + neutral_count),
            'article_count': total
        }


class PremiumDataProvider:
    """Optional premium data providers (EODHD, FinHub, etc.)."""
    
    def __init__(self, api_key: str, provider: str = "eodhd"):
        self.api_key = api_key
        self.provider = provider
        self.base_url = {
            'eodhd': 'https://eodhd.com/api',
            'finhub': 'https://finnhub.io/api/v1',
            'alpha_vantage': 'https://www.alphavantage.co/query'
        }.get(provider, '')
        
        logger.info(f"Initialized {provider} premium data provider")
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fetch data from premium provider."""
        import requests
        
        if not self.api_key:
            logger.warning(f"No API key for {self.provider}")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            params = params or {}
            params['api_token'] = self.api_key if self.provider == 'eodhd' else params.get('token', self.api_key)
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching from {self.provider}: {str(e)}")
            return None


class DataManager:
    """Unified data management interface."""
    
    def __init__(self, settings):
        self.settings = settings
        self.yahoo = YahooFinanceProvider()
        self.news = NewsProvider()
        self.premium_providers = []
        
        # Initialize premium providers if API keys available
        if settings.EODHD_API_KEY:
            self.premium_providers.append(PremiumDataProvider(settings.EODHD_API_KEY, 'eodhd'))
        
        if settings.FINHUB_API_KEY:
            self.premium_providers.append(PremiumDataProvider(settings.FINHUB_API_KEY, 'finhub'))
        
        logger.info("Initialized Data Manager")
    
    def get_price_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Get price data, trying premium providers first if available."""
        # Try premium providers first
        for provider in self.premium_providers:
            # Implementation would go here for premium data
            pass
        
        # Fall back to Yahoo Finance
        return self.yahoo.get_historical_data(symbol, period)
    
    def get_watchlist_data(self) -> Dict[str, Dict]:
        """Get current data for all symbols in watchlist."""
        results = {}
        
        for symbol in self.settings.WATCHLIST:
            try:
                price = self.yahoo.get_current_price(symbol)
                news = self.yahoo.get_news(symbol, limit=5)
                sentiment = self.news.analyze_sentiment(news) if news else {}
                
                results[symbol] = {
                    'price': price,
                    'news_count': len(news) if news else 0,
                    'sentiment': sentiment
                }
            except Exception as e:
                logger.error(f"Error getting data for {symbol}: {str(e)}")
        
        return results
