# app/ml/feature_engineering.py
import pandas as pd
import numpy as np

async def compute_fund_features(fund_id: str, lookback_days: int = 252):
    """Compute financial features for a fund"""
    navs = await get_navs_for_fund(fund_id)  # Your existing function
    
    df = pd.DataFrame([
        {"date": nav.date, "nav": nav.nav} 
        for nav in navs
    ])
    
    # Calculate returns and risk metrics
    df['daily_return'] = df['nav'].pct_change()
    df['volatility_20d'] = df['daily_return'].rolling(20).std() * np.sqrt(252)
    df['sharpe_ratio'] = df['daily_return'].rolling(60).mean() / df['daily_return'].rolling(60).std()
    df['max_drawdown'] = calculate_max_drawdown(df['nav'])
    
    return df.tail(1).to_dict('records')[0]  # Latest features
