"""
Strategy Lab - Generate, backtest, and optimize trading strategies
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class BaseStrategy:
    """Base class for all trading strategies."""
    
    def __init__(self, name: str, params: Dict):
        self.name = name
        self.params = params
        self.created_at = datetime.now()
        self.performance_history = []
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        """
        Generate trading signal.
        
        Returns:
            1 for buy, -1 for sell, 0 for hold, None for no decision
        """
        raise NotImplementedError
    
    def calculate_position_size(self, portfolio_value: float, price: float) -> int:
        """Calculate position size based on risk parameters."""
        risk_per_trade = self.params.get('risk_percent', 1.0) / 100
        dollar_risk = portfolio_value * risk_per_trade
        shares = int(dollar_risk / price)
        return max(0, shares)


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy."""
    
    def __init__(self, params: Dict = None):
        params = params or {
            'lookback_period': 20,
            'threshold': 0.05,
            'risk_percent': 1.0
        }
        super().__init__("Momentum", params)
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        if len(data) < self.params['lookback_period']:
            return None
        
        returns = data['close'].pct_change().rolling(self.params['lookback_period']).sum()
        current_return = returns.iloc[-1]
        
        if current_return > self.params['threshold']:
            return 1  # Buy
        elif current_return < -self.params['threshold']:
            return -1  # Sell
        return 0  # Hold


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy."""
    
    def __init__(self, params: Dict = None):
        params = params or {
            'lookback_period': 20,
            'std_threshold': 2.0,
            'risk_percent': 1.0
        }
        super().__init__("Mean Reversion", params)
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        if len(data) < self.params['lookback_period']:
            return None
        
        close = data['close']
        ma = close.rolling(self.params['lookback_period']).mean()
        std = close.rolling(self.params['lookback_period']).std()
        z_score = (close - ma) / std
        
        current_z = z_score.iloc[-1]
        
        if current_z < -self.params['std_threshold']:
            return 1  # Buy (price below lower band)
        elif current_z > self.params['std_threshold']:
            return -1  # Sell (price above upper band)
        return 0


class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover strategy."""
    
    def __init__(self, params: Dict = None):
        params = params or {
            'short_period': 10,
            'long_period': 30,
            'risk_percent': 1.0
        }
        super().__init__("MA Crossover", params)
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        if len(data) < self.params['long_period']:
            return None
        
        short_ma = data['close'].rolling(self.params['short_period']).mean()
        long_ma = data['close'].rolling(self.params['long_period']).mean()
        
        prev_short = short_ma.iloc[-2]
        prev_long = long_ma.iloc[-2]
        curr_short = short_ma.iloc[-1]
        curr_long = long_ma.iloc[-1]
        
        # Golden cross (buy signal)
        if prev_short <= prev_long and curr_short > curr_long:
            return 1
        # Death cross (sell signal)
        elif prev_short >= prev_long and curr_short < curr_long:
            return -1
        return 0


