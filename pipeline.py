"""
Main workflow orchestrator
Coordinates data import, cleaning, processing, and analysis
"""
import sys
import os
from pathlib import Path
import logging
from sqlalchemy import create_engine
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, DATA_RETENTION_DAYS, DATABASE_FILE
from src.data_importer import FitnessDataImporter
from src.data_cleaner import FitnessDataCleaner
from src.data_processor import FitnessDataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'fitness_analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FitnessAnalyticsPipeline:
    """Main pipeline for fitness analytics"""
    
    def __init__(self):
        self.importer = FitnessDataImporter()
        self.cleaner = FitnessDataCleaner()
        self.processor = FitnessDataProcessor()
    
    def run_full_pipeline(self, days_back: int = 30, save_intermediate: bool = True, fetch_new: bool = True):
        """
        Run the complete analytics pipeline
        
        Args:
            days_back: Number of days to retrieve
            save_intermediate: Save intermediate results
            fetch_new: Whether to fetch new data from API or load local
        """
        logger.info("=" * 60)
        logger.info("Starting Fitness Analytics Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Data Import
        if fetch_new:
            logger.info("\n[STEP 1] Importing data from Google Fit...")
            raw_data = self.importer.import_all_data(days_back=days_back)
            if save_intermediate:
                logger.info("Saving raw data...")
                self.importer.save_raw_data()
        else:
            logger.info("\n[STEP 1] Loading local data (skipping API)...")
            raw_data = self.importer.load_local_data()
        
        if not raw_data:
            logger.error("No data found to process.")
            return False
        
        logger.info(f"Successfully imported {len(raw_data)} data types")
        
        # Step 2: Data Cleaning
        logger.info("\n[STEP 2] Cleaning data...")
        cleaned_data = self._clean_all_data(raw_data)
        logger.info(f"Cleaned {len(cleaned_data)} datasets")
        
        # Step 3: Data Processing
        logger.info("\n[STEP 3] Processing and engineering features...")
        processed_data = self._process_all_data(cleaned_data)
        logger.info(f"Processed {len(processed_data)} datasets")
        
        # Step 4: Save processed data
        logger.info("\n[STEP 4] Saving processed data...")
        self._save_processed_data(processed_data)
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)
        
        return True
    
    def _clean_all_data(self, raw_data):
        """Clean all data types"""
        cleaned = {}
        
        for data_type, df in raw_data.items():
            logger.info(f"Cleaning {data_type} data...")
            
            if df.empty:
                logger.warning(f"Empty dataframe for {data_type}")
                continue
            
            # Apply type-specific cleaning
            if data_type == 'steps':
                df = self.cleaner.clean_steps(df)
            elif data_type == 'heart_rate':
                df = self.cleaner.clean_heart_rate(df)
            elif data_type == 'sleep':
                df = self.cleaner.clean_sleep(df)
            elif data_type == 'calories':
                df = self.cleaner.clean_calories(df)
            
            # Apply general cleaning
            df = self.cleaner.remove_duplicates(df)
            df = self.cleaner.handle_missing_values(df, method='interpolate')
            
            cleaned[data_type] = df
        
        return cleaned
    
    def _process_all_data(self, cleaned_data):
        """Process all data types"""
        processed = {}
        
        for data_type, df in cleaned_data.items():
            logger.info(f"Processing {data_type} data...")
            
            # Aggregate to daily
            if data_type == 'steps':
                df = self.processor.aggregate_daily(df, metric='sum')
            elif data_type == 'heart_rate':
                df = self.processor.aggregate_daily(df, metric='mean')
            elif data_type == 'sleep':
                df = self.processor.aggregate_daily(df, metric='sum')
            elif data_type == 'calories':
                df = self.processor.aggregate_daily(df, metric='sum')
            
            # Add features
            df = self.processor.calculate_moving_averages(df)
            df = self.processor.calculate_daily_change(df)
            df = self.processor.add_datetime_features(df)
            
            processed[data_type] = df
        
        return processed
    
    def _save_processed_data(self, processed_data):
        """Save processed data to SQL database"""
        engine = create_engine(f"sqlite:///{DATABASE_FILE}")
        logger.info(f"Connecting to database: {DATABASE_FILE}")
        
        for data_type, df in processed_data.items():
            logger.info(f"Saving {data_type} to SQL table...")
            # Use 'replace' to overwrite the table on each pipeline run
            df.to_sql(data_type, engine, if_exists='replace', index=False)
            logger.info(f"Saved {len(df)} records for {data_type} to table '{data_type}'")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fitness Analytics Pipeline")
    parser.add_argument('--days', type=int, default=DATA_RETENTION_DAYS, help='Days of data to retrieve')
    parser.add_argument('--save-intermediate', action='store_true', 
                       help='Save intermediate results')
    parser.add_argument('--local', action='store_true',
                       help='Use existing local data instead of fetching from API')
    
    args = parser.parse_args()
    
    pipeline = FitnessAnalyticsPipeline()
    success = pipeline.run_full_pipeline(
        days_back=args.days,
        save_intermediate=args.save_intermediate,
        fetch_new=not args.local
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
