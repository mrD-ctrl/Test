"""
Trading212 Smart Bot - Trading Routes
Handles order execution, position management, and trading signals
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

from app.core.config import settings
from app.services.trading212_client import Trading212Client
from app.services.ml_engine import get_ml_engine

router = APIRouter()


class OrderRequest(BaseModel):
    """Model for placing a trade order"""
    symbol: str = Field(..., description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    order_type: str = Field(default="market", description="Order type: market or limit")
    side: str = Field(..., description="Order side: buy or sell")
    limit_price: Optional[float] = Field(None, gt=0, description="Limit price for limit orders")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")


class OrderResponse(BaseModel):
    """Response for order placement"""
    order_id: str
    status: str
    symbol: str
    side: str
    quantity: float
    executed_price: Optional[float]
    timestamp: str
    message: str


class TradingSignal(BaseModel):
    """Trading signal from ML engine"""
    symbol: str
    signal: int  # 1=buy, 0=hold, -1=sell
    confidence: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    generated_at: str


@router.post("/order", response_model=OrderResponse)
async def place_order(order: OrderRequest):
    """
    Place a trade order through Trading212
    
    Supports both paper trading and live execution based on settings
    """
    try:
        # Validate order
        if order.side not in ["buy", "sell"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order side must be 'buy' or 'sell'"
            )
        
        if order.order_type == "limit" and not order.limit_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit price required for limit orders"
            )
        
        # Check risk limits
        if order.quantity * (order.limit_price or 100) > settings.MAX_ORDER_VALUE_GBP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order value exceeds maximum allowed ({settings.MAX_ORDER_VALUE_GBP} GBP)"
            )
        
        # Execute order
        client = Trading212Client()
        
        if settings.EXECUTION_MODE == "paper":
            # Paper trading mode
            result = await client.place_paper_order(order.dict())
        else:
            # Live trading mode
            result = await client.place_live_order(order.dict())
        
        return OrderResponse(
            order_id=result.get("order_id", "unknown"),
            status=result.get("status", "pending"),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            executed_price=result.get("executed_price"),
            timestamp=datetime.now().isoformat(),
            message=result.get("message", "Order placed successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error placing order: {str(e)}"
        )


@router.get("/signals/{symbol}", response_model=TradingSignal)
async def get_trading_signal(symbol: str):
    """
    Get AI-generated trading signal for a symbol
    
    Uses ML engine to analyze market data and generate signals
    """
    try:
        ml_engine = get_ml_engine()
        
        # Get market data
        from app.services.data_collector import get_data_collector
        collector = get_data_collector()
        
        market_data = await collector.get_stock_data(symbol, period="3mo")
        
        if market_data is None or len(market_data) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for {symbol}"
            )
        
        # Prepare features and get prediction
        features = ml_engine.prepare_features(market_data)
        signal, confidence = ml_engine.predict_signal(features[-1])
        
        # Calculate target prices
        current_price = float(market_data['close'].iloc[-1])
        params = ml_engine.strategy_params
        
        target_price = current_price * (1 + params['take_profit_pct'] / 100) if signal == 1 else None
        stop_loss = current_price * (1 - params['stop_loss_pct'] / 100) if signal != 0 else None
        
        return TradingSignal(
            symbol=symbol.upper(),
            signal=signal,
            confidence=float(confidence),
            target_price=target_price,
            stop_loss=stop_loss,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating signal: {str(e)}"
        )


@router.get("/positions")
async def get_open_positions():
    """Get all open positions from Trading212"""
    try:
        client = Trading212Client()
        positions = await client.get_positions()
        
        return {
            "positions": positions,
            "total_count": len(positions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching positions: {str(e)}"
        )


@router.post("/close-position/{symbol}")
async def close_position(symbol: str, quantity: Optional[float] = None):
    """Close an existing position (full or partial)"""
    try:
        client = Trading212Client()
        result = await client.close_position(symbol, quantity)
        
        return {
            "status": "success",
            "symbol": symbol,
            "closed_quantity": quantity or "all",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error closing position: {str(e)}"
        )


@router.get("/history")
async def get_trading_history(days: int = 30):
    """Get trading history for specified number of days"""
    try:
        client = Trading212Client()
        history = await client.get_order_history(days)
        
        return {
            "history": history,
            "period_days": days,
            "total_orders": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
        )


@router.post("/execute-auto-trades")
async def execute_auto_trades():
    """
    Execute automated trading based on ML signals
    
    Only available in Pro/Enterprise tiers with auto-execution enabled
    """
    if settings.EXECUTION_MODE != "live":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auto-trading only available in live mode"
        )
    
    try:
        ml_engine = get_ml_engine()
        collector = get_data_collector()
        
        # Define watchlist (in production, get from user settings)
        watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA"]
        
        executed_trades = []
        
        for symbol in watchlist:
            # Get signal
            signal_response = await get_trading_signal(symbol)
            
            if signal_response.signal != 0 and signal_response.confidence > 0.7:
                # Strong signal - execute trade
                order = OrderRequest(
                    symbol=symbol,
                    quantity=10,  # In production, calculate based on position sizing
                    side="buy" if signal_response.signal == 1 else "sell",
                    stop_loss=signal_response.stop_loss,
                    take_profit=signal_response.target_price
                )
                
                result = await place_order(order)
                executed_trades.append(result.dict())
        
        return {
            "executed_trades": executed_trades,
            "count": len(executed_trades),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing auto-trades: {str(e)}"
        )
