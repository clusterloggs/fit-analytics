# Fitness Analytics Workflow Architecture

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GOOGLE FIT API                                │
│              (Steps, Heart Rate, Calories, Activity, Move Min)           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ [STEP 1] DATA IMPORT (google_fit_client.py + data_importer.py)      │
│                                                                       │
│  • OAuth 2.0 authentication                                          │
│  • Retrieve daily aggregates for 5 data types                       │
│  • Save raw data to data/raw/*.csv                                  │
│  • Handle API rate limits & errors                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ [STEP 2] DATA CLEANING (data_cleaner.py)                            │
│                                                                       │
│  Steps Data:         Remove negative, > 50,000/day outliers        │
│  Heart Rate:         Keep 30-250 bpm range                         │
│  Sleep:              Keep 0-12 hour range                          │
│  Calories:           Remove negative, > 10,000/day                 │
│  Weight:             Keep 30-250 kg range                          │
│                                                                       │
│  All data:           Remove duplicates                              │
│                      Interpolate missing values                     │
│                      Aggregate to daily level                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ [STEP 3] FEATURE ENGINEERING (data_processor.py)                    │
│                                                                       │
│  Aggregation:        Sum (steps, calories), Mean (HR, weight)       │
│  Time-Series:        7, 14, 30-day moving averages                  │
│  Change Metrics:     Daily change, % change                         │
│  Date Features:      Day of week, week/month, is_weekend            │
│  Stats:              Rolling std dev                                │
│  Lag Features:       1, 7, 14-day lags (for models)                │
│                                                                       │
│  Output:             Enhanced dataset with 20+ features             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
               ┌─────────────┴──────────────┐
               ▼                            ▼
        [STEP 4a] MODELS          [STEP 4b] ANALYSIS
        (predictive_analytics.py)  (computed on-demand)
               │                            │
               ├─Linear Regression          ├─Descriptive Stats
               │ (7-day forecast)           │ (mean, median, std)
               │                            │
               ├─Random Forest              ├─Trend Analysis
               │ (complex patterns)         │ (uptrend/downtrend)
               │                            │
               └─Model Evaluation           └─Distribution Analysis
                 (R² scores)
               │
               ▼
        Saved to models/
        (in memory during runtime)
               │
               └──────────────────┐
                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│ [STEP 5] DASHBOARD VISUALIZATION (dashboard.py)                    │
│                                                                     │
│  Summary Metrics:    Current values, 7-day trends                 │
│  Time Series:        Interactive Plotly charts                    │
│  Distributions:      Histograms of each metric                    │
│  Forecasts:          7-day predictions with models               │
│  Performance:        Model accuracy metrics (R²)                  │
│                                                                     │
│  Framework:          Streamlit + Plotly                           │
│  Real-time:          Computation on view                          │
│  Interactive:        Filters, date ranges                         │
└────────────────────────────────────────────────────────────────────┘

```

## Process Execution Flow

### Command: `python pipeline.py`

```
1. Initialize Pipeline
   ├─ Create importer, cleaner, processor, predictor
   └─ Setup logging to fitness_analytics.log

2. Data Import (1-5 minutes)
   ├─ Authenticate with Google
   ├─ Request data for each type
   ├─ Parse API responses
   └─ Save raw CSVs → data/raw/

3. Data Cleaning (< 1 minute)
   ├─ Type-specific validation
   │  ├─ Remove outliers
   │  ├─ Validate ranges
   │  └─ Handle edge cases
   ├─ General cleaning
   │  ├─ Remove duplicates
   │  └─ Interpolate missing
   └─ Report statistics

4. Data Processing (< 1 minute)
   ├─ Aggregate to daily level
   ├─ Calculate features
   │  ├─ Moving averages
   │  ├─ Daily changes
   │  └─ Datetime features
   └─ Create processed CSVs

5. Model Training (< 1 minute)
   ├─ Train linear regression
   ├─ Train random forest (optional)
   └─ Calculate R² scores

6. Save Results
   ├─ Processed data → data/processed/
   ├─ Models → memory (runtime)
   └─ Logs → fitness_analytics.log

```

### Command: `streamlit run dashboard.py`

```
1. Initialize/Cache Resources
   ├─ Load processed data
   ├─ Load trained models
   └─ Prepare for visualization

2. Render UI
   ├─ Sidebar (settings, date range)
   ├─ Summary metrics row
   ├─ Tabbed views
   │  ├─ Steps chart + stats
   │  ├─ Heart Rate chart + stats
   │  ├─ Sleep chart + stats
   │  ├─ Calories chart + stats
   │  └─ Weight chart + stats
   └─ Forecast section

3. Interactive Features
   ├─ Date range selection
   ├─ Refresh data button
   ├─ Chart hover interactions
   └─ Chart zoom/pan

4. Live Updates
   ├─ Charts update real-time
   ├─ Metrics recalculate
   └─ Cache refreshes on demand

```

## Data Storage

### Raw Data (`data/raw/`)
```
steps_20250315_143022.csv
├─ timestamp (ms)
├─ value (step count)
├─ data_type
├─ date
└─ time

[Similar for heart_rate, sleep, calories, weight]
```

### Processed Data (`data/processed/`)
```
steps_processed_20250315_143022.csv
├─ date
├─ value (daily sum)
├─ ma_7 (7-day moving avg)
├─ ma_14
├─ ma_30
├─ daily_change
├─ pct_change
├─ day_of_week
├─ week_of_year
├─ month
├─ day
├─ quarter
└─ is_weekend

[Similar for other metrics, minus moving averages for weight]
```

## Configuration Parameters

In `config.py`:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `DATA_RETENTION_DAYS` | 365 | Keep 1 year of data |
| `PREDICTION_DAYS_AHEAD` | 7 | Forecast 7 days ahead |
| `MOVING_AVERAGE_WINDOW` | 7 | Default 7-day MA |
| `BATCH_SIZE` | 1000 | API request batch size |

## Error Handling

- **API Errors**: Logged with retry mechanism
- **Missing Data**: Interpolated or reported
- **Invalid Credentials**: Prompts for re-authentication
- **Data Quality**: Validated with type-specific rules

## Performance

| Operation | Duration | Notes |
|-----------|----------|-------|
| Data Import | 1-5 min | Depends on Google Fit server |
| Data Cleaning | <1 min | For typical data volume |
| Processing | <1 min | Feature engineering |
| Model Training | <1 min | Linear regression |
| Dashboard Load | 2-5 sec | First load, then cached |

## Extensibility

### Add New Data Types
1. Implement in `google_fit_client.py`
2. Add cleaner method in `data_cleaner.py`
3. Add processor logic in `data_processor.py`
4. Add tab in `dashboard.py`

### Add New Features
1. Implement in `data_processor.py`
2. Use in models via `predictive_analytics.py`
3. Visualize in `dashboard.py`

### Add New Models
1. Create in `predictive_analytics.py`
2. Train in pipeline function
3. Integrate into dashboard predictions

---

**This architecture ensures**: data quality → feature richness → accurate models → insightful visualizations
