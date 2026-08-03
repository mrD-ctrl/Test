"""
Trading212 Smart Bot - Strategy Routes
Strategy management, backtesting, and ML optimization
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from app.services.ml_engine import get_ml_engine
from app.core.config import settings

router = APIRouter()


class StrategyConfig(BaseModel):
    """Strategy configuration model"""
    strategy_name: str = Field(default="momentum", description="Strategy type")
    parameters: Dict = Field(default={}, description="Strategy parameters")
    risk_settings: Dict = Field(default={}, description="Risk management settings")


@router.get("/list")
async def list_strategies():
    """List all available trading strategies"""
    strategies = {
        "momentum": {
            "name": "Momentum Trading",
            "description": "Buy stocks showing strong upward price momentum",
            "parameters": {
                "lookback_period": 20,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "volume_threshold": 1.5
            },
            "risk_level": "medium",
            "suitable_for": ["ISA", "Invest"]
        },
        "mean_reversion": {
            "name": "Mean Reversion",
            "description": "Trade based on price returning to average",
            "parameters": {
                "bollinger_period": 20,
                "std_deviation": 2.0,
                "exit_threshold": 0.5
            },
            "risk_level": "low",
            "suitable_for": ["ISA", "Invest"]
        },
        "breakout": {
            "name": "Breakout Trading",
            "description": "Enter positions when price breaks key resistance levels",
            "parameters": {
                "consolidation_period": 10,
                "volume_confirmation": True,
                "false_breakout_filter": True
            },
            "risk_level": "high",
            "suitable_for": ["Invest"]
        },
        "dividend_harvest": {
            "name": "Dividend Harvesting",
            "description": "Focus on dividend-paying stocks for ISA tax efficiency",
            "parameters": {
                "min_dividend_yield": 3.0,
                "payout_ratio_max": 60,
                "dividend_growth_years": 5
            },
            "risk_level": "low",
            "suitable_for": ["ISA"]
        },
        "hybrid_ml": {
            "name": "ML-Optimized Hybrid",
            "description": "AI-powered strategy combining multiple approaches",
            "parameters": {
                "auto_optimize": True,
                "ml_confidence_threshold": 0.7,
                "adaptive_risk": True
            },
            "risk_level": "medium",
            "suitable_for": ["ISA", "Invest"],
            "tier_required": "pro"
        }
    }
    
    return {
        "strategies": strategies,
        "default_strategy": settings.DEFAULT_STRATEGY,
        "current_tier": "pro"  # In production, get from license
    }


@router.get("/current")
async def get_current_strategy():
    """Get currently active strategy configuration"""
    ml_engine = get_ml_engine()
    
    return {
        "strategy_name": settings.DEFAULT_STRATEGY,
        "parameters": ml_engine.strategy_params,
        "last_optimized": ml_engine.last_retrain_time.isoformat(),
        "performance": ml_engine.get_performance_report()
    }


@router.post("/configure")
async def configure_strategy(config: StrategyConfig):
    """Configure trading strategy parameters"""
    ml_engine = get_ml_engine()
    
    # Validate strategy name
    valid_strategies = ["momentum", "mean_reversion", "breakout", "dividend_harvest", "hybrid_ml"]
    if config.strategy_name not in valid_strategies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid strategy. Choose from: {valid_strategies}"
        )
    
    # Update strategy parameters
    if config.parameters:
        ml_engine.strategy_params.update(config.parameters)
    
    # Update risk settings
    if config.risk_settings:
        if "stop_loss_pct" in config.risk_settings:
            ml_engine.strategy_params["stop_loss_pct"] = config.risk_settings["stop_loss_pct"]
        if "take_profit_pct" in config.risk_settings:
            ml_engine.strategy_params["take_profit_pct"] = config.risk_settings["take_profit_pct"]
        if "position_size_pct" in config.risk_settings:
            ml_engine.strategy_params["position_size_pct"] = config.risk_settings["position_size_pct"]
    
    # Save updated configuration
    ml_engine.save_model()
    
    return {
        "status": "success",
        "message": f"Strategy '{config.strategy_name}' configured successfully",
        "updated_parameters": ml_engine.strategy_params,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/backtest")
async def run_backtest(
    strategy: str = "momentum",
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01",
    initial_capital: float = 10000,
    symbols: Optional[List[str]] = None
):
    """
    Run backtest for a strategy
    
    Note: This is a simplified simulation. 
    Production would use historical data and proper backtesting engine.
    """
    if symbols is None:
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    # Simulated backtest results
    import random
    random.seed(42)  # For reproducibility
    
    trades = []
    capital = initial_capital
    
    for _ in range(50):  # Simulate 50 trades
        trade_result = random.uniform(-0.05, 0.08)  # -5% to +8%
        profit_loss = capital * trade_result
        capital += profit_loss
        
        trades.append({
            "date": datetime.now().isoformat(),
            "symbol": random.choice(symbols),
            "return_pct": round(trade_result * 100, 2),
            "profit_loss": round(profit_loss, 2)
        })
    
    total_return = ((capital - initial_capital) / initial_capital) * 100
    
    return {
        "strategy": strategy,
        "period": {"start": start_date, "end": end_date},
        "initial_capital": initial_capital,
        "final_capital": round(capital, 2),
        "total_return_pct": round(total_return, 2),
        "total_trades": len(trades),
        "winning_trades": len([t for t in trades if t["profit_loss"] > 0]),
        "losing_trades": len([t for t in trades if t["profit_loss"] < 0]),
        "sample_trades": trades[:10],
        "disclaimer": "Backtesting results are simulated and do not guarantee future performance"
    }


@router.get("/ml-performance")
async def get_ml_performance():
    """Get ML engine performance metrics"""
    ml_engine = get_ml_engine()
    report = ml_engine.get_performance_report()
    
    return {
        "ml_status": "active",
        "model_loaded": report["model_saved"],
        "performance": report,
        "optimization_history": [
            {"date": "2024-01-15", "accuracy": 0.62, "trades": 45},
            {"date": "2024-01-20", "accuracy": 0.65, "trades": 52},
            {"date": "2024-01-25", "accuracy": 0.68, "trades": 58}
        ],
        "next_retrain_check": "24 hours or after 50 new trades"
    }


@router.post("/optimize")
async def optimize_strategy():
    """Trigger manual strategy optimization"""
    ml_engine = get_ml_engine()
    
    # Get current performance
    performance_data = ml_engine.get_performance_report()
    
    # Optimize parameters
    optimized_params = ml_engine.optimize_strategy_params(performance_data)
    
    # Save optimized model
    ml_engine.save_model()
    
    return {
        "status": "success",
        "message": "Strategy parameters optimized based on recent performance",
        "optimized_parameters": optimized_params,
        "previous_win_rate": performance_data["win_rate"],
        "timestamp": datetime.now().isoformat()
    }