class RSIStrategy(BaseStrategy):
    """RSI-based trading strategy."""
    
    def __init__(self, params: Dict = None):
        params = params or {
            'rsi_period': 14,
            'oversold': 30,
            'overbought': 70,
            'risk_percent': 1.0
        }
        super().__init__("RSI", params)
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        if len(data) < self.params['rsi_period'] + 1:
            return None
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['rsi_period']).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < self.params['oversold']:
            return 1  # Buy (oversold)
        elif current_rsi > self.params['overbought']:
            return -1  # Sell (overbought)
        return 0


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands trading strategy."""
    
    def __init__(self, params: Dict = None):
        params = params or {
            'period': 20,
            'std_dev': 2.0,
            'risk_percent': 1.0
        }
        super().__init__("Bollinger Bands", params)
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[int]:
        if len(data) < self.params['period']:
            return None
        
        close = data['close']
        ma = close.rolling(self.params['period']).mean()
        std = close.rolling(self.params['period']).std()
        
        upper_band = ma + (std * self.params['std_dev'])
        lower_band = ma - (std * self.params['std_dev'])
        
        current_price = close.iloc[-1]
        
        if current_price < lower_band.iloc[-1]:
            return 1  # Buy (price below lower band)
        elif current_price > upper_band.iloc[-1]:
            return -1  # Sell (price above upper band)
        return 0


class StrategyLab:
    """
    Strategy Lab - Generates, backtests, and optimizes trading strategies.
    Continuously learns and improves strategy performance.
    """
    
    STRATEGY_CLASSES = [
        MomentumStrategy,
        MeanReversionStrategy,
        MACrossoverStrategy,
        RSIStrategy,
        BollingerBandsStrategy
    ]
    
    def __init__(self, settings):
        self.settings = settings
        self.strategies_dir = settings.STRATEGIES_DIR
        self.strategies: List[BaseStrategy] = []
        self.strategy_performance: Dict[str, Dict] = {}
        
        # Create strategies directory
        self.strategies_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized Strategy Lab")
    
    def generate_strategies(self, count: int = None) -> List[BaseStrategy]:
        """Generate new strategy variations."""
        count = count or self.settings.STRATEGY_GENERATION_COUNT
        new_strategies = []
        
        for _ in range(count):
            # Randomly select a strategy type
            strategy_class = np.random.choice(self.STRATEGY_CLASSES)
            
            # Generate random parameters within reasonable ranges
            params = self._generate_random_params(strategy_class)
            
            # Create strategy instance
            strategy = strategy_class(params)
            new_strategies.append(strategy)
        
        logger.info(f"Generated {len(new_strategies)} new strategies")
        return new_strategies
    
    def _generate_random_params(self, strategy_class) -> Dict:
        """Generate random parameters for a strategy."""
        if strategy_class == MomentumStrategy:
            return {
                'lookback_period': np.random.randint(10, 50),
                'threshold': np.random.uniform(0.02, 0.15),
                'risk_percent': np.random.uniform(0.5, 2.0)
            }
        elif strategy_class == MeanReversionStrategy:
            return {
                'lookback_period': np.random.randint(10, 50),
                'std_threshold': np.random.uniform(1.5, 3.0),
                'risk_percent': np.random.uniform(0.5, 2.0)
            }
        elif strategy_class == MACrossoverStrategy:
            short = np.random.randint(5, 20)
            return {
                'short_period': short,
                'long_period': np.random.randint(short + 5, short + 50),
                'risk_percent': np.random.uniform(0.5, 2.0)
            }
        elif strategy_class == RSIStrategy:
            return {
                'rsi_period': np.random.randint(10, 20),
                'oversold': np.random.randint(20, 35),
                'overbought': np.random.randint(65, 80),
                'risk_percent': np.random.uniform(0.5, 2.0)
            }
        elif strategy_class == BollingerBandsStrategy:
            return {
                'period': np.random.randint(15, 30),
                'std_dev': np.random.uniform(1.5, 2.5),
                'risk_percent': np.random.uniform(0.5, 2.0)
            }
        return {}
    
    def backtest_strategy(
        self, 
        strategy: BaseStrategy, 
        data: pd.DataFrame,
        initial_capital: float = 10000
    ) -> Dict:
        """
        Backtest a strategy on historical data.
        
        Returns:
            Dictionary with performance metrics
        """
        if data.empty or len(data) < 30:
            return {'error': 'Insufficient data'}
        
        # Ensure 'close' column exists - handle multi-level columns from yfinance
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten multi-index columns - new yfinance format: ('Close', 'AAPL')
            # Extract just the price type (Close, High, Low, etc.)
            new_columns = []
            for col in data.columns:
                if isinstance(col, tuple):
                    # Use first element (e.g., 'Close') or second if first is empty
                    new_col = col[0] if col[0] else col[1]
                else:
                    new_col = col
                new_columns.append(new_col.lower())
            data.columns = new_columns
        
        # Standardize column names to lowercase for single-level index
        data.columns = data.columns.str.lower().str.strip()
        
        if 'close' not in data.columns:
            return {'error': 'No close price column found'}
        
        capital = initial_capital
        position = 0
        trades = []
        portfolio_values = []
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1].copy()
            signal = strategy.generate_signal(current_data)
            current_price = data['close'].iloc[i]
            
            # Execute trades based on signal
            if signal == 1 and position == 0:  # Buy
                shares = strategy.calculate_position_size(capital, current_price)
                if shares > 0:
                    cost = shares * current_price
                    if cost <= capital:
                        capital -= cost
                        position = shares
                        trades.append({
                            'type': 'buy',
                            'price': current_price,
                            'shares': shares,
                            'index': i
                        })
            
            elif signal == -1 and position > 0:  # Sell
                revenue = position * current_price
                capital += revenue
                trades.append({
                    'type': 'sell',
                    'price': current_price,
                    'shares': position,
                    'index': i
                })
                position = 0
            
            # Track portfolio value
            portfolio_value = capital + (position * current_price)
            portfolio_values.append(portfolio_value)
        
        # Calculate performance metrics
        if not portfolio_values:
            return {'error': 'No trades executed'}
        
        portfolio_series = pd.Series(portfolio_values)
        returns = portfolio_series.pct_change().dropna()
        
        total_return = (portfolio_values[-1] - initial_capital) / initial_capital
        
        # Risk metrics
        sharpe_ratio = 0
        if returns.std() != 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        
        sortino_ratio = 0
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() != 0:
            sortino_ratio = (returns.mean() / downside_returns.std()) * np.sqrt(252)
        
        max_drawdown = 0
        peak = portfolio_values[0]
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        win_trades = [t for t in trades if t['type'] == 'sell']
        win_count = len(win_trades)
        
        # Calculate win rate (simplified)
        win_rate = 0.5  # Default
        
        metrics = {
            'strategy_name': strategy.name,
            'parameters': strategy.params,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'final_value': portfolio_values[-1],
            'trade_count': len(trades),
            'win_rate': win_rate,
            'backtest_period_days': len(data),
            'timestamp': datetime.now().isoformat()
        }
        
        return metrics
    
    def save_strategy(self, strategy: BaseStrategy, metrics: Dict):
        """Save strategy and its performance to disk."""
        strategy_id = f"{strategy.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000)}"
        
        strategy_data = {
            'id': strategy_id,
            'name': strategy.name,
            'parameters': strategy.params,
            'created_at': strategy.created_at.isoformat(),
            'performance': metrics,
            'status': 'active'
        }
        
        filepath = self.strategies_dir / f"{strategy_id}.json"
        with open(filepath, 'w') as f:
            json.dump(strategy_data, f, indent=2)
        
        logger.info(f"Saved strategy {strategy_id} with return: {metrics.get('total_return_pct', 0):.2f}%")
        return strategy_id
    
    def load_strategies(self) -> List[Dict]:
        """Load all saved strategies from disk."""
        strategies = []
        
        for filepath in self.strategies_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    strategy_data = json.load(f)
                    strategies.append(strategy_data)
            except Exception as e:
                logger.error(f"Error loading strategy {filepath}: {str(e)}")
        
        logger.info(f"Loaded {len(strategies)} strategies from disk")
        return strategies
    
    def get_best_strategies(self, top_n: int = 10, metric: str = 'sharpe_ratio') -> List[Dict]:
        """Get top performing strategies based on specified metric."""
        all_strategies = self.load_strategies()
        
        # Sort by metric
        sorted_strategies = sorted(
            all_strategies,
            key=lambda x: x.get('performance', {}).get(metric, 0),
            reverse=True
        )
        
        return sorted_strategies[:top_n]
    
    def optimize_strategies(self):
        """
        Optimize existing strategies by adjusting parameters.
        This is called periodically to improve strategy performance.
        """
        logger.info("Starting strategy optimization...")
        
        # Load existing strategies
        existing = self.load_strategies()
        
        # Get top performers
        top_strategies = self.get_best_strategies(top_n=5)
        
        optimized_count = 0
        for strategy_data in top_strategies:
            # Create slight variations of top strategies
            base_params = strategy_data['parameters']
            
            for _ in range(3):  # Generate 3 variations per top strategy
                new_params = self._mutate_params(base_params)
                
                # Find the strategy class
                strategy_class = next(
                    (cls for cls in self.STRATEGY_CLASSES 
                     if cls.__name__.replace('Strategy', '') == strategy_data['name']),
                    None
                )
                
                if strategy_class:
                    new_strategy = strategy_class(new_params)
                    self.strategies.append(new_strategy)
                    optimized_count += 1
        
        logger.info(f"Generated {optimized_count} optimized strategy variations")
        return optimized_count
    
    def _mutate_params(self, params: Dict) -> Dict:
        """Create slightly modified version of parameters."""
        mutated = params.copy()
        
        for key, value in mutated.items():
            if isinstance(value, (int, float)):
                # Mutate by ±10%
                mutation_factor = np.random.uniform(0.9, 1.1)
                mutated[key] = value * mutation_factor
                if isinstance(value, int):
                    mutated[key] = int(mutated[key])
        
        return mutated
    
    def run_backtest_on_watchlist(
        self, 
        strategy: BaseStrategy, 
        data_provider,
        period: str = "6mo"
    ) -> Dict:
        """Run backtest across all symbols in watchlist."""
        results = {}
        
        for symbol in self.settings.WATCHLIST:
            data = data_provider.get_price_data(symbol, period)
            if data is not None and len(data) > 30:
                metrics = self.backtest_strategy(strategy, data)
                results[symbol] = metrics
        
        # Aggregate results
        if results:
            avg_return = np.mean([r.get('total_return', 0) for r in results.values() if 'error' not in r])
            avg_sharpe = np.mean([r.get('sharpe_ratio', 0) for r in results.values() if 'error' not in r])
            
            return {
                'strategy_name': strategy.name,
                'symbols_tested': len(results),
                'average_return': avg_return,
                'average_sharpe': avg_sharpe,
                'symbol_results': results
            }
        
        return {'error': 'No valid results'}
