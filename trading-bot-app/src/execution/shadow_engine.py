"""
Shadow Trading Engine - Simulates trades without real money
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ShadowPortfolio:
    """Simulated portfolio for shadow trading."""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.portfolio_values: List[Dict] = [{
            'timestamp': datetime.now(),
            'value': initial_capital,
            'cash': initial_capital
        }]
    
    def get_current_value(self, prices: Dict[str, float]) -> float:
        """Calculate current portfolio value given current prices."""
        position_value = sum(
            pos['shares'] * prices.get(symbol, pos['avg_price'])
            for symbol, pos in self.positions.items()
        )
        return self.cash + position_value
    
    def buy(self, symbol: str, shares: int, price: float) -> bool:
        """Execute a buy order in shadow portfolio."""
        cost = shares * price
        
        if cost > self.cash:
            logger.warning(f"Insufficient cash for {symbol}: need {cost}, have {self.cash}")
            return False
        
        self.cash -= cost
        
        if symbol in self.positions:
            # Add to existing position
            pos = self.positions[symbol]
            total_shares = pos['shares'] + shares
            pos['avg_price'] = ((pos['shares'] * pos['avg_price']) + cost) / total_shares
            pos['shares'] = total_shares
        else:
            # New position
            self.positions[symbol] = {
                'shares': shares,
                'avg_price': price,
                'entry_date': datetime.now()
            }
        
        self.trade_history.append({
            'type': 'buy',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'cost': cost,
            'timestamp': datetime.now()
        })
        
        logger.info(f"Shadow BUY: {shares} {symbol} @ {price:.2f}")
        return True
    
    def sell(self, symbol: str, shares: int, price: float) -> bool:
        """Execute a sell order in shadow portfolio."""
        if symbol not in self.positions:
            logger.warning(f"No position in {symbol} to sell")
            return False
        
        pos = self.positions[symbol]
        if shares > pos['shares']:
            shares = pos['shares']  # Sell all if requested more than held
        
        revenue = shares * price
        self.cash += revenue
        
        pos['shares'] -= shares
        
        self.trade_history.append({
            'type': 'sell',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'revenue': revenue,
            'pnl': (price - pos['avg_price']) * shares,
            'timestamp': datetime.now()
        })
        
        # Remove position if fully sold
        if pos['shares'] <= 0:
            del self.positions[symbol]
        
        logger.info(f"Shadow SELL: {shares} {symbol} @ {price:.2f}")
        return True
    
    def get_performance(self, prices: Dict[str, float]) -> Dict:
        """Calculate portfolio performance metrics."""
        current_value = self.get_current_value(prices)
        total_return = (current_value - self.initial_capital) / self.initial_capital
        
        # Calculate P&L for each position
        position_pnl = {}
        for symbol, pos in self.positions.items():
            current_price = prices.get(symbol, pos['avg_price'])
            pnl = (current_price - pos['avg_price']) * pos['shares']
            pnl_percent = (current_price - pos['avg_price']) / pos['avg_price'] * 100
            position_pnl[symbol] = {
                'shares': pos['shares'],
                'avg_price': pos['avg_price'],
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
        
        return {
            'initial_capital': self.initial_capital,
            'current_value': current_value,
            'cash': self.cash,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'position_count': len(self.positions),
            'positions': position_pnl,
            'trade_count': len(self.trade_history),
            'timestamp': datetime.now().isoformat()
        }


class ShadowEngine:
    """
    Shadow trading engine that simulates trades.
    Runs parallel to live trading for validation and learning.
    """
    
    def __init__(self, settings, data_provider, strategy_lab):
        self.settings = settings
        self.data_provider = data_provider
        self.strategy_lab = strategy_lab
        self.portfolio = ShadowPortfolio(initial_capital=100000)  # Virtual $100k
        self.is_running = False
        self.trades_today = 0
        self.last_optimization = datetime.now()
        
        logger.info("Initialized Shadow Trading Engine")
    
    def start(self):
        """Start shadow trading."""
        self.is_running = True
        logger.info("Shadow trading started")
    
    def stop(self):
        """Stop shadow trading."""
        self.is_running = False
        logger.info("Shadow trading stopped")
    
    def execute_strategy_signals(
        self, 
        strategy: Dict, 
        prices: Dict[str, float],
        data_cache: Dict[str, pd.DataFrame]
    ):
        """Execute trading signals from a strategy in shadow mode."""
        if not self.is_running:
            return
        
        strategy_name = strategy.get('name', 'Unknown')
        params = strategy.get('parameters', {})
        
        for symbol in self.settings.WATCHLIST:
            if symbol not in data_cache:
                continue
            
            data = data_cache[symbol]
            if data is None or len(data) < 30:
                continue
            
            # Get signal from strategy
            # Note: In production, would reconstruct strategy object and call generate_signal
            # For now, simplified logic
            signal = self._generate_shadow_signal(data, params, strategy_name)
            
            if signal == 1:  # Buy signal
                self._execute_shadow_buy(symbol, prices.get(symbol, 0))
            
            elif signal == -1:  # Sell signal
                self._execute_shadow_sell(symbol, prices.get(symbol, 0))
    
    def _generate_shadow_signal(
        self, 
        data: pd.DataFrame, 
        params: Dict, 
        strategy_name: str
    ) -> int:
        """Generate trading signal based on strategy type."""
        try:
            if strategy_name == "Momentum":
                lookback = params.get('lookback_period', 20)
                threshold = params.get('threshold', 0.05)
                returns = data['close'].pct_change().rolling(lookback).sum().iloc[-1]
                
                if returns > threshold:
                    return 1
                elif returns < -threshold:
                    return -1
            
            elif strategy_name == "Mean Reversion":
                lookback = params.get('lookback_period', 20)
                std_threshold = params.get('std_threshold', 2.0)
                
                close = data['close']
                ma = close.rolling(lookback).mean()
                std = close.rolling(lookback).std()
                z_score = (close.iloc[-1] - ma.iloc[-1]) / std.iloc[-1]
                
                if z_score < -std_threshold:
                    return 1
                elif z_score > std_threshold:
                    return -1
            
            elif strategy_name == "RSI":
                rsi_period = params.get('rsi_period', 14)
                oversold = params.get('oversold', 30)
                overbought = params.get('overbought', 70)
                
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                if current_rsi < oversold:
                    return 1
                elif current_rsi > overbought:
                    return -1
            
            elif strategy_name == "MA Crossover":
                short_period = params.get('short_period', 10)
                long_period = params.get('long_period', 30)
                
                short_ma = data['close'].rolling(short_period).mean()
                long_ma = data['close'].rolling(long_period).mean()
                
                if short_ma.iloc[-2] <= long_ma.iloc[-2] and short_ma.iloc[-1] > long_ma.iloc[-1]:
                    return 1
                elif short_ma.iloc[-2] >= long_ma.iloc[-2] and short_ma.iloc[-1] < long_ma.iloc[-1]:
                    return -1
            
            elif strategy_name == "Bollinger Bands":
                period = params.get('period', 20)
                std_dev = params.get('std_dev', 2.0)
                
                close = data['close']
                ma = close.rolling(period).mean()
                std = close.rolling(period).std()
                upper = ma + (std * std_dev)
                lower = ma - (std * std_dev)
                
                if close.iloc[-1] < lower.iloc[-1]:
                    return 1
                elif close.iloc[-1] > upper.iloc[-1]:
                    return -1
            
        except Exception as e:
            logger.error(f"Error generating shadow signal: {str(e)}")
        
        return 0  # Hold
    
    def _execute_shadow_buy(self, symbol: str, price: float):
        """Execute a shadow buy order."""
        if price <= 0:
            return
        
        # Check if already have position
        if symbol in self.portfolio.positions:
            return  # Already long
        
        # Check daily trade limit
        if self.trades_today >= self.settings.SHADOW_TRADES_PER_DAY:
            return
        
        # Calculate position size
        risk_per_trade = self.settings.RISK_PER_TRADE_PERCENT / 100
        dollar_risk = self.portfolio.get_current_value({}) * risk_per_trade
        shares = int(dollar_risk / price)
        
        if shares <= 0:
            return
        
        # Execute buy
        self.portfolio.buy(symbol, shares, price)
        self.trades_today += 1
    
    def _execute_shadow_sell(self, symbol: str, price: float):
        """Execute a shadow sell order."""
        if price <= 0:
            return
        
        # Check if have position
        if symbol not in self.portfolio.positions:
            return
        
        # Sell all shares
        shares = self.portfolio.positions[symbol]['shares']
        self.portfolio.sell(symbol, shares, price)
    
    def get_performance(self) -> Dict:
        """Get current shadow portfolio performance."""
        # Get latest prices
        prices = {}
        for symbol in self.portfolio.positions.keys():
            price = self.data_provider.yahoo.get_current_price(symbol)
            if price:
                prices[symbol] = price
        
        return self.portfolio.get_performance(prices)
    
    def reset_daily_counters(self):
        """Reset daily counters."""
        self.trades_today = 0
        logger.info("Reset shadow trading daily counters")
