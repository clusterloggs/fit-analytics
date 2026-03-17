# Quick Start Guide - Fitness Analytics

## ✅ Project Setup Complete

Your fitness analytics project is ready with a complete workflow for Google Fit data collection, cleaning, processing, and predictive analytics.

## 📋 What's Included

### 1. **Data Pipeline** (`pipeline.py`)
- Orchestrates the complete workflow
- Imports data from Google Fit
- Cleans and validates data
- Engineers features
- Trains predictive models
- Logs all operations

### 2. **Data Modules** (`src/`)
- `google_fit_client.py` - Google Fit API integration
- `data_importer.py` - Imports steps, heart rate, sleep, calories, weight
- `data_cleaner.py` - Validation, outlier removal, duplicate handling
- `data_processor.py` - Feature engineering (moving averages, trends, datetime features)
- `predictive_analytics.py` - Linear regression & Random Forest models

### 3. **Interactive Dashboard** (`dashboard.py`)
- Real-time metrics visualization
- Time series analysis with moving averages
- Distribution charts
- 7-day forecasts
- Built with Streamlit + Plotly

### 4. **Directory Structure**
```
├── data/raw/          ← CSV files imported from Google Fit
├── data/processed/    ← Cleaned and processed data
├── notebooks/         ← Space for your Jupyter analysis
└── src/              ← Python modules
```

## 🚀 Getting Started

### Step 1: Set Up Google Fit Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **Google Fit API**
4. Create **OAuth 2.0 Desktop Application** credentials
5. Download the JSON file
6. Save as `credentials.json` in the project root

### Step 2: Run the Data Pipeline
```bash
# First time (import 30 days)
python pipeline.py

# Import 90 days of data
python pipeline.py --days 90

# Save intermediate results
python pipeline.py --save-intermediate
```

The pipeline will:
- Authenticate with Google Fit
- Import your fitness data
- Clean and validate it
- Engineer features
- Train models
- Save results to `data/processed/`
- Log everything to `fitness_analytics.log`

### Step 3: Launch the Dashboard
```bash
streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser to see:
- Summary metrics (today's activity)
- Detailed time series charts
- Trend analysis
- 7-day forecasts

## 📊 Data Collected

- **Steps**: Daily step count
- **Heart Rate**: Average, min, max bpm
- **Sleep**: Sleep duration
- **Calories**: Energy burned
- **Weight**: Body weight

## 🔧 Key Features

### Cleaning
- Removes physiologically impossible values
- Handles missing data
- Detects and removes duplicates
- Validates data quality

### Processing
- Daily aggregation (sum for steps/calories, mean for HR/weight)
- 7, 14, 30-day moving averages
- Daily change and % change
- Datetime features (day of week, month, season, weekday/weekend)
- Lag features for time-series models

### Analytics
- Trend identification (uptrend/downtrend/neutral)
- Momentum calculation
- Distribution analysis
- Weekly summaries

### Predictions
- 7-day linear regression forecasts
- Model performance metrics (R² scores)
- Historical vs. predicted comparison

## 📝 Log File
All pipeline runs are logged to `fitness_analytics.log` with timestamps

## 🎯 Next Steps

1. **Configure credentials.json** → Essential for data import
2. **Run pipeline** → Test data collection
3. **Launch dashboard** → Explore your data
4. **Customize analysis** → Edit specific metrics/windows in `config.py`

## 🛠️ Customization

Edit `config.py` to:
- Change data retention period (default: 365 days)
- Adjust prediction window (default: 7 days)
- Modify moving average windows (default: 7, 14, 30)
- Change batch sizes for API calls

## 📚 File Structure
```
fit analytics/
├── config.py                      # Configuration
├── pipeline.py                    # Main workflow
├── dashboard.py                   # Streamlit dashboard
├── setup.py                       # Verification utilities
├── requirements.txt               # Dependencies
├── README.md                      # Full documentation
├── QUICKSTART.md                  # This file
├── .github/
│   └── copilot-instructions.md   # Development guidelines
├── src/                          # Python modules
│   ├── google_fit_client.py
│   ├── data_importer.py
│   ├── data_cleaner.py
│   ├── data_processor.py
│   └── predictive_analytics.py
└── data/
    ├── raw/                      # Downloaded data
    └── processed/                # Cleaned data
```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
→ Run: `pip install -r requirements.txt`

### Google Fit authentication fails
→ Verify `credentials.json` is in project root
→ Ensure Google Fit API is enabled in Cloud Console
→ Delete `token.pickle` to re-authenticate

### No data imports
→ Check Google Fit has activity data
→ Verify internet connectivity
→ Review `fitness_analytics.log` for errors

### Dashboard is slow
→ Reduce date range in sidebar
→ Use smaller `--days` parameter in pipeline

## 💡 Tips
- Start with 7-14 days of data for quick testing
- Use `--save-intermediate` to inspect raw data
- Check logs to understand data quality issues
- Modify metric windows in `config.py` for your preferences

## 📖 Full Documentation
See `README.md` for comprehensive documentation including:
- Detailed API documentation
- Data type specifications
- Advanced configuration
- Future enhancement roadmap

---

**Ready to analyze your fitness data?** Start with `Step 1: Set Up Google Fit Credentials` above! 💪
