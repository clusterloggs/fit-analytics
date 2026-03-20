"""
Streamlit Dashboard for Fitness Analytics
Main dashboard for visualizing fitness data and predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="Fitness Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Late import to use updated path
from config import DATABASE_FILE

logger = logging.getLogger(__name__)

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


@st.cache_data
def load_data_from_db():
    """Load all processed data tables from the SQLite database."""
    if not os.path.exists(DATABASE_FILE):
        st.error(f"Database not found at {DATABASE_FILE}. Please run the main pipeline first (`python pipeline.py`).")
        return None
    
    try:
        engine = create_engine(f"sqlite:///{DATABASE_FILE}")
        with engine.connect() as connection:
            inspector = sqlalchemy.inspect(engine)
            table_names = inspector.get_table_names()
            
            if not table_names:
                st.warning("Database is empty. Please run the pipeline to populate it.")
                return {}
            
            data = {tbl: pd.read_sql_table(tbl, connection, parse_dates=['date']) for tbl in table_names}
            logger.info(f"Successfully loaded tables: {', '.join(data.keys())}")
            st.success(f"Loaded data from tables: {', '.join(table_names)}")
            return data
    except Exception as e:
        st.error(f"Failed to load data from database: {e}")
        return None


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
        st.header("Dashboard Controls")
        st.info("Run `pipeline.py` to update the data.")
        if st.button("Reload Data from DB"):
            st.cache_data.clear()
            st.rerun()
    
    # Load data
    st.info("Loading processed data from database...")
    processed_data = load_data_from_db()
    
    if processed_data is None:
        return
    
    if not processed_data:
        st.warning("No data available to display. Ensure the pipeline has been run successfully.")
        return
    
    # Summary metrics
    st.header("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    st.markdown("---")
    
    # Detailed views
    st.header("Detailed Analysis")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Steps", "Heart Rate", "Sleep", "Calories"
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
    
    
    st.markdown("---")
    st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
