import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import custom modules
from data_fetcher import fetch_stock_data, fetch_forex_data
from technical_indicators import calculate_indicators
import database as db
from scheduled_tasks import start_scheduled_tasks
from shared_state import initialize_session
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme, apply_chart_theme
from utils import format_currency

# Initialize the database
db.init_db()

# Start background tasks for sending alerts and cleanup
start_scheduled_tasks()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Forex & Stock Market Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
apply_theme()

# Initialize session state
user_prefs = initialize_session()

# Render sidebar
sidebar_state = render_sidebar()

# Application title and description
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.title("Forex & Stock Market Prediction System")
st.markdown("""
This application provides real-time market data analysis, technical indicators, 
and AI-powered predictions for forex pairs and stocks.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Main dashboard content
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.header("Market Dashboard")

# Create a card for market information
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
market_info_cols = st.columns([2, 1])

with market_info_cols[0]:
    st.subheader(f"Current Selection: {sidebar_state['display_name']}")
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <span style="font-weight: 600;">Market Type:</span> {sidebar_state['market_type']}
    </div>
    <div style="margin-bottom: 1rem;">
        <span style="font-weight: 600;">Time Period:</span> {sidebar_state['period']}
    </div>
    <div style="margin-bottom: 1rem;">
        <span style="font-weight: 600;">Interval:</span> {sidebar_state['interval']}
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Fetch and display current market data
try:
    with st.spinner('Fetching market data...'):
        # Fetch data based on market type
        if sidebar_state['market_type'] == "Forex":
            df = fetch_forex_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
        else:
            df = fetch_stock_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
            
        # Calculate technical indicators
        df = calculate_indicators(df)
    
    # Display latest price information
    if not df.empty:
        latest_data = df.iloc[-1]
        
        with market_info_cols[1]:
            price_change_pct = ((latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100)
            delta_color = "green" if price_change_pct >= 0 else "red"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Latest Close</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(latest_data['Close'])}</div>
                <div style="font-size: 1rem; color: {delta_color};">{price_change_pct:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display date range
            st.markdown(f"""
            <div style="margin-top: 1rem; text-align: center;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="font-weight: 600;">Data Range:</span> {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}
                </div>
                <div>
                    <span style="font-weight: 600;">Data Points:</span> {len(df)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main price chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader(f"{sidebar_state['display_name']} Price Chart")
    
    # Create a figure
    fig = go.Figure()
    
    # Add price candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add EMA if selected
    if sidebar_state['show_ema']:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA_20'],
            name='EMA 20',
            line=dict(color='#2196f3', width=2)
        ))
        
    # Update layout with theme
    fig.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Apply theme to chart
    fig = apply_chart_theme(fig)
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Quick Statistics")
    
    stats_cols = st.columns(4)
    
    # Calculate some basic statistics
    price_change = df['Close'].iloc[-1] - df['Close'].iloc[0]
    price_change_pct = (price_change / df['Close'].iloc[0]) * 100
    
    # Custom styled metrics
    with stats_cols[0]:
        delta_color = "green" if price_change_pct >= 0 else "red"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
            <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Price Change</div>
            <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(price_change)}</div>
            <div style="font-size: 0.9rem; color: {delta_color};">{price_change_pct:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_cols[1]:
        volatility = df['Close'].std()
        volatility_pct = (volatility / df['Close'].mean()) * 100
        volatility_status = "High" if volatility_pct > 5 else "Low" if volatility_pct < 1 else "Moderate"
        volatility_color = "red" if volatility_pct > 5 else "green" if volatility_pct < 1 else "orange"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
            <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Volatility (Std Dev)</div>
            <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{volatility:.2f}</div>
            <div style="font-size: 0.9rem; color: {volatility_color};">{volatility_status} ({volatility_pct:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_cols[2]:
        volume_value = f"{df['Volume'].mean():.0f}" if 'Volume' in df.columns else "N/A"
        volume_change = ((df['Volume'].iloc[-1] / df['Volume'].iloc[0]) - 1) * 100 if 'Volume' in df.columns and df['Volume'].iloc[0] > 0 else 0
        volume_color = "green" if volume_change > 10 else "red" if volume_change < -10 else "gray"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
            <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Volume (Avg)</div>
            <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{volume_value}</div>
            <div style="font-size: 0.9rem; color: {volume_color};">{volume_change:.2f}% change</div>
        </div>
        """, unsafe_allow_html=True) if 'Volume' in df.columns else st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
            <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Volume (Avg)</div>
            <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">N/A</div>
            <div style="font-size: 0.9rem; color: gray;">Not available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # RSI value
    with stats_cols[3]:
        if 'RSI' in df.columns:
            current_rsi = df['RSI'].iloc[-1]
            rsi_status = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
            rsi_color = "red" if current_rsi > 70 else "green" if current_rsi < 30 else "orange"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">RSI</div>
                <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{current_rsi:.2f}</div>
                <div style="font-size: 0.9rem; color: {rsi_color};">{rsi_status}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">RSI</div>
                <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">N/A</div>
                <div style="font-size: 0.9rem; color: gray;">Not calculated</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation section
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Navigation")
    
    # Create a more visually appealing navigation section
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
        <a href="Technical_Analysis" style="text-decoration: none; color: inherit; flex: 1; min-width: 200px;">
            <div style="background-color: var(--card-background); border-radius: 8px; padding: 1.5rem; box-shadow: 0 4px 6px var(--shadow-color); transition: transform 0.2s, box-shadow 0.2s; height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem; color: #0d6efd;">📊</div>
                <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: var(--text-color);">Technical Analysis</h3>
                <p style="margin: 0; color: var(--text-color); opacity: 0.8;">View detailed technical indicators and chart patterns</p>
            </div>
        </a>
        
        <a href="Price_Predictions" style="text-decoration: none; color: inherit; flex: 1; min-width: 200px;">
            <div style="background-color: var(--card-background); border-radius: 8px; padding: 1.5rem; box-shadow: 0 4px 6px var(--shadow-color); transition: transform 0.2s, box-shadow 0.2s; height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem; color: #6f42c1;">🔮</div>
                <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: var(--text-color);">Price Predictions</h3>
                <p style="margin: 0; color: var(--text-color); opacity: 0.8;">AI-powered price forecasts and trading signals</p>
            </div>
        </a>
        
        <a href="Alerts_Management" style="text-decoration: none; color: inherit; flex: 1; min-width: 200px;">
            <div style="background-color: var(--card-background); border-radius: 8px; padding: 1.5rem; box-shadow: 0 4px 6px var(--shadow-color); transition: transform 0.2s, box-shadow 0.2s; height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem; color: #fd7e14;">🔔</div>
                <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: var(--text-color);">Alerts Management</h3>
                <p style="margin: 0; color: var(--text-color); opacity: 0.8;">Set up and manage trading alerts</p>
            </div>
        </a>
        
        <a href="Settings" style="text-decoration: none; color: inherit; flex: 1; min-width: 200px;">
            <div style="background-color: var(--card-background); border-radius: 8px; padding: 1.5rem; box-shadow: 0 4px 6px var(--shadow-color); transition: transform 0.2s, box-shadow 0.2s; height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem; color: #20c997;">⚙️</div>
                <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: var(--text-color);">Settings</h3>
                <p style="margin: 0; color: var(--text-color); opacity: 0.8;">Configure application preferences</p>
            </div>
        </a>
    </div>
    
    <style>
    a:hover div {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px var(--shadow-color);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close the fade-in div

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")
