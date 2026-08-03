"""
Main Orchestrator - Coordinates all components of the trading bot
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import threading
import time

from config.settings import settings
from data.providers import DataManager
from strategies.strategy_lab import StrategyLab
from execution.shadow_engine import ShadowEngine
from execution.trading212 import Trading212Manager
from dashboard.app import DashboardApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOGS_DIR / 'system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TradingBotOrchestrator:
    """
    Main orchestrator that coordinates all components:
    - Data collection
    - Strategy generation and optimization
    - Shadow trading
    - Live trading (when API key provided)
    - Dashboard
    """
    
    def __init__(self):
        self.settings = settings
        self.is_running = False
        self.start_time = None
        
        # Validate settings
        errors = self.settings.validate()
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            raise ValueError(f"Invalid configuration: {errors}")
        
        logger.info(f"Initializing Trading Bot in {self.settings.MODE} mode")
        
        # Initialize components
        self.data_manager = DataManager(self.settings)
        self.strategy_lab = StrategyLab(self.settings)
        self.shadow_engine = ShadowEngine(self.settings, self.data_manager, self.strategy_lab)
        
        # Initialize Trading 212 manager (only if API key provided)
        self.trading212: Optional[Trading212Manager] = None
        if self.settings.has_trading212_key:
            self.trading212 = Trading212Manager(self.settings)
            logger.info("Trading 212 integration enabled")
        else:
            logger.info("Running in shadow-only mode (no Trading 212 API key)")
        
        # Initialize dashboard
        self.dashboard = DashboardApp(self.settings, orchestrator=self)
        
        # Data cache
        self.data_cache = {}
        
        # Scheduler state
        self.last_optimization = datetime.now()
        self.last_data_refresh = datetime.now()
        
        logger.info("Trading Bot Orchestrator initialized successfully")
    
    def start(self):
        """Start the trading bot."""
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        self.shadow_engine.start()
        
        logger.info("Trading Bot started")
        logger.info(f"Mode: {self.settings.MODE}")
        logger.info(f"Watchlist: {len(self.settings.WATCHLIST)} symbols")
        
        # Generate initial strategies if none exist
        existing_strategies = self.strategy_lab.load_strategies()
        if not existing_strategies:
            logger.info("No existing strategies found. Generating initial strategies...")
            new_strategies = self.strategy_lab.generate_strategies(10)
            logger.info(f"Generated {len(new_strategies)} initial strategies")
    
    def stop(self):
        """Stop the trading bot."""
        self.is_running = False
        self.shadow_engine.stop()
        logger.info("Trading Bot stopped")
    
    async def run_async(self):
        """Main async run loop."""
        self.start()
        
        try:
            while self.is_running:
                await self._run_cycle()
                await asyncio.sleep(60)  # Run cycle every minute
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    async def _run_cycle(self):
        """Run one cycle of the trading bot."""
        try:
            now = datetime.now()
            
            # Refresh market data
            if now - self.last_data_refresh > timedelta(minutes=5):
                await self._refresh_data()
                self.last_data_refresh = now
            
            # Execute shadow trades
            if self.settings.MODE in ['shadow', 'hybrid']:
                self._execute_shadow_trades()
            
            # Run optimization periodically
            if now - self.last_optimization > timedelta(hours=self.settings.OPTIMIZATION_INTERVAL_HOURS):
                self._run_optimization()
                self.last_optimization = now
            
            # Reset daily counters at midnight
            if now.hour == 0 and now.minute < 5:
                self.shadow_engine.reset_daily_counters()
        
        except Exception as e:
            logger.error(f"Error in run cycle: {str(e)}")
    
    async def _refresh_data(self):
        """Refresh market data for watchlist."""
        logger.info("Refreshing market data...")
        
        for symbol in self.settings.WATCHLIST:
            try:
                data = self.data_manager.get_price_data(symbol, period="1y")
                if data is not None:
                    self.data_cache[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        logger.info(f"Data refresh complete. Cached {len(self.data_cache)} symbols.")
    
    def _execute_shadow_trades(self):
        """Execute shadow trading logic."""
        if not self.data_cache:
            return
        
        # Get top strategies
        top_strategies = self.strategy_lab.get_best_strategies(top_n=5)
        
        if not top_strategies:
            return
        
        # Get current prices
        prices = self.data_manager.yahoo.get_multiple_prices(self.settings.WATCHLIST)
        
        # Execute signals from each strategy
        for strategy in top_strategies:
            self.shadow_engine.execute_strategy_signals(
                strategy=strategy,
                prices=prices,
                data_cache=self.data_cache
            )
    
    def _run_optimization(self):
        """Run strategy optimization."""
        logger.info("Running strategy optimization...")
        
        # Generate new strategies
        new_strategies = self.strategy_lab.generate_strategies()
        logger.info(f"Generated {len(new_strategies)} new strategies")
        
        # Backtest new strategies on cached data
        for strategy in new_strategies:
            if self.data_cache:
                # Use first symbol in cache for backtesting
                symbol = list(self.data_cache.keys())[0]
                data = self.data_cache[symbol]
                
                if data is not None and len(data) > 30:
                    metrics = self.strategy_lab.backtest_strategy(strategy, data)
                    
                    if 'error' not in metrics:
                        self.strategy_lab.save_strategy(strategy, metrics)
        
        # Optimize existing strategies
        self.strategy_lab.optimize_strategies()
        
        logger.info("Strategy optimization complete")
    
    def run_dashboard_only(self):
        """Run only the dashboard (for monitoring)."""
        logger.info("Starting dashboard only...")
        self.dashboard.run()
    
    def run_full(self):
        """Run full system with dashboard in separate thread."""
        self.start()
        
        # Start dashboard in separate thread
        dashboard_thread = threading.Thread(target=self.dashboard.run, daemon=True)
        dashboard_thread.start()
        
        # Run main loop
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            self.stop()


def main():
    """Main entry point."""
    print("=" * 60)
    print("🤖 AI-Powered Self-Learning Trading Bot")
    print("=" * 60)
    print(f"\nMode: {settings.MODE}")
    print(f"Dashboard: http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        orchestrator = TradingBotOrchestrator()
        orchestrator.run_full()
    except Exception as e:
        logger.error(f"Failed to start: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure to:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and configure if needed")
        print("3. For live mode, add your Trading 212 API key")


if __name__ == "__main__":
    main()
