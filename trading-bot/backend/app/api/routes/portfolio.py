"""
Trading212 Smart Bot - Portfolio Routes
Portfolio management, analytics, and ISA tracking
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from datetime import datetime

from app.services.trading212_client import Trading212Client
from app.core.config import settings

router = APIRouter()


@router.get("/summary")
async def get_portfolio_summary():
    """Get comprehensive portfolio summary"""
    client = Trading212Client()
    
    account_info = await client.get_account_info()
    positions = await client.get_positions()
    portfolio_value = await client.get_portfolio_value()
    
    # Calculate metrics
    total_invested = sum(pos["quantity"] * pos["entry_price"] for pos in positions)
    current_value = sum(
        pos["quantity"] * pos.get("current_price", pos["entry_price"]) 
        for pos in positions
    )
    total_pnl = current_value - total_invested if total_invested > 0 else 0
    pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "account": {
            "type": account_info["account_type"],
            "currency": account_info["currency"],
            "isa_limit_remaining": account_info.get("isa_limit_remaining", 0)
        },
        "balances": {
            "cash": portfolio_value["cash"],
            "positions_value": portfolio_value["positions_value"],
            "total_equity": portfolio_value["total_equity"]
        },
        "performance": {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_pnl": round(total_pnl, 2),
            "pnl_percent": round(pnl_percent, 2)
        },
        "positions_count": len(positions),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/allocation")
async def get_asset_allocation():
    """Get portfolio asset allocation by sector/position"""
    client = Trading212Client()
    positions = await client.get_positions()
    
    if not positions:
        return {"allocation": [], "total_value": 0}
    
    total_value = sum(
        pos["quantity"] * pos.get("current_price", pos["entry_price"])
        for pos in positions
    )
    
    allocation = []
    for pos in positions:
        value = pos["quantity"] * pos.get("current_price", pos["entry_price"])
        percentage = (value / total_value * 100) if total_value > 0 else 0
        
        allocation.append({
            "symbol": pos["symbol"],
            "value": round(value, 2),
            "percentage": round(percentage, 2),
            "quantity": pos["quantity"],
            "avg_price": pos["entry_price"]
        })
    
    # Sort by percentage descending
    allocation.sort(key=lambda x: x["percentage"], reverse=True)
    
    return {
        "allocation": allocation,
        "total_value": round(total_value, 2),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    client = Trading212Client()
    positions = await client.get_positions()
    
    # Calculate various metrics
    winning_positions = [
        p for p in positions 
        if p.get("current_price", p["entry_price"]) > p["entry_price"]
    ]
    losing_positions = [
        p for p in positions
        if p.get("current_price", p["entry_price"]) < p["entry_price"]
    ]
    
    total_unrealized_pnl = sum(
        (p.get("current_price", p["entry_price"]) - p["entry_price"]) * p["quantity"]
        for p in positions
    )
    
    return {
        "metrics": {
            "total_positions": len(positions),
            "winning_positions": len(winning_positions),
            "losing_positions": len(losing_positions),
            "win_rate": round(len(winning_positions) / max(1, len(positions)) * 100, 2),
            "total_unrealized_pnl": round(total_unrealized_pnl, 2),
            "average_position_size": round(
                sum(p["quantity"] * p["entry_price"] for p in positions) / max(1, len(positions)), 2
            )
        },
        "top_performers": sorted(
            positions,
            key=lambda x: (x.get("current_price", x["entry_price"]) - x["entry_price"]) / x["entry_price"],
            reverse=True
        )[:5],
        "worst_performers": sorted(
            positions,
            key=lambda x: (x.get("current_price", x["entry_price"]) - x["entry_price"]) / x["entry_price"]
        )[:5],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/isa-tracking")
async def track_isa_contributions():
    """Track ISA contributions against annual limit"""
    if settings.TRADING212_ACCOUNT_TYPE != "isa":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISA tracking only available for ISA accounts"
        )
    
    client = Trading212Client()
    account_info = await client.get_account_info()
    
    # Calculate contributions this tax year
    # In production, track from tax year start date (April 6)
    tax_year_start = datetime(datetime.now().year - 1 if datetime.now().month < 4 else datetime.now().year, 4, 6)
    
    # Simulated contribution tracking
    contributions_ytd = account_info["balance"] * 0.8  # Estimate
    
    remaining_limit = settings.ISA_ANNUAL_LIMIT - contributions_ytd
    
    return {
        "account_type": "ISA",
        "tax_year": f"{tax_year_start.year}-{tax_year_start.year + 1}",
        "annual_limit": settings.ISA_ANNUAL_LIMIT,
        "contributed_ytd": round(contributions_ytd, 2),
        "remaining_limit": round(max(0, remaining_limit), 2),
        "utilization_percent": round(contributions_ytd / settings.ISA_ANNUAL_LIMIT * 100, 2),
        "tax_year_start": tax_year_start.isoformat(),
        "warning": "Consult a tax advisor for accurate ISA tracking"
    }


@router.get("/risk-analysis")
async def analyze_portfolio_risk():
    """Analyze portfolio risk metrics"""
    client = Trading212Client()
    positions = await client.get_positions()
    account_info = await client.get_account_info()
    
    if not positions:
        return {"risk_level": "low", "details": "No positions to analyze"}
    
    # Calculate concentration risk
    total_value = sum(
        p["quantity"] * p.get("current_price", p["entry_price"])
        for p in positions
    )
    
    largest_position_pct = max(
        (p["quantity"] * p.get("current_price", p["entry_price"])) / total_value
        for p in positions
    ) if total_value > 0 else 0
    
    # Risk assessment
    risk_factors = []
    risk_score = 0
    
    if largest_position_pct > 0.25:
        risk_factors.append("High concentration in single position")
        risk_score += 2
    elif largest_position_pct > 0.15:
        risk_factors.append("Moderate concentration risk")
        risk_score += 1
    
    if len(positions) < 5:
        risk_factors.append("Limited diversification")
        risk_score += 1
    
    if len(positions) > 20:
        risk_factors.append("Over-diversification may dilute returns")
        risk_score += 0.5
    
    # Determine overall risk level
    if risk_score >= 3:
        risk_level = "high"
    elif risk_score >= 1.5:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "risk_factors": risk_factors,
        "metrics": {
            "largest_position_percent": round(largest_position_pct * 100, 2),
            "total_positions": len(positions),
            "portfolio_value": round(total_value, 2),
            "cash_reserve": account_info["balance"],
            "cash_percent": round(account_info["balance"] / (total_value + account_info["balance"]) * 100, 2)
        },
        "recommendations": [
            "Consider rebalancing if any position exceeds 10% of portfolio",
            "Maintain at least 5-10% cash for opportunities",
            "Diversify across sectors and geographies"
        ] if risk_level != "low" else ["Portfolio risk appears well-managed"]
    }
