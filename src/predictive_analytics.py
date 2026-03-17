"""
Predictive Analytics Module
Handles forecasting and predictive modeling
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple, List
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessPredictor:
    """Predictive models for fitness metrics"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
    
    def train_forecast_model(
        self,
        df: pd.DataFrame,
        metric_name: str = 'value',
        forecast_days: int = 7,
        lookback_days: int = 30
    ) -> Dict:
        """
        Train a forecast model using linear regression
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            metric_name: Name of the metric
            forecast_days: Number of days to forecast
            lookback_days: Number of historical days to use for training
            
        Returns:
            Dictionary with model info and metrics
        """
        try:
            df = df.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Create time-based features
            df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
            df['days_since_start_sq'] = df['days_since_start'] ** 2
            
            # Split into train/test
            train_size = int(len(df) * 0.8)
            train_df = df.iloc[:train_size]
            test_df = df.iloc[train_size:]
            
            # Prepare features
            X_train = train_df[['days_since_start', 'days_since_start_sq']].values
            y_train = train_df['value'].values
            
            X_test = test_df[['days_since_start', 'days_since_start_sq']].values
            y_test = test_df['value'].values
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Store model
            self.models[metric_name] = model
            
            logger.info(f"Trained forecast model for {metric_name}: Train R²={train_score:.3f}, Test R²={test_score:.3f}")
            
            return {
                'metric': metric_name,
                'train_r2': train_score,
                'test_r2': test_score,
                'model': model
            }
        
        except Exception as e:
            logger.error(f"Error training forecast model: {e}")
            return None
    
    def predict_future(
        self,
        metric_name: str,
        df: pd.DataFrame,
        days_ahead: int = 7
    ) -> pd.DataFrame:
        """
        Predict future values
        
        Args:
            metric_name: Name of the metric
            df: Historical data
            days_ahead: Number of days to predict
            
        Returns:
            DataFrame with predictions
        """
        try:
            if metric_name not in self.models:
                logger.warning(f"No model found for {metric_name}")
                return None
            
            model = self.models[metric_name]
            df = df.copy()
            df['date'] = pd.to_datetime(df['date'])
            
            # Create features for prediction
            last_day = df['days_since_start'].max()
            future_days = np.arange(last_day + 1, last_day + days_ahead + 1)
            future_dates = [df['date'].max() + timedelta(days=i) for i in range(1, days_ahead + 1)]
            
            X_future = np.column_stack([
                future_days,
                future_days ** 2
            ])
            
            predictions = model.predict(X_future)
            
            forecast_df = pd.DataFrame({
                'date': future_dates,
                'predicted_value': predictions,
                'metric': metric_name
            })
            
            logger.info(f"Generated {days_ahead}-day forecast for {metric_name}")
            return forecast_df
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return None
    
    def train_random_forest_model(
        self,
        df: pd.DataFrame,
        metric_name: str = 'value',
        target_col: str = 'value'
    ) -> Dict:
        """
        Train a Random Forest model for more complex patterns
        
        Args:
            df: DataFrame with features and target
            metric_name: Name of the metric
            target_col: Name of target column
            
        Returns:
            Dictionary with model info
        """
        try:
            df = df.copy()
            
            # Prepare features (exclude target and non-numeric columns)
            feature_cols = [col for col in df.columns 
                          if col not in [target_col, 'date', 'metric']]
            
            X = df[feature_cols].fillna(0).values
            y = df[target_col].values
            
            # Train
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            score = model.score(X, y)
            
            self.models[metric_name] = model
            
            logger.info(f"Trained Random Forest for {metric_name}: R²={score:.3f}")
            logger.info(f"Top features: {feature_importance.head(3)['feature'].tolist()}")
            
            return {
                'metric': metric_name,
                'model': model,
                'r2_score': score,
                'feature_importance': feature_importance
            }
        
        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")
            return None
    
    def identify_trends(self, df: pd.DataFrame, window: int = 7) -> Dict:
        """
        Identify trends in the data
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            window: Window size for trend calculation
            
        Returns:
            Dictionary with trend information
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate trend using moving averages
        df['ma_short'] = df['value'].rolling(window=window//2).mean()
        df['ma_long'] = df['value'].rolling(window=window).mean()
        
        latest_short = df['ma_short'].iloc[-1]
        latest_long = df['ma_long'].iloc[-1]
        
        if latest_short > latest_long:
            trend = 'UPTREND'
        elif latest_short < latest_long:
            trend = 'DOWNTREND'
        else:
            trend = 'NEUTRAL'
        
        # Calculate momentum
        momentum = df['value'].iloc[-1] - df['value'].iloc[-window]
        
        logger.info(f"Identified trend: {trend}, Momentum: {momentum:.2f}")
        
        return {
            'trend': trend,
            'momentum': momentum,
            'short_ma': latest_short,
            'long_ma': latest_long
        }
