from fastapi import APIRouter, Query, HTTPException, Request
import httpx
from mftool import Mftool
from .nav_history import router as nav_history_router

router = APIRouter()
mf = Mftool()

# ---------------------------
# Ping Mftool to check if it's working
# ---------------------------
@router.get("/ping-mf")
async def ping_mftool():
    try:
        schemes = mf.get_scheme_codes()
        return {"status": "ok", "schemes_count": len(schemes)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------
# Get mutual fund names (paginated)
# ---------------------------
@router.get("/names")
async def get_mutual_fund_names(page: int = Query(1, ge=1)):
    try:
        all_scheme_codes = mf.get_scheme_codes()
        funds = [
            {"code": code, "name": name.replace("Scheme", "").strip()}
            for code, name in all_scheme_codes.items()
        ]

        page_size = 20
        total_count = len(funds)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        if page < 1 or start_idx >= total_count:
            raise HTTPException(status_code=400, detail="Page number out of range")

        return {
            "funds": funds[start_idx:end_idx],
            "total_count": total_count,
            "total_pages": total_pages,
            "page": page,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Get mutual fund details by scheme code
# ---------------------------
@router.get("/details/{scheme_code}")
async def get_fund_details(scheme_code: str):
    try:
        details = mf.get_scheme_details(scheme_code)
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------
# Get mutual fund names via mfapi.in (range)
# ---------------------------
@router.get("/mutualfunds")
async def get_mutual_funds(
    start: int = Query(0, ge=0),
    end: int = Query(100, ge=1)
):
    try:
        url = "https://api.mfapi.in/mf"
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if start >= len(data):
            raise HTTPException(status_code=400, detail="Start index out of range")
        if end > len(data):
            end = len(data)
        if end <= start:
            raise HTTPException(status_code=400, detail="End index must be greater than start")

        sliced_data = data[start:end]
        scheme_names = [item["schemeName"] for item in sliced_data if "schemeName" in item]

        return {"fund_names": scheme_names, "start": start, "end": end}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Search mutual funds by query
# ---------------------------
@router.get("/search")
async def search_funds(q: str):
    try:
        all_scheme_codes = mf.get_scheme_codes()
        matching_funds = [
            {"code": code, "name": name.replace("Scheme", "").strip()}
            for code, name in all_scheme_codes.items()
            if q.lower() in name.lower()
        ]
        return {"funds": matching_funds[:10]}  # top 10 matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Get funds by initial letter
# ---------------------------
@router.get("/names_by_initial")
async def get_funds_by_initial(
    initial: str = Query(..., min_length=1, max_length=1, description="Initial letter filter")
):
    try:
        all_scheme_codes = mf.get_scheme_codes()
        initial_lower = initial.lower()
        filtered_funds = [
            {"code": code, "name": name.replace("Scheme", "").strip()}
            for code, name in all_scheme_codes.items()
            if name and name.lower().startswith(initial_lower)
        ]
        return {"funds": filtered_funds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Include nav_history router
# ---------------------------
router.include_router(nav_history_router)
