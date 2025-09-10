# app/routers/recommendations.py
from fastapi import APIRouter, Depends
from app.ml.recommender_model import MutualFundRecommender

router = APIRouter()
recommender = MutualFundRecommender()

@router.post("/recommend")
async def get_fund_recommendations(
    user_risk_score: int,
    user_category: str = "Balanced Growth",
    top_n: int = 5
):
    """Get personalized mutual fund recommendations"""
    recommendations = recommender.recommend_funds(
        user_risk_score=user_risk_score,
        user_category=user_category,
        top_n=top_n
    )
    
    return {
        "user_profile": user_category,
        "risk_score": user_risk_score,
        "recommendations": recommendations
    }
