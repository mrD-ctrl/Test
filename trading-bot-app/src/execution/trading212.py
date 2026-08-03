"""
Trading 212 API Client
Based on official Trading 212 API specifications
"""
import httpx
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Trading212Client:
    """
    Client for Trading 212 API.
    Supports both Invest and ISA accounts.
    """
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.client = httpx.AsyncClient(headers=self.headers, base_url=base_url)
        logger.info(f"Initialized Trading 212 client for {base_url}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_account_info(self) -> Optional[Dict]:
        """Get account information."""
        try:
            response = await self.client.get('/accounts')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
    
    async def get_positions(self) -> List[Dict]:
        """Get current portfolio positions."""
        try:
            response = await self.client.get('/positions')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    async def get_balance(self) -> Optional[float]:
        """Get available cash balance."""
        try:
            positions = await self.get_positions()
            # Balance calculation depends on API response structure
            # This is a simplified version
            return None
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None
    
    async def place_order(
        self,
        instrument_id: str,
        order_type: str,
        side: str,
        quantity: Optional[float] = None,
        value: Optional[float] = None,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Place an order.
        
        Args:
            instrument_id: Instrument identifier
            order_type: MARKET, LIMIT, STOP, etc.
            side: BUY or SELL
            quantity: Number of shares (for quantity orders)
            value: Order value in currency (for value orders)
            price: Limit/stop price
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Order confirmation or None if error
        """
        try:
            order_data = {
                'instrumentId': instrument_id,
                'type': order_type,
                'side': side,
            }
            
            if quantity is not None:
                order_data['quantity'] = quantity
            
            if value is not None:
                order_data['value'] = value
            
            if price is not None:
                order_data['price'] = price
            
            if stop_loss is not None:
                order_data['stopLoss'] = stop_loss
            
            if take_profit is not None:
                order_data['takeProfit'] = take_profit
            
            response = await self.client.post('/orders', json=order_data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Order placed successfully: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        try:
            response = await self.client.delete(f'/orders/{order_id}')
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    async def get_order_history(self, limit: int = 50) -> List[Dict]:
        """Get order history."""
        try:
            response = await self.client.get('/orders', params={'limit': limit})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            return []
    
    async def get_instrument(self, symbol: str) -> Optional[Dict]:
        """Get instrument details by ISIN or symbol."""
        try:
            response = await self.client.get('/instruments', params={'search': symbol})
            response.raise_for_status()
            instruments = response.json()
            
            if instruments:
                return instruments[0]
            return None
        except Exception as e:
            logger.error(f"Error getting instrument: {str(e)}")
            return None
    
    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            response = await self.client.get('/accounts')
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


class Trading212Manager:
    """Manages Trading 212 connection and operations."""
    
    def __init__(self, settings):
        self.settings = settings
        self.client: Optional[Trading212Client] = None
        self.is_connected = False
        
        if settings.has_trading212_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Trading 212 client."""
        try:
            self.client = Trading212Client(
                api_key=self.settings.TRADING212_API_KEY,
                base_url=self.settings.TRADING212_BASE_URL
            )
            self.is_connected = True
            logger.info("Trading 212 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Trading 212 client: {str(e)}")
            self.is_connected = False
    
    async def connect(self) -> bool:
        """Test and establish connection."""
        if not self.client:
            return False
        
        self.is_connected = await self.client.test_connection()
        return self.is_connected
    
    async def disconnect(self):
        """Close connection."""
        if self.client:
            await self.client.close()
            self.is_connected = False
    
    async def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary."""
        if not self.is_connected:
            return {'error': 'Not connected'}
        
        try:
            positions = await self.client.get_positions()
            # balance = await self.client.get_balance()
            
            total_value = sum(
                pos.get('marketValue', 0) 
                for pos in positions
            )
            
            return {
                'positions': positions,
                'position_count': len(positions),
                'total_value': total_value,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {'error': str(e)}
    
    async def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Optional[Dict]:
        """Execute a trade."""
        if not self.is_connected:
            logger.error("Cannot execute trade: Not connected to Trading 212")
            return None
        
        try:
            # Get instrument ID
            instrument = await self.client.get_instrument(symbol)
            if not instrument:
                logger.error(f"Instrument not found: {symbol}")
                return None
            
            instrument_id = instrument.get('id')
            
            # Place order
            result = await self.client.place_order(
                instrument_id=instrument_id,
                order_type=order_type,
                side=side,
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return None
