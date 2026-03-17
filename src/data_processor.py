"""
Data Processing Module
Handles feature engineering and data transformation
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessDataProcessor:
    """Process and engineer features for analysis"""
    
    @staticmethod
    def aggregate_daily(df: pd.DataFrame, metric: str = 'mean') -> pd.DataFrame:
        """Aggregate data to daily level"""
        df = df.copy()
        # The timestamp column is expected from the data importer
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        if metric == 'mean':
            daily = df.groupby('date')['value'].mean()
        elif metric == 'sum':
            daily = df.groupby('date')['value'].sum()
        elif metric == 'max':
            daily = df.groupby('date')['value'].max()
        elif metric == 'min':
            daily = df.groupby('date')['value'].min()
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        result_df = daily.reset_index()
        result_df.columns = ['date', 'value']
        
        logger.info(f"Aggregated data to daily level using {metric}")
        return result_df

    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame, windows: List[int] = None) -> pd.DataFrame:
        """
        Calculate moving averages
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            windows: List of window sizes (e.g., [7, 14, 30])
        """
        if windows is None:
            windows = [7, 14, 30]
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        for window in windows:
            df[f'ma_{window}'] = df['value'].rolling(window=window, min_periods=1).mean()
        
        logger.info(f"Calculated moving averages for windows: {windows}")
        return df
    
    @staticmethod
    def calculate_rolling_std(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """Calculate rolling standard deviation"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['rolling_std'] = df['value'].rolling(window=window, min_periods=1).std()
        
        logger.info(f"Calculated rolling std with window {window}")
        return df
    
    @staticmethod
    def calculate_daily_change(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate day-over-day change"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['daily_change'] = df['value'].diff()
        df['pct_change'] = df['value'].pct_change() * 100
        
        logger.info("Calculated daily change metrics")
        return df
    
    @staticmethod
    def calculate_weekly_stats(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate weekly statistics"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['week'] = df['date'].dt.isocalendar().week
        df['year'] = df['date'].dt.year
        
        weekly = df.groupby(['year', 'week']).agg({
            'value': ['sum', 'mean', 'min', 'max', 'std', 'count']
        }).reset_index()
        
        weekly.columns = ['year', 'week', 'weekly_sum', 'weekly_mean', 
                         'weekly_min', 'weekly_max', 'weekly_std', 'weekly_count']
        
        logger.info("Calculated weekly statistics")
        return weekly
    
    @staticmethod
    def normalize_data(df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """
        Normalize data
        
        Args:
            df: DataFrame with 'value' column
            method: 'minmax' or 'zscore'
        """
        df = df.copy()
        
        if method == 'minmax':
            min_val = df['value'].min()
            max_val = df['value'].max()
            df['value_normalized'] = (df['value'] - min_val) / (max_val - min_val)
        elif method == 'zscore':
            mean_val = df['value'].mean()
            std_val = df['value'].std()
            df['value_normalized'] = (df['value'] - mean_val) / std_val
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        logger.info(f"Normalized data using {method} method")
        return df
    
    @staticmethod
    def add_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add datetime-based features"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        logger.info("Added datetime features")
        return df
    
    @staticmethod
    def add_lag_features(df: pd.DataFrame, lags: List[int] = None) -> pd.DataFrame:
        """
        Add lagged features for time-series modeling
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            lags: List of lag periods (e.g., [1, 7, 14])
        """
        if lags is None:
            lags = [1, 7, 14]
        
        df = df.copy()
        df = df.sort_values('date')
        
        for lag in lags:
            df[f'lag_{lag}'] = df['value'].shift(lag)
        
        logger.info(f"Added lag features: {lags}")
        return df
    
    @staticmethod
    def fill_missing_dates(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
        """Fill missing dates with interpolation"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Create complete date range
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq=freq)
        df_complete = pd.DataFrame({'date': date_range})
        
        # Merge with original data
        df_result = df_complete.merge(df, on='date', how='left')
        
        # Interpolate missing values
        df_result['value'] = df_result['value'].interpolate(method='linear')
        df_result['value'] = df_result['value'].fillna(method='bfill').fillna(method='ffill')
        
        logger.info(f"Filled missing dates, total records: {len(df_result)}")
        return df_result
