from fastapi import APIRouter, Path, HTTPException
import httpx
import pandas as pd
import numpy as np

router = APIRouter()

# ---------- Helpers for risk ----------
def _parse_nav_series(history: list[dict]) -> pd.Series:
    # MFAPI.in returns latest-first: [{"date":"DD-MM-YYYY","nav":"123.45"}, ...]
    df = pd.DataFrame(history)
    if df.empty or "nav" not in df or "date" not in df:
        raise ValueError("Invalid NAV history format")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"]).sort_values("date")
    return pd.Series(df["nav"].values, index=df["date"])


def _riskometer_from_nav(navs: pd.Series, freq: str = "D") -> dict:
    rets = navs.pct_change().dropna()
    if len(rets) < 10:
        raise ValueError("Insufficient NAV history to compute risk")
    ann_factor = 252 if freq == "D" else 12

    # Volatility (annualized %)
    vol = rets.std(ddof=1) * np.sqrt(ann_factor) * 100

    # Downside deviation (annualized %)
    downside = rets[rets < 0]
    dd = np.sqrt((downside ** 2).sum() / len(rets)) * np.sqrt(ann_factor) * 100

    # Max drawdown (%)
    cum = (1 + rets).cumprod()
    running_max = cum.cummax()
    mdd = ((cum - running_max) / running_max).min() * 100

    # Normalize to 0-100
    def norm(v, lo, hi):
        return float(np.clip((v - lo) / (hi - lo), 0, 1) * 100)

    vol_s = norm(vol, 0, 40)
    dd_s = norm(abs(mdd), 0, 50)
    downside_s = norm(dd, 0, 30)

    score = vol_s * 0.6 + dd_s * 0.25 + downside_s * 0.15

    if score < 20:
        cat = "Very Low"
    elif score < 40:
        cat = "Low"
    elif score < 60:
        cat = "Moderate"
    elif score < 80:
        cat = "Moderately High"
    elif score < 90:
        cat = "High"
    else:
        cat = "Very High"

    return {
        "risk_score": round(score, 2),
        "category": cat,
        "metrics": {
            "volatility_pct": round(float(vol), 2),
            "downside_deviation_pct": round(float(dd), 2),
            "max_drawdown_pct": round(float(mdd), 2),
        },
    }


@router.get("/{scheme_code}")
def get_mutual_fund_risk(
    scheme_code: str = Path(..., description="Mutual fund scheme code")
):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        response = httpx.get(url, timeout=20.0)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Mutual fund with code {scheme_code} not found")
        response.raise_for_status()
        payload = response.json()
        history = payload.get("data", [])
        if not history:
            raise HTTPException(status_code=502, detail="No NAV history from upstream")

        series = _parse_nav_series(history)
        risk = _riskometer_from_nav(series, freq="D")

        # CHANGE: pick first element (latest) instead of assigning the whole list
        latest = history[0]  # was: latest = history

        latest_nav = pd.to_numeric(latest.get("nav", "nan"), errors="coerce")
        return {
            "scheme_code": scheme_code,
            "scheme_name": payload.get("meta", {}).get("scheme_name"),
            "as_of": latest.get("date"),
            "latest_nav": None if pd.isna(latest_nav) else float(latest_nav),
            "risk": risk,
            "source": "api.mfapi.in",
            "disclaimer": "Computed from historical NAV; not the official SEBI/AMFI Riskometer.",
        }
    except HTTPException:
        raise
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Error contacting external API: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing error: {exc}")
