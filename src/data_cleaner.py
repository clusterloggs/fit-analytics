"""
Data Cleaning Module
Handles data cleaning, validation, and preprocessing
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessDataCleaner:
    """Clean and validate fitness data"""
    
    @staticmethod
    def clean_steps(df: pd.DataFrame) -> pd.DataFrame:
        """Clean step count data"""
        df = df.copy()
        
        # Remove null values
        df = df.dropna(subset=['value'])
        
        # Remove negative values (impossible)
        df = df[df['value'] >= 0]
        
        # Remove outliers (steps > 50000 per day is unrealistic)
        df = df[df['value'] <= 50000]
        
        logger.info(f"Cleaned steps data: {len(df)} records remaining")
        return df
    
    @staticmethod
    def clean_heart_rate(df: pd.DataFrame) -> pd.DataFrame:
        """Clean heart rate data"""
        df = df.copy()
        
        # Remove null values
        df = df.dropna(subset=['value'])
        
        # Remove physiologically impossible values (HR typically 40-220 bpm)
        df = df[(df['value'] >= 30) & (df['value'] <= 250)]
        
        logger.info(f"Cleaned heart rate data: {len(df)} records remaining")
        return df
    
    @staticmethod
    def clean_sleep(df: pd.DataFrame) -> pd.DataFrame:
        """Clean sleep data"""
        df = df.copy()
        
        # Remove null values
        df = df.dropna(subset=['value'])
        
        # Limit sleep duration to realistic values (0-12 hours)
        df = df[(df['value'] >= 0) & (df['value'] <= 43200)]
        
        logger.info(f"Cleaned sleep data: {len(df)} records remaining")
        return df
    
    @staticmethod
    def clean_calories(df: pd.DataFrame) -> pd.DataFrame:
        """Clean calories data"""
        df = df.copy()
        
        # Remove null values
        df = df.dropna(subset=['value'])
        
        # Remove negative values
        df = df[df['value'] >= 0]
        
        # Remove extreme outliers (> 10000 calories per day)
        df = df[df['value'] <= 10000]
        
        logger.info(f"Cleaned calories data: {len(df)} records remaining")
        return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate records"""
        if subset is None:
            subset = ['timestamp']
        
        initial_len = len(df)
        df = df.drop_duplicates(subset=subset)
        removed = initial_len - len(df)
        
        if removed > 0:
            logger.info(f"Removed {removed} duplicate records")
        
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, method: str = 'interpolate') -> pd.DataFrame:
        """Handle missing values"""
        df = df.copy()
        
        if method == 'interpolate':
            df['value'] = df['value'].interpolate(method='linear', limit_direction='both')
        elif method == 'forward_fill':
            df['value'] = df['value'].fillna(method='ffill')
        elif method == 'backward_fill':
            df['value'] = df['value'].fillna(method='bfill')
        elif method == 'drop':
            df = df.dropna(subset=['value'])
        
        logger.info(f"Handled missing values using {method} method")
        return df
