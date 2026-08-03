"""
Comprehensive Test Suite for Trading Bot App
Run: python -m pytest tests/test_all.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from config.settings import settings
from data.providers import DataManager, YahooFinanceProvider
from strategies.strategy_lab import StrategyLab, MomentumStrategy, RSIStrategy
from execution.shadow_engine import ShadowEngine, ShadowPortfolio
from dashboard.app import DashboardApp


class TestSettings:
    """Test configuration settings."""
    
    def test_settings_initialized(self):
        """Test that settings are properly initialized."""
        assert settings.MODE in ['shadow', 'live', 'hybrid']
        assert len(settings.WATCHLIST) > 0
        assert settings.INITIAL_CAPITAL > 0
    
    def test_shadow_mode_default(self):
        """Test default mode is shadow (safe)."""
        assert settings.MODE == 'shadow'
    
    def test_watchlist_valid(self):
        """Test watchlist contains valid symbols."""
        assert 'AAPL' in settings.WATCHLIST
        assert 'GOOGL' in settings.WATCHLIST


class TestDataProviders:
    """Test data provider components."""
    
    def test_yahoo_provider_initialized(self):
        """Test Yahoo Finance provider initialization."""
        provider = YahooFinanceProvider()
        assert provider.name == "Yahoo Finance"
    
    def test_data_manager_initialized(self):
        """Test DataManager initialization."""
        dm = DataManager(settings)
        assert dm.yahoo is not None
    
    def test_fetch_historical_data(self):
        """Test fetching historical data from Yahoo Finance."""
        dm = DataManager(settings)
        data = dm.get_price_data('AAPL', period='1mo')
        
        assert data is not None
        assert len(data) > 0
        assert 'close' in data.columns or 'Close' in data.columns
    
    def test_fetch_current_prices(self):
        """Test fetching current prices for multiple symbols."""
        dm = DataManager(settings)
        prices = dm.yahoo.get_multiple_prices(['AAPL', 'GOOGL', 'MSFT'])
        
        assert len(prices) > 0
        assert 'AAPL' in prices
        assert prices['AAPL'] > 0


class TestStrategyLab:
    """Test strategy generation and backtesting."""
    
    def test_strategy_lab_initialized(self):
        """Test StrategyLab initialization."""
        sl = StrategyLab(settings)
        assert sl.strategies_dir.exists()
    
    def test_generate_strategies(self):
        """Test strategy generation."""
        sl = StrategyLab(settings)
        strategies = sl.generate_strategies(5)
        
        assert len(strategies) == 5
        for strategy in strategies:
            assert hasattr(strategy, 'name')
            assert hasattr(strategy, 'params')
    
    def test_backtest_strategy(self):
        """Test strategy backtesting."""
        sl = StrategyLab(settings)
        
        # Create test data
        dates = pd.date_range('2024-01-01', periods=60, freq='D')
        prices = 100 + np.cumsum(np.random.randn(60) * 0.5)
        data = pd.DataFrame({'close': prices}, index=dates)
        
        # Generate and backtest strategy
        strategies = sl.generate_strategies(1)
        metrics = sl.backtest_strategy(strategies[0], data)
        
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'error' not in metrics or metrics.get('trade_count', 0) >= 0
    
    def test_save_and_load_strategies(self):
        """Test saving and loading strategies."""
        sl = StrategyLab(settings)
        
        # Generate and save a strategy
        strategies = sl.generate_strategies(1)
        test_data = pd.DataFrame({'close': [100, 101, 102, 103, 104]})
        metrics = sl.backtest_strategy(strategies[0], test_data)
        strategy_id = sl.save_strategy(strategies[0], metrics)
        
        # Load strategies
        loaded = sl.load_strategies()
        assert len(loaded) > 0
        
        # Verify saved strategy exists
        ids = [s['id'] for s in loaded]
        assert strategy_id in ids


class TestShadowEngine:
    """Test shadow trading engine."""
    
    def test_shadow_portfolio_initialized(self):
        """Test ShadowPortfolio initialization."""
        portfolio = ShadowPortfolio(initial_capital=10000)
        assert portfolio.initial_capital == 10000
        assert portfolio.cash == 10000
        assert len(portfolio.positions) == 0
    
    def test_shadow_buy_order(self):
        """Test buy order in shadow portfolio."""
        portfolio = ShadowPortfolio(initial_capital=10000)
        
        success = portfolio.buy('AAPL', 10, 150.0)
        assert success is True
        assert 'AAPL' in portfolio.positions
        assert portfolio.positions['AAPL']['shares'] == 10
        assert portfolio.cash == 8500
    
    def test_shadow_sell_order(self):
        """Test sell order in shadow portfolio."""
        portfolio = ShadowPortfolio(initial_capital=10000)
        
        # Buy first
        portfolio.buy('AAPL', 10, 150.0)
        
        # Then sell
        success = portfolio.sell('AAPL', 5, 160.0)
        assert success is True
        assert portfolio.positions['AAPL']['shares'] == 5
        assert portfolio.cash == 9300  # 8500 + 800
    
    def test_shadow_engine_initialized(self):
        """Test ShadowEngine initialization."""
        dm = DataManager(settings)
        sl = StrategyLab(settings)
        se = ShadowEngine(settings, dm, sl)
        
        assert se.portfolio.initial_capital == 100000
        assert se.is_running is False
    
    def test_shadow_start_stop(self):
        """Test starting and stopping shadow engine."""
        dm = DataManager(settings)
        sl = StrategyLab(settings)
        se = ShadowEngine(settings, dm, sl)
        
        se.start()
        assert se.is_running is True
        
        se.stop()
        assert se.is_running is False


class TestDashboard:
    """Test dashboard application."""
    
    def test_dashboard_initialized(self):
        """Test DashboardApp initialization."""
        da = DashboardApp(settings)
        assert da is not None
    
    def test_dashboard_routes(self):
        """Test dashboard has required routes."""
        da = DashboardApp(settings)
        
        # Check Flask app has routes
        rules = [rule.rule for rule in da.app.url_map.iter_rules()]
        assert '/' in rules
        assert '/api/status' in rules
        assert '/api/strategies' in rules


class TestIntegration:
    """Integration tests for full system."""
    
    def test_full_workflow(self):
        """Test complete workflow: data -> strategy -> shadow trade."""
        # Initialize all components
        dm = DataManager(settings)
        sl = StrategyLab(settings)
        se = ShadowEngine(settings, dm, sl)
        
        # Fetch data
        data = dm.get_price_data('AAPL', period='1mo')
        assert data is not None
        
        # Generate strategies
        strategies = sl.generate_strategies(3)
        assert len(strategies) == 3
        
        # Backtest best strategy
        metrics = sl.backtest_strategy(strategies[0], data)
        assert 'total_return' in metrics
        
        # Start shadow trading
        se.start()
        assert se.is_running is True
        
        # Execute a test trade
        prices = {'AAPL': 150.0}
        se.portfolio.buy('AAPL', 10, 150.0)
        assert 'AAPL' in se.portfolio.positions
        
        # Get performance
        perf = se.portfolio.get_performance(prices)
        assert 'current_value' in perf
        assert perf['position_count'] == 1
        
        se.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
