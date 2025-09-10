# app/ml/recommender_model.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
import numpy as np

class MutualFundRecommender:
    def __init__(self):
        self.fund_features = None
        self.user_fund_matcher = RandomForestRegressor()
        self.fund_clusterer = KMeans(n_clusters=5)
    
    async def train(self):
        # Build feature matrix using your existing systems
        self.fund_features = await build_fund_feature_matrix()
        
        # Cluster funds by risk characteristics
        risk_features = self.fund_features[['risk_score', 'volatility', 'max_drawdown']]
        self.fund_clusterer.fit(risk_features)
        self.fund_features['cluster'] = self.fund_clusterer.labels_
    
    def recommend_funds(self, user_risk_score: int, user_category: str, top_n: int = 5):
        """Recommend funds based on user questionnaire results"""
        
        # Map questionnaire score to risk tolerance
        risk_tolerance = self._map_score_to_tolerance(user_risk_score)
        
        # Filter funds by risk compatibility
        compatible_funds = self.fund_features[
            abs(self.fund_features['risk_score'] - risk_tolerance) < 20
        ]
        
        # Rank by performance metrics
        recommendations = compatible_funds.nlargest(top_n, 'risk_score')
        
        return recommendations[['fund_id', 'risk_score', 'volatility']].to_dict('records')
    
    def _map_score_to_tolerance(self, questionnaire_score: int) -> float:
        """Map your questionnaire score (12-60) to risk tolerance"""
        # Use your existing SCORE_RANGES mapping
        for low, high, category in SCORE_RANGES:
            if low <= questionnaire_score <= high:
                return (questionnaire_score / 60) * 100  # Normalize to 0-100
        return 50  # Default moderate risk
