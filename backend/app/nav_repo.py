# app/nav_repo.py

from typing import List, Optional
from datetime import date
from app.models import FundNav


async def get_navs_for_fund(
    fund_id: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[FundNav]:
    """
    Retrieve NAV rows for a fund_id within optional start/end date range,
    ordered by ascending date.
    """
    query = FundNav.objects.filter(fund_id=fund_id)
    if start:
        query = query.filter(date__gte=start)
    if end:
        query = query.filter(date__lte=end)
    navs = await query.order_by("date").all()
    return navs


async def get_latest_nav(fund_id: str) -> Optional[FundNav]:
    """
    Retrieve the most recent NAV row for a fund_id.
    """
    latest_nav = await FundNav.objects.filter(fund_id=fund_id).order_by("-date").first()
    return latest_nav
