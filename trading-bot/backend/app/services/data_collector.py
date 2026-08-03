"""
Trading212 Smart Bot - Data Collector Service
Aggregates data from multiple sources: Yahoo Finance, Google News, and optional premium APIs
"""
import asyncio
import aiohttp
import yfinance as yf
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from loguru import logger
from bs4 import BeautifulSoup
import json

from app.core.config import settings


class DataCollector:
    """
    Multi-source data collector for trading bot.
    Supports:
    - Free: Yahoo Finance, Google News RSS
    - Premium (optional): EODHD, Finnhub, Polygon
    """
    
    def __init__(self):
        self.session = None
        self.running = False
        self.data_cache = {}
        self.news_cache = []
        
    async def start_background_tasks(self):
        """Start background data collection tasks"""
        self.running = True
        self.session = aiohttp.ClientSession()
        
        # Start background tasks
        asyncio.create_task(self._news_collection_loop())
        asyncio.create_task(self._price_data_refresh_loop())
        
        logger.info("Data collector background tasks started")
    
    async def stop(self):
        """Stop data collection"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Data collector stopped")
    
    async def _news_collection_loop(self):
        """Periodically collect news data"""
        while self.running:
            try:
                await self.collect_news()
                await asyncio.sleep(settings.NEWS_UPDATE_INTERVAL_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error in news collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _price_data_refresh_loop(self):
        """Periodically refresh price data for watched symbols"""
        while self.running:
            try:
                # Refresh cached price data
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in price data loop: {e}")
                await asyncio.sleep(60)
    
    async def get_stock_data(
        self, 
        symbol: str, 
        period: str = "1mo", 
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical stock data from Yahoo Finance
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            # Standardize column names
            df.columns = df.columns.str.lower()
            
            logger.debug(f"Retrieved {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    async def get_multiple_stocks(
        self, 
        symbols: List[str], 
        period: str = "1mo"
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple stocks concurrently"""
        tasks = [self.get_stock_data(symbol, period) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data_dict = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame):
                data_dict[symbol] = result
            else:
                logger.error(f"Failed to fetch data for {symbol}: {result}")
        
        return data_dict
    
    async def collect_news(self, query: str = "stock market") -> List[Dict]:
        """
        Collect news from multiple sources
        
        Args:
            query: Search query for news
        
        Returns:
            List of news articles with sentiment scores
        """
        news_articles = []
        
        # Google News RSS (Free)
        if settings.GOOGLE_NEWS_ENABLED:
            google_news = await self._fetch_google_news(query)
            news_articles.extend(google_news)
        
        # Yahoo Finance News (Free)
        if settings.YAHOO_FINANCE_ENABLED:
            yahoo_news = await self._fetch_yahoo_news(query)
            news_articles.extend(yahoo_news)
        
        # Finnhub News (Premium - optional)
        if settings.FINNHUB_ENABLED and settings.FINNHUB_API_KEY:
            finnhub_news = await self._fetch_finnhub_news(query)
            news_articles.extend(finnhub_news)
        
        # Calculate sentiment for each article
        for article in news_articles:
            article['sentiment_score'] = self._calculate_sentiment(article.get('content', ''))
        
        # Cache recent news
        self.news_cache = news_articles[-100:]  # Keep last 100 articles
        
        logger.info(f"Collected {len(news_articles)} news articles")
        return news_articles
    
    async def _fetch_google_news(self, query: str) -> List[Dict]:
        """Fetch news from Google News RSS"""
        articles = []
        try:
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-GB&gl=UK&ceid=GB:en"
            
            async with self.session.get(rss_url, timeout=10) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    feed = feedparser.parse(xml_content)
                    
                    for entry in feed.entries[:20]:  # Limit to 20 articles
                        articles.append({
                            'title': entry.title,
                            'source': 'Google News',
                            'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                            'link': entry.link,
                            'content': entry.get('description', ''),
                            'symbols_mentioned': self._extract_symbols(entry.title + ' ' + entry.get('description', ''))
                        })
        except Exception as e:
            logger.error(f"Error fetching Google News: {e}")
        
        return articles
    
    async def _fetch_yahoo_news(self, query: str) -> List[Dict]:
        """Fetch news from Yahoo Finance"""
        articles = []
        try:
            # Use Yahoo Finance search
            ticker = yf.Ticker(query.split()[0] if query else "AAPL")
            news = ticker.news
            
            for item in news[:15]:
                articles.append({
                    'title': item.get('title', ''),
                    'source': 'Yahoo Finance',
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat() if item.get('providerPublishTime') else datetime.now().isoformat(),
                    'link': item.get('link', ''),
                    'content': item.get('summary', ''),
                    'symbols_mentioned': self._extract_symbols(item.get('title', '') + ' ' + item.get('summary', ''))
                })
        except Exception as e:
            logger.error(f"Error fetching Yahoo News: {e}")
        
        return articles
    
    async def _fetch_finnhub_news(self, query: str) -> List[Dict]:
        """Fetch news from Finnhub (Premium API)"""
        articles = []
        if not settings.FINNHUB_API_KEY:
            return articles
        
        try:
            # Get current date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            url = "https://finnhub.io/api/v1/news"
            params = {
                'category': 'general',
                'token': settings.FINNHUB_API_KEY
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data[:20]:
                        articles.append({
                            'title': item.get('headline', ''),
                            'source': 'Finnhub',
                            'published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                            'link': item.get('url', ''),
                            'content': item.get('summary', ''),
                            'sentiment_score': item.get('sentiment', {}).get('score', 0) if item.get('sentiment') else 0
                        })
        except Exception as e:
            logger.error(f"Error fetching Finnhub news: {e}")
        
        return articles
    
    def _calculate_sentiment(self, text: str) -> float:
        """
        Calculate sentiment score for text
        Simple rule-based approach (can be enhanced with NLP models)
        
        Returns:
            Sentiment score between -1 (very negative) and 1 (very positive)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            'gain', 'growth', 'profit', 'surge', 'rally', 'beat', 'outperform',
            'upgrade', 'bullish', 'optimistic', 'record', 'high', 'strong'
        ]
        
        # Negative indicators
        negative_words = [
            'loss', 'decline', 'drop', 'fall', 'crash', 'miss', 'underperform',
            'downgrade', 'bearish', 'pessimistic', 'low', 'weak', 'warning'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        # Normalize to [-1, 1]
        score = (positive_count - negative_count) / total
        return round(score, 3)
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract stock symbols mentioned in text"""
        import re
        # Simple pattern to find potential stock symbols (uppercase letters)
        symbols = re.findall(r'\b[A-Z]{2,5}\b', text)
        
        # Filter common words that might match
        common_words = {'THE', 'AND', 'FOR', 'NOT', 'YOU', 'ALL', 'ARE', 'HAS', 'WAS'}
        symbols = [s for s in symbols if s not in common_words]
        
        return list(set(symbols))[:10]  # Limit to 10 symbols
    
    async def get_market_overview(self) -> Dict:
        """Get overall market overview including major indices"""
        indices = {
            'FTSE 100': '^FTSE',
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW JONES': '^DJI',
            'DAX': '^GDAXI',
            'NIKKEI': '^N225'
        }
        
        overview = {}
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                
                overview[name] = {
                    'symbol': symbol,
                    'current_price': float(info.lastPrice) if info.lastPrice else None,
                    'change_percent': None,  # Would need historical comparison
                    'currency': info.currency or 'GBP'
                }
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                overview[name] = {'error': str(e)}
        
        return overview
    
    async def get_economic_calendar(self) -> List[Dict]:
        """Get upcoming economic events (simplified version)"""
        # This would ideally connect to an economic calendar API
        # For now, return a placeholder structure
        events = [
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'event': 'Bank of England Interest Rate Decision',
                'importance': 'high',
                'actual': None,
                'forecast': '5.25%',
                'previous': '5.25%'
            },
            {
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'event': 'UK GDP Growth Rate',
                'importance': 'high',
                'actual': None,
                'forecast': '0.2%',
                'previous': '0.0%'
            }
        ]
        
        return events
    
    def get_cached_news(self, limit: int = 50) -> List[Dict]:
        """Get recently cached news articles"""
        return self.news_cache[-limit:]
    
    def get_news_by_symbol(self, symbol: str, limit: int = 20) -> List[Dict]:
        """Get news articles mentioning a specific symbol"""
        relevant_news = [
            article for article in self.news_cache
            if symbol in article.get('symbols_mentioned', [])
        ]
        return relevant_news[-limit:]


# Singleton instance
data_collector_instance = None

def get_data_collector() -> DataCollector:
    """Get or create data collector singleton"""
    global data_collector_instance
    if data_collector_instance is None:
        data_collector_instance = DataCollector()
    return data_collector_instance
