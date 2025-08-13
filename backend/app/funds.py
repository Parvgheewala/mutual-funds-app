from fastapi import APIRouter, Query
from mftool import Mftool
import httpx
from fastapi import HTTPException

router = APIRouter()
mf = Mftool()

@router.get("/names")
async def get_mutual_fund_names(page: int = Query(1, ge=1)):
    try:
        all_scheme_codes = mf.get_scheme_codes()
        # Create list of dictionaries with both code and name
        funds = [
            {"code": code, "name": name.replace('Scheme', '').strip()} 
            for code, name in all_scheme_codes.items()
        ]
        
        start_idx = (page - 1) * 20
        end_idx = start_idx + 20
        
        paginated_funds = funds[start_idx:end_idx]
        return {"funds": paginated_funds}
    except Exception as e:
        return {"error": str(e)}

@router.get("/details/{scheme_code}")
async def get_fund_details(scheme_code: str):
    try:
        details = mf.get_scheme_details(scheme_code)
        return details
    except Exception as e:
        return {"error": str(e)}

@router.get("/mutualfunds")
def get_mutual_funds(
    start: int = Query(0, ge=0),
    end: int = Query(100, ge=1)
):
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

@router.get("/search")
async def search_funds(q: str):
    try:
        all_scheme_codes = mf.get_scheme_codes()
        # Filter funds based on search query
        matching_funds = [
            {"code": code, "name": name.replace('Scheme', '').strip()}
            for code, name in all_scheme_codes.items()
            if q.lower() in name.lower()
        ]
        return {"funds": matching_funds[:10]}  # Limit to top 10 matches
    except Exception as e:
        return {"error": str(e)}
