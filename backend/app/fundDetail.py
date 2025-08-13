from fastapi import APIRouter, Path, HTTPException
import httpx

router = APIRouter()

@router.get("/mutualfund/{scheme_code}")
def get_mutual_fund_details(
    scheme_code: str = Path(..., description="Mutual fund scheme code")
):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail=f"Mutual fund with code {scheme_code} not found")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Error contacting external API: {exc}")

    return data
