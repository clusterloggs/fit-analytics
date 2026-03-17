# Fitness Analytics

Fitness Analytics is a Python-based analytics platform that integrates with Google Fit to automatically collect, clean, process, and forecast personal fitness metrics. It provides a complete data pipeline with automated quality checks, advanced feature engineering, predictive models, and an interactive web dashboard for visualizing trends and predictions across steps, heart rate, sleep, calories, and weight.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Usage](#usage)
- [Configuration](#configuration)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

### Prerequisites

- **Python 3.7+** (tested with 3.13)
- **Google Account** with daily activity in Google Fit
- **Google Cloud Project** with Fit API enabled

### 1. Setup Google Fit Credentials

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Fit API**
4. Navigate to **Credentials** → **Create Credentials** → **OAuth 2.0 Desktop Application**
5. Download the JSON file as `credentials.json`
6. Place `credentials.json` in the project root

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Data Pipeline

```bash
# Retrieve and process 30 days of data
python pipeline.py

# Retrieve 90 days of data
python pipeline.py --days 90

# Save intermediate raw and processed data
python pipeline.py --save-intermediate
```

**Output**: Processed datasets saved to `data/processed/`, logs to `fitness_analytics.log`

### 4. Launch the Dashboard

```bash
streamlit run dashboard.py
```

Open your browser to `http://localhost:8501`

## Features

### Data Collection & Ingestion
- **Automated Sync**: Connects to Google Fit API with OAuth 2.0 authentication
- **Multiple Metrics**: Collects steps, heart rate, sleep, calories, and weight
- **Configurable Time Window**: Pull any date range of historical data

### Data Quality & Cleaning
- **Outlier Detection**: Removes physiologically impossible values (e.g., >50k steps/day, <30 bpm HR)
- **Duplicate Removal**: Identifies and removes duplicate records
- **Missing Data Handling**: Interpolates gaps intelligently
- **Type-Specific Validation**: Applies metric-appropriate range checks

### Analytics & Insights
- **7, 14, and 30-day Moving Averages**: Smooths trends and reduces noise
- **Trend Analysis**: Identifies uptrends, downtrends, and momentum
- **Distribution Analysis**: Histograms and statistical summaries
- **Temporal Features**: Day-of-week patterns, seasonality, weekly aggregates

### Forecasting
- **Linear Regression Models**: Fast, interpretable 7-day forecasts
- **Random Forest Models**: Advanced pattern capture (optional)
- **Model Evaluation**: R² scores for accuracy assessment
- **Confidence Metrics**: Track model performance over time

### Dashboard
- **Interactive Visualizations**: Plotly charts with hover details and drill-down
- **Real-Time Metrics**: Current values, weekly trends, performance indicators
- **Multi-Tab Interface**: Separate views for each fitness metric
- **Forecast Charts**: Historical data overlaid with 7-day predictions

## Architecture

### System Design

Fitness Analytics follows a **modular data pipeline architecture** with clear separation of concerns:

```
Google Fit API
      ↓
[Import] → Raw CSV
      ↓
[Clean] → Validated Data
      ↓
[Process] → Features (MA, trends, datetime)
      ↓
[Predict] → Models & Forecasts
      ↓
[Dashboard] → Interactive Viz
```

### Key Components

| Component | Purpose | Key Trade-offs |
|-----------|---------|-----------------|
| `google_fit_client.py` | API authentication and data retrieval | Simple OAuth 2.0, no rate limit handling |
| `data_cleaner.py` | Data validation and quality checks | Type-specific rules, assumes daily aggregates |
| `data_processor.py` | Feature engineering and transformation | Interpolates missing values, creates lag features |
| `predictive_analytics.py` | Model training and forecasting | Linear regression (fast, simple) and Random Forest (complex but slower) |
| `pipeline.py` | Orchestrates the complete workflow | Stateful execution, all-or-nothing approach |
| `dashboard.py` | Web-based visualization | In-memory caching, Streamlit compute-on-demand |

### Technical Decisions

**Why Linear Regression for Forecasting?**
- Fast training and prediction (<1s)
- Interpretable coefficients
- Suitable for typical 7-day windows
- Random Forest is available for complex patterns

**Why Daily Aggregation?**
- Simplifies analysis and visualization
- Reduces noise from intra-day variations
- Standard practice for fitness analytics
- Supports consistent moving average windows

**Why Streamlit?**
- Rapid prototyping with zero frontend code
- Built-in caching and reactivity
- Excellent Plotly integration
- Easy deployment to cloud platforms

## Usage

### Common Workflows

#### Analyze Recent Activity (7 days)

```bash
python pipeline.py --days 7
streamlit run dashboard.py
```

#### Monthly Analysis

```bash
python pipeline.py --days 30 --save-intermediate
```

This saves both raw and processed data to CSV for external analysis.

#### Inspect Raw Data Quality

```bash
python pipeline.py --days 14 --save-intermediate
# Check data/raw/*.csv for original Google Fit data
```

### Dashboard Navigation

1. **Summary Metrics** - Scan top metrics and 7-day trends
2. **Steps Tab** - View step count trends, distribution, forecast
3. **Heart Rate Tab** - Monitor HR patterns and averages
4. **Sleep Tab** - Track sleep duration and consistency
5. **Calories Tab** - Analyze energy expenditure
6. **Weight Tab** - Monitor body weight trends

Use the sidebar to adjust the historical data window and refresh on-demand.

### Programmatic Access

```python
from src.data_importer import FitnessDataImporter
from src.data_cleaner import FitnessDataCleaner
from src.data_processor import FitnessDataProcessor

# Import data
importer = FitnessDataImporter()
raw_data = importer.import_all_data(days_back=30)

# Clean data
cleaner = FitnessDataCleaner()
steps = cleaner.clean_steps(raw_data['steps'])

# Process
processor = FitnessDataProcessor()
features = processor.calculate_moving_averages(steps)
features = processor.add_datetime_features(features)

print(features.head())
```

## Configuration

Edit `config.py` to customize pipeline behavior:

```python
# Data retention and processing
DATA_RETENTION_DAYS = 365          # Keep 1 year of history
PREDICTION_DAYS_AHEAD = 7          # Forecast window
MOVING_AVERAGE_WINDOW = 7          # Default MA window
BATCH_SIZE = 1000                  # API request batch size

# Google Fit API scopes
GOOGLE_FIT_SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    # ... other scopes
]
```

### Customization Examples

**Extend forecast window to 14 days:**
```python
PREDICTION_DAYS_AHEAD = 14
```

**Use 14, 30-day moving averages instead of default:**
- Modify the windows list in `data_processor.py` `calculate_moving_averages()` method

**Change data retention to 2 years:**
```python
DATA_RETENTION_DAYS = 730
```

## Monitoring & Troubleshooting

### Logging & Diagnostics

All pipeline runs are logged to `fitness_analytics.log`:

```bash
# View recent execution
tail -f fitness_analytics.log

# Check for errors
grep ERROR fitness_analytics.log

# Summary statistics
grep "Imported\|Cleaned\|Processed" fitness_analytics.log
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: credentials.json` | OAuth file missing | Download from Google Cloud Console and place in project root |
| `HTTP 401 Unauthorized` | Invalid/expired credentials | Delete `token.pickle` to re-authenticate on next run |
| `No data imports` | Google Fit has no recorded activity | Ensure device is syncing to Google Fit |
| `Dashboard loads slowly` | Large date range | Reduce `--days` parameter, use sidebar to filter |
| `Model R² score is <0.5` | Insufficient data or high variance | Collect more data, check for anomalies in raw CSV |

### Data Quality Checks

After running the pipeline, verify data integrity:

```bash
# Inspect raw data
head -20 data/raw/steps_*.csv

# Check for excessive nulls
grep "^,," data/processed/steps_*.csv | wc -l

# Validate dates are continuous
python -c "import pandas as pd; \
df = pd.read_csv('data/processed/steps_*.csv'); \
print(f'Date range: {df.date.min()} to {df.date.max()}')"
```

### Performance Tuning

For dashboards with >1 year of data:

1. **Reduce Historical Window**: Use sidebar to show last 90 days
2. **Cache Results**: Dashboard caches data automatically; use "Refresh" button sparingly
3. **Adjust Sample Rate**: Modify `plotly` chart `scattergl` for faster rendering (in `dashboard.py`)
4. **Batch Processing**: Split large imports with `--days` parameter

## Contributing

We welcome contributions! To contribute:

1. **Report Issues**: File bugs and feature requests in the issue tracker
2. **Submit PRs**: 
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/my-feature`)
   - Add tests for new functionality
   - Ensure all tests pass
   - Open a pull request with a clear description

3. **Development Setup**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Code Standards**:
   - Use type hints for function parameters
   - Add docstrings to all functions
   - Follow PEP 8 style guide
   - Log operations with `logging` module

### Roadmap

**Planned Features**:
- [ ] Apple Health integration
- [ ] Multi-user support
- [ ] Anomaly detection and alerts
- [ ] Goal tracking and notifications
- [ ] PDF report generation
- [ ] Mobile app integration
- [ ] Advanced statistical tests
- [ ] Social comparison features

## License

Fitness Analytics is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute this software for personal or commercial use, provided you include the license and copyright notice.

## Support & Resources

- **Documentation**: See `QUICKSTART.md` for quick reference, `ARCHITECTURE.md` for system design
- **Issues**: File bugs and feature requests on GitHub
- **Questions**: Open a discussion or check existing issues

---

**Questions about the code?** Check out `ARCHITECTURE.md` for a detailed technical overview of the data pipeline.

**Not sure how to set up credentials?** See the **Quick Start** section above or our [setup guide](QUICKSTART.md).

**Want to extend the system?** See the contributing section—we'd love your contributions!
