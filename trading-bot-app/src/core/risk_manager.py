"""
Risk Manager - Sole authority for trade validation and risk controls
No strategy creation, no execution - only approval/rejection of trades
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Risk Manager with exclusive authority for:
    - Validating trade requests
    - Enforcing position size limits
    - Tracking daily loss limits
    - Approving/rejecting live trades
    
    NO authority for:
    - Creating strategies
    - Executing trades
    - Fetching market data
    """
    
    def __init__(self, settings):
        self.settings = settings
        
        # Risk limits from settings
        self.max_position_size_pct = settings.MAX_POSITION_SIZE_PERCENT
        self.stop_loss_pct = settings.STOP_LOSS_PERCENT
        self.take_profit_pct = settings.TAKE_PROFIT_PERCENT
        self.max_daily_loss_pct = settings.MAX_DAILY_LOSS_PERCENT
        self.max_open_positions = settings.MAX_OPEN_POSITIONS
        self.risk_per_trade_pct = settings.RISK_PER_TRADE_PERCENT
        
        # Daily tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_losses = 0.0
        self.open_positions_count = 0
        
        # State file
        self.state_file = settings.STORAGE_DIR / 'risk_manager_state.json'
        self._load_state()
        
        logger.info("✓ Risk Manager initialized")
    
    def can_trade_live(self) -> bool:
        """
        Check if live trading is allowed based on risk constraints.
        Returns True only if all risk checks pass.
        """
        # Check daily loss limit
        if self._is_daily_loss_limit_reached():
            logger.warning("Daily loss limit reached. Live trading paused.")
            return False
        
        # Check max open positions
        if self.open_positions_count >= self.max_open_positions:
            logger.warning(f"Max open positions ({self.max_open_positions}) reached.")
            return False
        
        return True
    
    def validate_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        portfolio_value: float
    ) -> Dict:
        """
        Validate a trade request against all risk rules.
        
        Returns:
            Dict with 'approved' boolean and 'reason' string
        """
        # Calculate position value
        position_value = quantity * price
        position_size_pct = (position_value / portfolio_value) * 100
        
        # Rule 1: Position size limit
        if position_size_pct > self.max_position_size_pct:
            return {
                'approved': False,
                'reason': f"Position size {position_size_pct:.2f}% exceeds max {self.max_position_size_pct}%"
            }
        
        # Rule 2: Max open positions
        if side == 'buy' and self.open_positions_count >= self.max_open_positions:
            return {
                'approved': False,
                'reason': f"Maximum {self.max_open_positions} open positions reached"
            }
        
        # Rule 3: Daily loss limit
        if self._is_daily_loss_limit_reached():
            return {
                'approved': False,
                'reason': "Daily loss limit reached"
            }
        
        # Rule 4: Minimum position size (avoid dust trades)
        if position_value < 10:  # Minimum £10
            return {
                'approved': False,
                'reason': f"Position value ${position_value} below minimum £10"
            }
        
        # All checks passed
        return {
            'approved': True,
            'reason': 'All risk checks passed',
            'position_size_pct': position_size_pct,
            'risk_amount': portfolio_value * (self.risk_per_trade_pct / 100)
        }
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        price: float,
        stop_loss_pct: Optional[float] = None
    ) -> int:
        """
        Calculate safe position size based on risk parameters.
        Uses the more conservative of:
        - Fixed percentage of portfolio
        - Risk-based sizing with stop loss
        """
        sl_pct = stop_loss_pct or self.stop_loss_pct
        
        # Method 1: Fixed percentage of portfolio
        max_position_value = portfolio_value * (self.max_position_size_pct / 100)
        
        # Method 2: Risk-based sizing
        risk_amount = portfolio_value * (self.risk_per_trade_pct / 100)
        risk_shares = int(risk_amount / (price * (sl_pct / 100))) if sl_pct > 0 else 0
        
        # Take the more conservative (smaller) position
        shares_by_value = int(max_position_value / price)
        shares = min(shares_by_value, risk_shares) if risk_shares > 0 else shares_by_value
        
        return max(0, shares)
    
    def record_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        entry_price: float,
        exit_price: Optional[float] = None
    ):
        """Record a trade for tracking and analytics."""
        self.daily_trades += 1
        
        if side == 'buy':
            self.open_positions_count += 1
        else:
            self.open_positions_count = max(0, self.open_positions_count - 1)
        
        # Record P&L if closing a position
        if exit_price and side == 'sell':
            pnl = (exit_price - entry_price) * quantity
            self.daily_pnl += pnl
            
            if pnl < 0:
                self.daily_losses += abs(pnl)
        
        self._save_state()
        logger.debug(f"Trade recorded: {side} {quantity} {symbol} @ {entry_price}")
    
    def reset_daily_counters(self):
        """Reset daily tracking counters (called at midnight)."""
        logger.info(
            f"Daily reset | P&L: ${self.daily_pnl:.2f} | "
            f"Trades: {self.daily_trades} | Losses: ${self.daily_losses:.2f}"
        )
        
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_losses = 0.0
        self.open_positions_count = 0
        
        self._save_state()
    
    def _is_daily_loss_limit_reached(self) -> bool:
        """Check if daily loss limit has been reached."""
        # Simplified: assume $10,000 portfolio for calculation
        portfolio_value = 10000
        max_daily_loss = portfolio_value * (self.max_daily_loss_pct / 100)
        
        return self.daily_losses >= max_daily_loss
    
    def get_risk_status(self) -> Dict:
        """Get current risk status for dashboard."""
        portfolio_value = 10000  # Would come from actual portfolio in production
        max_daily_loss = portfolio_value * (self.max_daily_loss_pct / 100)
        
        return {
            'can_trade_live': self.can_trade_live(),
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'daily_losses': self.daily_losses,
            'daily_loss_limit': max_daily_loss,
            'daily_loss_usage_pct': (self.daily_losses / max_daily_loss * 100) if max_daily_loss > 0 else 0,
            'open_positions': self.open_positions_count,
            'max_open_positions': self.max_open_positions,
            'risk_per_trade_pct': self.risk_per_trade_pct,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct
        }
    
    def _save_state(self):
        """Save state to disk."""
        state = {
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'daily_losses': self.daily_losses,
            'open_positions_count': self.open_positions_count,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving risk manager state: {e}")
    
    def _load_state(self):
        """Load state from disk."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.daily_pnl = state.get('daily_pnl', 0.0)
                    self.daily_trades = state.get('daily_trades', 0)
                    self.daily_losses = state.get('daily_losses', 0.0)
                    self.open_positions_count = state.get('open_positions_count', 0)
                logger.debug("Risk manager state loaded")
        except Exception as e:
            logger.error(f"Error loading risk manager state: {e}")
