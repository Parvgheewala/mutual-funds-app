# app/routers/navs_store.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date

from app.nav_repo import get_navs_for_fund, get_latest_nav

router = APIRouter()


@router.get("/series/{fund_id}")
async def nav_series(
    fund_id: str,
    start: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
):
    navs = await get_navs_for_fund(fund_id, start, end)
    if not navs:
        raise HTTPException(status_code=404, detail="No NAV data found for fund")
    return [
        {
            "date": nav.date.isoformat(),
            "nav": nav.nav,
            "aum": nav.aum,
            "scheme_name": nav.scheme_name,
            "category": nav.category,
        }
        for nav in navs
    ]


@router.get("/latest/{fund_id}")
async def nav_latest(fund_id: str):
    nav = await get_latest_nav(fund_id)
    if not nav:
        raise HTTPException(status_code=404, detail="No NAV data found for fund")
    return {
        "date": nav.date.isoformat(),
        "nav": nav.nav,
        "aum": nav.aum,
        "scheme_name": nav.scheme_name,
        "category": nav.category,
    }
