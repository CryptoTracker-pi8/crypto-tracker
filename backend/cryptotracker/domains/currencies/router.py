from fastapi import APIRouter, HTTPException, Query

from cryptotracker.domains.currencies.schemas import (
    CurrencyDetailResponse,
    CurrencyHistoryResponse,
    CurrencyListResponse,
)
from cryptotracker.domains.currencies.service import CoinGeckoService

router = APIRouter(prefix="/currencies", tags=["currencies"])

# Initialize service
coin_gecko_service = CoinGeckoService()


@router.get("", response_model=CurrencyListResponse)
async def get_currencies(limit: int = Query(default=50, ge=1, le=250, description="Number of currencies to return")):
    """
    Get list of popular cryptocurrencies.
    """
    try:
        currencies = await coin_gecko_service.get_popular_currencies(limit=limit)
        return CurrencyListResponse(currencies=currencies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch currencies: {str(e)}")


@router.get("/{symbol}", response_model=CurrencyDetailResponse)
async def get_currency(symbol: str):
    """
    Get currency details by symbol.
    """
    try:
        currency = await coin_gecko_service.get_currency_by_symbol(symbol.upper())
        if not currency:
            raise HTTPException(status_code=404, detail=f"Currency {symbol} not found")
        return CurrencyDetailResponse(currency=currency)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch currency: {str(e)}")


@router.get("/{symbol}/history", response_model=CurrencyHistoryResponse)
async def get_currency_history(
    symbol: str,
    days: int = Query(default=7, ge=1, le=365, description="Number of days of history")
):
    """
    Get currency price history.
    """
    try:
        history = await coin_gecko_service.get_currency_history(symbol.upper(), days=days)
        if not history:
            raise HTTPException(status_code=404, detail=f"Currency {symbol} not found")
        return CurrencyHistoryResponse(symbol=symbol.upper(), history=history)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch currency history: {str(e)}")

