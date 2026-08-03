"""
Core Orchestrator - Central coordination with clear authority separation
Ensures no duplicate authority or conflicts between components
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """
    Main orchestrator that coordinates all components with clear authority boundaries.
    
    Authority Boundaries:
    - Strategy Lab: ONLY creates/optimizes strategies (NO execution)
    - Execution Engine: ONLY executes trades (NO strategy creation)
    - Risk Manager: ONLY validates/approves trades (NO strategy or execution)
    - Data Manager: ONLY fetches/provides data (NO decisions)
    - Orchestrator: ONLY coordinates timing (NO direct trading logic)
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.is_running = False
        self.start_time = None
        
        # Initialize components with clear responsibilities
        from src.data.providers import DataManager
        from src.strategies.strategy_lab import StrategyLab
        from src.execution.shadow_engine import ShadowEngine
        from src.execution.trading212 import Trading212Manager
        from src.core.risk_manager import RiskManager
        
        # Data Layer - Authority: Fetch and cache market data only
        self.data_manager = DataManager(self.settings)
        
        # Strategy Lab - Authority: Create, backtest, optimize strategies only
        self.strategy_lab = StrategyLab(self.settings)
        
        # Risk Manager - Authority: Validate and approve/reject trades only
        self.risk_manager = RiskManager(self.settings)
        
        # Shadow Engine - Authority: Execute simulated trades only
        self.shadow_engine = ShadowEngine(
            settings=self.settings,
            data_manager=self.data_manager,
            strategy_lab=self.strategy_lab,
            risk_manager=self.risk_manager
        )
        
        # Trading 212 Manager - Authority: Execute live trades only
        self.trading212: Optional[Trading212Manager] = None
        if self.settings.has_trading212_key:
            self.trading212 = Trading212Manager(self.settings)
            logger.info("✓ Trading 212 integration enabled (Live/Hybrid mode)")
        else:
            logger.info("✓ Running in Shadow Mode (no Trading 212 API key)")
        
        # State tracking
        self.data_cache: Dict[str, any] = {}
        self.last_optimization = datetime.now()
        self.last_data_refresh = datetime.now()
        self.last_strategy_generation = datetime.now()
        
        # Performance tracking
        self.stats = {
            'cycles_run': 0,
            'shadow_trades_executed': 0,
            'live_trades_executed': 0,
            'strategies_generated': 0,
            'optimizations_run': 0,
            'errors': 0
        }
        
        logger.info("✓ Trading Orchestrator initialized with clear authority boundaries")
    
    async def run(self):
        """Main async run loop for continuous learning and trading."""
        self.start()
        
        try:
            while self.is_running:
                await self._run_cycle()
                await asyncio.sleep(60)  # Run cycle every minute
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.shutdown()
    
    def start(self):
        """Start the trading bot."""
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Start shadow engine (always runs, even without broker key)
        self.shadow_engine.start()
        
        # Generate initial strategies if none exist
        existing_strategies = self.strategy_lab.load_strategies()
        if not existing_strategies:
            logger.info("No existing strategies found. Generating initial batch...")
            new_strategies = self.strategy_lab.generate_strategies(15)
            self.stats['strategies_generated'] += len(new_strategies)
            
            # Backtest initial strategies
            self._backtest_new_strategies(new_strategies)
        
        logger.info(f"✓ Trading Bot started in {self.settings.MODE.upper()} mode")
        logger.info(f"✓ Watchlist: {len(self.settings.WATCHLIST)} symbols")
        logger.info(f"✓ Optimization interval: {self.settings.OPTIMIZATION_INTERVAL_HOURS} hours")
    
    async def shutdown(self):
        """Gracefully shutdown all components."""
        logger.info("Shutting down trading bot...")
        self.is_running = False
        
        # Stop shadow engine
        self.shadow_engine.stop()
        
        # Save final state
        self._save_state()
        
        logger.info(f"✓ Shutdown complete. Total cycles: {self.stats['cycles_run']}")
    
    async def _run_cycle(self):
        """Run one complete cycle of the trading bot."""
        try:
            now = datetime.now()
            self.stats['cycles_run'] += 1
            
            # 1. Refresh market data (Data Manager authority)
            if now - self.last_data_refresh > timedelta(minutes=5):
                await self._refresh_market_data()
                self.last_data_refresh = now
            
            # 2. Generate new strategies periodically (Strategy Lab authority)
            if now - self.last_strategy_generation > timedelta(hours=12):
                new_strategies = self.strategy_lab.generate_strategies(5)
                self.stats['strategies_generated'] += len(new_strategies)
                self._backtest_new_strategies(new_strategies)
                self.last_strategy_generation = now
            
            # 3. Execute shadow trades (Shadow Engine authority)
            if self.settings.MODE in ['shadow', 'hybrid']:
                executed = self._execute_shadow_trades()
                self.stats['shadow_trades_executed'] += executed
            
            # 4. Execute live trades if in live/hybrid mode (Trading212 authority)
            if self.settings.MODE in ['live', 'hybrid'] and self.trading212:
                executed = self._execute_live_trades()
                self.stats['live_trades_executed'] += executed
            
            # 5. Run optimization periodically (Strategy Lab authority)
            if now - self.last_optimization > timedelta(hours=self.settings.OPTIMIZATION_INTERVAL_HOURS):
                self._run_optimization()
                self.last_optimization = now
            
            # 6. Reset daily counters at midnight
            if now.hour == 0 and now.minute < 5:
                self.shadow_engine.reset_daily_counters()
                self._reset_daily_stats()
            
            # Log status every 10 cycles
            if self.stats['cycles_run'] % 10 == 0:
                self._log_status()
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error in run cycle: {str(e)}", exc_info=True)
    
    async def _refresh_market_data(self):
        """Refresh market data for all watched symbols."""
        logger.debug("Refreshing market data...")
        
        for symbol in self.settings.WATCHLIST:
            try:
                data = self.data_manager.get_price_data(symbol, period="1y")
                if data is not None and not data.empty:
                    self.data_cache[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        logger.info(f"✓ Data refresh complete. Cached {len(self.data_cache)} symbols.")
    
    def _execute_shadow_trades(self) -> int:
        """Execute shadow trading logic. Returns number of trades executed."""
        if not self.data_cache:
            return 0
        
        # Get top performing strategies
        top_strategies = self.strategy_lab.get_best_strategies(top_n=5)
        
        if not top_strategies:
            return 0
        
        # Get current prices
        prices = self.data_manager.yahoo.get_multiple_prices(self.settings.WATCHLIST)
        
        trades_executed = 0
        for strategy in top_strategies:
            result = self.shadow_engine.execute_strategy_signals(
                strategy=strategy,
                prices=prices,
                data_cache=self.data_cache
            )
            if result:
                trades_executed += 1
        
        return trades_executed
    
    def _execute_live_trades(self) -> int:
        """Execute live trading logic. Returns number of trades executed."""
        if not self.trading212 or not self.data_cache:
            return 0
        
        # Get top strategies approved for live trading
        top_strategies = self.strategy_lab.get_best_strategies(top_n=3)
        
        if not top_strategies:
            return 0
        
        # Get current prices and account info
        prices = self.data_manager.yahoo.get_multiple_prices(self.settings.WATCHLIST)
        
        trades_executed = 0
        for strategy in top_strategies:
            # Risk manager must approve before live execution
            if self.risk_manager.can_trade_live():
                result = self.trading212.execute_strategy_signals(
                    strategy=strategy,
                    prices=prices,
                    data_cache=self.data_cache
                )
                if result:
                    trades_executed += 1
        
        return trades_executed
    
    def _run_optimization(self):
        """Run strategy optimization cycle."""
        logger.info("Starting strategy optimization cycle...")
        
        # Optimize existing strategies
        optimized_count = self.strategy_lab.optimize_strategies()
        self.stats['optimizations_run'] += 1
        
        logger.info(f"✓ Optimization complete. Optimized {optimized_count} strategies")
    
    def _backtest_new_strategies(self, strategies: List):
        """Backtest newly generated strategies on cached data."""
        if not self.data_cache:
            return
        
        for strategy in strategies:
            # Use first available symbol for backtesting
            symbol = list(self.data_cache.keys())[0]
            data = self.data_cache[symbol]
            
            if data is not None and len(data) > 30:
                metrics = self.strategy_lab.backtest_strategy(strategy, data)
                
                if 'error' not in metrics:
                    self.strategy_lab.save_strategy(strategy, metrics)
    
    def _log_status(self):
        """Log current system status."""
        logger.info(
            f"Status | Cycles: {self.stats['cycles_run']} | "
            f"Shadow Trades: {self.stats['shadow_trades_executed']} | "
            f"Live Trades: {self.stats['live_trades_executed']} | "
            f"Strategies: {self.stats['strategies_generated']} | "
            f"Errors: {self.stats['errors']}"
        )
    
    def _reset_daily_stats(self):
        """Reset daily statistics."""
        self.stats['shadow_trades_executed'] = 0
        self.stats['live_trades_executed'] = 0
        logger.info("Daily counters reset")
    
    def _save_state(self):
        """Save current state to disk."""
        state_file = self.settings.STORAGE_DIR / 'orchestrator_state.json'
        state = {
            'last_update': datetime.now().isoformat(),
            'stats': self.stats,
            'mode': self.settings.MODE
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get current system status for dashboard."""
        return {
            'is_running': self.is_running,
            'mode': self.settings.MODE,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'stats': self.stats,
            'cached_symbols': len(self.data_cache),
            'strategies_count': len(self.strategy_lab.load_strategies()),
            'last_optimization': self.last_optimization.isoformat(),
            'last_data_refresh': self.last_data_refresh.isoformat()
        }
