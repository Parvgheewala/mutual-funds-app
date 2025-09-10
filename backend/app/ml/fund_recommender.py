# app/ml/fund_recommender.py
from app.fundDetail import _riskometer_from_nav
from app.questionnaire import SCORE_RANGES

async def build_fund_feature_matrix():
    """Build feature matrix for all funds"""
    all_funds = await get_unique_fund_ids()  # Implement this
    features = []
    
    for fund_id in all_funds:
        try:
            # Use your existing risk calculation
            navs = await get_navs_for_fund(fund_id)
            nav_series = convert_to_pandas_series(navs)  # Convert your data
            risk_data = _riskometer_from_nav(nav_series)
            
            features.append({
                'fund_id': fund_id,
                'risk_score': risk_data['risk_score'],
                'volatility': risk_data['metrics']['volatility_pct'],
                'max_drawdown': risk_data['metrics']['max_drawdown_pct'],
                'category': navs[0].category if navs else None
            })
        except Exception as e:
            print(f"Error processing {fund_id}: {e}")
    
    return pd.DataFrame(features)
