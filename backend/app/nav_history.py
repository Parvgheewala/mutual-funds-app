from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

BASE_URL = "https://api.mfapi.in/mf"

@router.get("/nav_history/{scheme_code}")
async def get_nav_history(scheme_code: str):
    """
    Fetches NAV history for a given mutual fund scheme code from mfapi.in
    """
    url = f"{BASE_URL}/{scheme_code}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return {"data": data.get("data", [])}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
