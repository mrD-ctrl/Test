"""
Trading212 Smart Bot - Trading212 Broker Client
Wrapper for Trading212 API with paper trading and live execution support
"""
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from app.core.config import settings


class Trading212Client:
    """
    Trading212 API client wrapper.
    
    Note: Trading212 does not have a public API as of 2024.
    This is a placeholder implementation showing the structure.
    In production, you would need to:
    1. Apply for Trading212 API access
    2. Use unofficial API wrappers (at your own risk)
    3. Implement screen scraping (not recommended)
    
    For this demo, we simulate API calls.
    """
    
    def __init__(self):
        self.base_url = "https://api.trading212.com"  # Placeholder
        self.api_key = settings.TRADING212_API_KEY
        self.account_type = settings.TRADING212_ACCOUNT_TYPE
        self.session = None
        
        # Paper trading state (in-memory for demo)
        self.paper_positions = {}
        self.paper_balance = settings.PAPER_TRADING_INITIAL_BALANCE
        self.paper_orders = []
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        # Simulated response
        return {
            "account_id": "T212-DEMO-12345",
            "account_type": self.account_type,
            "currency": "GBP",
            "balance": self.paper_balance if settings.EXECUTION_MODE == "paper" else 0,
            "equity": self.paper_balance + self._calculate_paper_pnl(),
            "isa_limit_remaining": settings.ISA_ANNUAL_LIMIT if self.account_type == "isa" else 0
        }
    
    def _calculate_paper_pnl(self) -> float:
        """Calculate unrealized P&L for paper positions"""
        total_pnl = 0.0
        for symbol, position in self.paper_positions.items():
            # Simulated current price (in production, fetch from market data)
            current_price = position.get("current_price", position["entry_price"])
            pnl = (current_price - position["entry_price"]) * position["quantity"]
            total_pnl += pnl
        return total_pnl
    
    async def place_paper_order(self, order_data: Dict) -> Dict:
        """Place order in paper trading mode"""
        symbol = order_data["symbol"]
        quantity = order_data["quantity"]
        side = order_data["side"]
        
        # Simulated execution price
        simulated_price = 150.0  # In production, get from market data
        
        order_value = quantity * simulated_price
        
        if side == "buy":
            if order_value > self.paper_balance:
                return {
                    "status": "rejected",
                    "message": "Insufficient balance",
                    "order_id": None
                }
            
            self.paper_balance -= order_value
            
            # Update or create position
            if symbol in self.paper_positions:
                pos = self.paper_positions[symbol]
                avg_price = (pos["entry_price"] * pos["quantity"] + order_value) / (pos["quantity"] + quantity)
                pos["quantity"] += quantity
                pos["entry_price"] = avg_price
            else:
                self.paper_positions[symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "entry_price": simulated_price,
                    "current_price": simulated_price,
                    "entry_date": datetime.now().isoformat()
                }
        else:  # sell
            if symbol not in self.paper_positions or self.paper_positions[symbol]["quantity"] < quantity:
                return {
                    "status": "rejected",
                    "message": "Insufficient position",
                    "order_id": None
                }
            
            self.paper_balance += order_value
            self.paper_positions[symbol]["quantity"] -= quantity
            
            if self.paper_positions[symbol]["quantity"] <= 0:
                del self.paper_positions[symbol]
        
        # Record order
        order_record = {
            "order_id": f"PAPER-{len(self.paper_orders) + 1}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": simulated_price,
            "timestamp": datetime.now().isoformat(),
            "status": "executed"
        }
        self.paper_orders.append(order_record)
        
        logger.info(f"Paper order executed: {side} {quantity} {symbol} @ {simulated_price}")
        
        return {
            "status": "executed",
            "order_id": order_record["order_id"],
            "executed_price": simulated_price,
            "message": "Paper order executed successfully"
        }
    
    async def place_live_order(self, order_data: Dict) -> Dict:
        """Place order in live trading mode"""
        # In production, make actual API call to Trading212
        # This is a simulation
        
        logger.warning("Live trading called but using simulation")
        
        return {
            "status": "simulated",
            "order_id": f"LIVE-SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "executed_price": None,
            "message": "Live order simulation (no real API connection)"
        }
    
    async def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        if settings.EXECUTION_MODE == "paper":
            return list(self.paper_positions.values())
        else:
            # In production, fetch from Trading212 API
            return []
    
    async def close_position(self, symbol: str, quantity: Optional[float] = None) -> Dict:
        """Close a position"""
        if settings.EXECUTION_MODE == "paper":
            if symbol not in self.paper_positions:
                return {"status": "error", "message": "Position not found"}
            
            position = self.paper_positions[symbol]
            close_qty = quantity or position["quantity"]
            
            if close_qty > position["quantity"]:
                return {"status": "error", "message": "Quantity exceeds position"}
            
            # Create sell order
            sell_order = {
                "symbol": symbol,
                "quantity": close_qty,
                "side": "sell"
            }
            
            result = await self.place_paper_order(sell_order)
            return result
        else:
            # In production, make API call to Trading212
            return {"status": "simulated", "message": "Live close position simulation"}
    
    async def get_order_history(self, days: int = 30) -> List[Dict]:
        """Get order history"""
        if settings.EXECUTION_MODE == "paper":
            return self.paper_orders[-100:]  # Last 100 orders
        else:
            # In production, fetch from Trading212 API
            return []
    
    async def get_portfolio_value(self) -> Dict:
        """Get total portfolio value"""
        account_info = await self.get_account_info()
        positions = await self.get_positions()
        
        total_position_value = sum(
            pos["quantity"] * pos.get("current_price", pos["entry_price"])
            for pos in positions
        )
        
        return {
            "cash": account_info["balance"],
            "positions_value": total_position_value,
            "total_equity": account_info["equity"],
            "currency": account_info["currency"],
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
client_instance = None

def get_trading212_client() -> Trading212Client:
    """Get or create Trading212 client singleton"""
    global client_instance
    if client_instance is None:
        client_instance = Trading212Client()
    return client_instance
