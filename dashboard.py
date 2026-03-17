"""
Streamlit Dashboard for Fitness Analytics
Main dashboard for visualizing fitness data and predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_importer import FitnessDataImporter
from data_cleaner import FitnessDataCleaner
from data_processor import FitnessDataProcessor
from predictive_analytics import FitnessPredictor
from config import PROCESSED_DATA_DIR

# Page configuration
st.set_page_config(
    page_title="Fitness Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_data():
    """Load and cache fitness data"""
    try:
        importer = FitnessDataImporter()
        data = importer.import_all_data(days_back=30)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}


def clean_and_process_data(data_dict):
    """Clean and process raw data"""
    cleaner = FitnessDataCleaner()
    processor = FitnessDataProcessor()
    processed = {}
    
    if 'steps' in data_dict and not data_dict['steps'].empty:
        steps = cleaner.clean_steps(data_dict['steps'])
        steps = cleaner.remove_duplicates(steps)
        steps = processor.aggregate_daily(steps, metric='sum')
        steps = processor.calculate_moving_averages(steps)
        steps = processor.add_datetime_features(steps)
        processed['steps'] = steps
    
    if 'heart_rate' in data_dict and not data_dict['heart_rate'].empty:
        hr = cleaner.clean_heart_rate(data_dict['heart_rate'])
        hr = cleaner.remove_duplicates(hr)
        hr = processor.aggregate_daily(hr, metric='mean')
        hr = processor.calculate_moving_averages(hr)
        hr = processor.add_datetime_features(hr)
        processed['heart_rate'] = hr
    
    if 'sleep' in data_dict and not data_dict['sleep'].empty:
        sleep = cleaner.clean_sleep(data_dict['sleep'])
        sleep = cleaner.remove_duplicates(sleep)
        sleep = processor.aggregate_daily(sleep, metric='mean')
        sleep = processor.add_datetime_features(sleep)
        processed['sleep'] = sleep
    
    if 'calories' in data_dict and not data_dict['calories'].empty:
        calories = cleaner.clean_calories(data_dict['calories'])
        calories = cleaner.remove_duplicates(calories)
        calories = processor.aggregate_daily(calories, metric='sum')
        calories = processor.calculate_moving_averages(calories)
        calories = processor.add_datetime_features(calories)
        processed['calories'] = calories
    
    if 'weight' in data_dict and not data_dict['weight'].empty:
        weight = cleaner.clean_weight(data_dict['weight'])
        weight = cleaner.remove_duplicates(weight)
        weight = processor.aggregate_daily(weight, metric='mean')
        weight = processor.add_datetime_features(weight)
        processed['weight'] = weight
    
    return processed


def plot_metric(df, metric_name, value_col='value'):
    """Create interactive plot for a metric"""
    fig = go.Figure()
    
    # Add actual data
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[value_col],
        mode='lines',
        name='Actual',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add moving averages if available
    if 'ma_7' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ma_7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='#ff7f0e', width=1, dash='dash')
        ))
    
    if 'ma_30' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ma_30'],
            mode='lines',
            name='30-Day MA',
            line=dict(color='#2ca02c', width=1, dash='dash')
        ))
    
    fig.update_layout(
        title=f"{metric_name.title()} Over Time",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def plot_distribution(df, metric_name, value_col='value'):
    """Create distribution plot"""
    fig = px.histogram(
        df,
        x=value_col,
        nbins=30,
        title=f"{metric_name.title()} Distribution",
        labels={value_col: metric_name.title()},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def calculate_stats(df, value_col='value'):
    """Calculate summary statistics"""
    return {
        'current': df[value_col].iloc[-1],
        'mean': df[value_col].mean(),
        'median': df[value_col].median(),
        'min': df[value_col].min(),
        'max': df[value_col].max(),
        'std': df[value_col].std(),
        'trend_7d': ((df[value_col].iloc[-1] - df[value_col].iloc[-7]) / df[value_col].iloc[-7] * 100) if len(df) >= 7 else 0
    }


# Main app
def main():
    st.title("Fitness Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        days_back = st.slider("Days of History", 7, 90, 30)
        refresh = st.button("Refresh Data")
        
        if refresh:
            st.cache_resource.clear()
    
    # Load data
    st.info("Loading fitness data...")
    raw_data = load_data()
    
    if not raw_data:
        st.warning("No data available. Please ensure Google Fit credentials are configured.")
        return
    
    # Process data
    processed_data = clean_and_process_data(raw_data)
    
    if not processed_data:
        st.warning("No processed data available.")
        return
    
    # Summary metrics
    st.header("Summary Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if 'steps' in processed_data:
        stats = calculate_stats(processed_data['steps'])
        with col1:
            st.metric("Today's Steps", f"{int(stats['current']):,}", 
                     f"{stats['trend_7d']:.1f}% vs 7d avg")
    
    if 'heart_rate' in processed_data:
        stats = calculate_stats(processed_data['heart_rate'])
        with col2:
            st.metric("Avg Heart Rate", f"{int(stats['current'])} bpm",
                     f"{stats['trend_7d']:.1f}% vs 7d avg")
    
    if 'sleep' in processed_data:
        stats = calculate_stats(processed_data['sleep'])
        with col3:
            st.metric("Sleep (hrs)", f"{stats['current']:.1f}",
                     f"{stats['trend_7d']:.1f}% vs 7d avg")
    
    if 'calories' in processed_data:
        stats = calculate_stats(processed_data['calories'])
        with col4:
            st.metric("Calories Burned", f"{int(stats['current']):,}",
                     f"{stats['trend_7d']:.1f}% vs 7d avg")
    
    if 'weight' in processed_data:
        stats = calculate_stats(processed_data['weight'])
        with col5:
            st.metric("Weight (kg)", f"{stats['current']:.1f}",
                     f"{stats['trend_7d']:.1f}% vs 7d avg")
    
    st.markdown("---")
    
    # Detailed views
    st.header("Detailed Analysis")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Steps", "Heart Rate", "Sleep", "Calories", "Weight"
    ])
    
    with tab1:
        if 'steps' in processed_data:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_metric(processed_data['steps'], 'Steps'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_distribution(processed_data['steps'], 'Steps'),
                    use_container_width=True
                )
            
            # Stats
            stats = calculate_stats(processed_data['steps'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{int(stats['mean']):,}")
            col2.metric("Min", f"{int(stats['min']):,}")
            col3.metric("Max", f"{int(stats['max']):,}")
            col4.metric("Std Dev", f"{int(stats['std']):,.0f}")
        else:
            st.info("No steps data available")
    
    with tab2:
        if 'heart_rate' in processed_data:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_metric(processed_data['heart_rate'], 'Heart Rate'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_distribution(processed_data['heart_rate'], 'Heart Rate'),
                    use_container_width=True
                )
            
            # Stats
            stats = calculate_stats(processed_data['heart_rate'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{int(stats['mean'])} bpm")
            col2.metric("Min", f"{int(stats['min'])} bpm")
            col3.metric("Max", f"{int(stats['max'])} bpm")
            col4.metric("Std Dev", f"{stats['std']:.1f}")
        else:
            st.info("No heart rate data available")
    
    with tab3:
        if 'sleep' in processed_data:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_metric(processed_data['sleep'], 'Sleep'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_distribution(processed_data['sleep'], 'Sleep'),
                    use_container_width=True
                )
            
            # Stats
            stats = calculate_stats(processed_data['sleep'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{stats['mean']:.1f} hrs")
            col2.metric("Min", f"{stats['min']:.1f} hrs")
            col3.metric("Max", f"{stats['max']:.1f} hrs")
            col4.metric("Std Dev", f"{stats['std']:.2f}")
        else:
            st.info("No sleep data available")
    
    with tab4:
        if 'calories' in processed_data:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_metric(processed_data['calories'], 'Calories'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_distribution(processed_data['calories'], 'Calories'),
                    use_container_width=True
                )
            
            # Stats
            stats = calculate_stats(processed_data['calories'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{int(stats['mean']):,}")
            col2.metric("Min", f"{int(stats['min']):,}")
            col3.metric("Max", f"{int(stats['max']):,}")
            col4.metric("Std Dev", f"{int(stats['std']):,.0f}")
        else:
            st.info("No calories data available")
    
    with tab5:
        if 'weight' in processed_data:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_metric(processed_data['weight'], 'Weight'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_distribution(processed_data['weight'], 'Weight'),
                    use_container_width=True
                )
            
            # Stats
            stats = calculate_stats(processed_data['weight'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{stats['mean']:.1f} kg")
            col2.metric("Min", f"{stats['min']:.1f} kg")
            col3.metric("Max", f"{stats['max']:.1f} kg")
            col4.metric("Std Dev", f"{stats['std']:.2f}")
        else:
            st.info("No weight data available")
    
    
    st.markdown("---")
    st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
