"""
Trading212 Smart Bot - Authentication Routes
Handles user authentication, API key management, and license validation
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

from app.core.config import settings
from app.services.security import encrypt_api_key, decrypt_api_key

router = APIRouter()


class APIKeyInput(BaseModel):
    """Model for API key input"""
    trading212_api_key: str = Field(..., description="Trading212 API key")
    trading212_pin: Optional[str] = Field(None, description="Trading212 PIN")
    account_type: str = Field(default="isa", description="Account type: isa or invest")
    
    # Optional premium API keys
    eodhd_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Model for API key response (without exposing actual keys)"""
    trading212_configured: bool
    account_type: str
    eodhd_configured: bool
    finnhub_configured: bool
    last_updated: str


class LicenseActivation(BaseModel):
    """Model for license activation"""
    license_key: str = Field(..., description="One-time purchase license key")
    email: str = Field(..., description="User email for license registration")


class LicenseResponse(BaseModel):
    """License status response"""
    license_type: str
    tier: str
    activated: bool
    features: list[str]
    expiry: Optional[str] = None


@router.post("/configure-api-keys", response_model=APIKeyResponse)
async def configure_api_keys(keys: APIKeyInput):
    """
    Configure broker and optional premium API keys
    
    All keys are encrypted before storage
    """
    try:
        # Encrypt and store Trading212 API key
        encrypted_t212 = encrypt_api_key(keys.trading212_api_key)
        
        # Store in secure location (in production, use secrets manager)
        # For demo, we'll just validate the format
        if not keys.trading212_api_key.startswith("t212_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Trading212 API key format"
            )
        
        # Validate account type
        if keys.account_type not in ["isa", "invest"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account type must be 'isa' or 'invest'"
            )
        
        # Store encrypted keys (in production, use database)
        # This is a simplified example
        stored_keys = {
            "trading212": encrypted_t212,
            "account_type": keys.account_type,
            "eodhd": encrypt_api_key(keys.eodhd_api_key) if keys.eodhd_api_key else None,
            "finnhub": encrypt_api_key(keys.finnhub_api_key) if keys.finnhub_api_key else None,
            "updated_at": datetime.now().isoformat()
        }
        
        return APIKeyResponse(
            trading212_configured=True,
            account_type=keys.account_type,
            eodhd_configured=bool(keys.eodhd_api_key),
            finnhub_configured=bool(keys.finnhub_api_key),
            last_updated=stored_keys["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring API keys: {str(e)}"
        )


@router.get("/api-keys-status", response_model=APIKeyResponse)
async def get_api_keys_status():
    """Get status of configured API keys (without exposing actual keys)"""
    # In production, retrieve from secure storage
    return APIKeyResponse(
        trading212_configured=bool(settings.TRADING212_API_KEY),
        account_type=settings.TRADING212_ACCOUNT_TYPE,
        eodhd_configured=settings.EODHD_ENABLED,
        finnhub_configured=settings.FINNHUB_ENABLED,
        last_updated=datetime.now().isoformat()
    )


@router.post("/activate-license", response_model=LicenseResponse)
async def activate_license(license_data: LicenseActivation):
    """
    Activate one-time purchase license
    
    License tiers:
    - Basic (£99): Single account, basic features
    - Pro (£199): Multiple accounts, ML features, auto-execution
    - Enterprise (£399): All features + premium API support
    """
    # Validate license key format
    if not license_data.license_key.startswith("T212-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license key format"
        )
    
    # Determine tier from license key
    tier_mapping = {
        "BASIC": "basic",
        "PRO": "pro", 
        "ENT": "enterprise"
    }
    
    # Extract tier from key (simplified logic)
    key_parts = license_data.license_key.split("-")
    if len(key_parts) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license key structure"
        )
    
    tier_code = key_parts[1][:3].upper()
    tier = tier_mapping.get(tier_code, "basic")
    
    # Define features per tier
    features_by_tier = {
        "basic": [
            "Single account support",
            "Yahoo Finance data",
            "Basic strategies",
            "Manual execution",
            "Community support"
        ],
        "pro": [
            "Unlimited accounts",
            "All free data sources",
            "ML optimization",
            "Auto-execution",
            "Backtesting module",
            "Email support"
        ],
        "enterprise": [
            "Everything in Pro",
            "Premium API integrations",
            "Custom strategies",
            "Priority support",
            "White-label options",
            "Advanced analytics"
        ]
    }
    
    # In production, validate against license server
    # For demo, accept any properly formatted key
    
    return LicenseResponse(
        license_type="One-Time Purchase",
        tier=tier,
        activated=True,
        features=features_by_tier[tier],
        expiry=None  # One-time purchase doesn't expire
    )


@router.get("/license-info", response_model=LicenseResponse)
async def get_license_info():
    """Get current license information"""
    # In production, retrieve from database/license server
    return LicenseResponse(
        license_type="One-Time Purchase",
        tier="pro",  # Demo default
        activated=True,
        features=[
            "Unlimited accounts",
            "All free data sources",
            "ML optimization",
            "Auto-execution",
            "Backtesting module"
        ],
        expiry=None
    )


@router.delete("/api-keys")
async def delete_api_keys():
    """Delete all stored API keys"""
    # In production, securely delete from storage
    return {"message": "API keys deleted successfully", "status": "success"}
