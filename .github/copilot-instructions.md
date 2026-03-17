# Fit Analytics Copilot Instructions

## Project Overview
Fitness analytics platform integrating Google Fit data with predictive analytics and interactive dashboard.

## Key Files & Purposes
- `config.py` - Configuration and paths
- `pipeline.py` - Main orchestrator (import → clean → process → predict)
- `dashboard.py` - Streamlit dashboard
- `src/google_fit_client.py` - Google Fit API integration
- `src/data_importer.py` - Data import to CSV
- `src/data_cleaner.py` - Data validation and cleaning
- `src/data_processor.py` - Feature engineering
- `src/predictive_analytics.py` - ML models and forecasting

## Quick Start
1. Install: `pip install -r requirements.txt`
2. Add `credentials.json` (Google Cloud OAuth)
3. Run pipeline: `python pipeline.py`
4. Launch dashboard: `streamlit run dashboard.py`

## Development Guidelines
- Keep data modules modular and independently testable
- Log all operations to `fitness_analytics.log`
- Use type hints for function parameters
- Add error handling with try/except blocks
- Update README for any new features

## Testing Commands
```bash
# Test pipeline with minimal data
python pipeline.py --days 7

# Test dashboard locally
streamlit run dashboard.py

# Check logs
tail fitness_analytics.log
```
