import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import uuid
from dotenv import load_dotenv

# Import custom modules
from data_fetcher import fetch_stock_data, fetch_forex_data
from technical_indicators import calculate_indicators
from model import train_model, make_predictions
from telegram_alerts import send_telegram_alert, format_alert_message, send_pending_alerts
from utils import format_currency, render_indicator_info
import database as db

# Initialize the database
db.init_db()

# Load environment variables
load_dotenv()

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
    
# Get or create user preferences
user_prefs = db.get_or_create_user_preferences(st.session_state['session_id'])

# Page configuration
st.set_page_config(
    page_title="Forex & Stock Market Prediction",
    page_icon="📈",
    layout="wide"
)

# Application title and description
st.title("Forex & Stock Market Prediction System")
st.markdown("""
This application provides real-time market data analysis, technical indicators, 
and AI-powered predictions for forex pairs and stocks.
""")

# Sidebar for inputs
st.sidebar.header("Settings")

# Market selection
market_type = st.sidebar.radio("Select Market", ["Forex", "Stock"])

if market_type == "Forex":
    # Forex pair selection
    forex_pairs = [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
        "USD/CAD", "USD/CHF", "NZD/USD"
    ]
    selected_symbol = st.sidebar.selectbox("Select Forex Pair", forex_pairs)
    # Convert to yfinance format
    symbol_mapping = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "USD/CHF": "USDCHF=X",
        "NZD/USD": "NZDUSD=X"
    }
    symbol = symbol_mapping[selected_symbol]
else:
    # Stock selection
    stock_options = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
    symbol = st.sidebar.selectbox("Select Stock", stock_options)

# Time period selection
period_options = {
    "1 Week": "1wk",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}
selected_period = st.sidebar.selectbox("Select Time Period", list(period_options.keys()))
period = period_options[selected_period]

# Interval selection
interval_options = {
    "1 Day": "1d",
    "1 Hour": "1h",
    "15 Minutes": "15m",
    "5 Minutes": "5m",
    "1 Minute": "1m"
}
selected_interval = st.sidebar.selectbox("Select Interval", list(interval_options.keys()))
interval = interval_options[selected_interval]

# Technical indicator selection
st.sidebar.header("Technical Indicators")
show_rsi = st.sidebar.checkbox("RSI (Relative Strength Index)", value=True)
show_macd = st.sidebar.checkbox("MACD (Moving Average Convergence Divergence)", value=True)
show_ema = st.sidebar.checkbox("EMA (Exponential Moving Average)", value=True)

# Model parameters
st.sidebar.header("Model Settings")
forecast_days = st.sidebar.slider("Forecast Days", 1, 30, 7)
train_button = st.sidebar.button("Train Model")

# Alert settings
st.sidebar.header("Alerts")
enable_alerts = st.sidebar.checkbox("Enable Telegram Alerts")
alert_threshold = st.sidebar.slider("Alert Threshold (%)", 0.0, 5.0, 1.0, 0.1)

# Main content
try:
    # Display loading message
    with st.spinner('Fetching market data...'):
        # Fetch data based on market type
        if market_type == "Forex":
            df = fetch_forex_data(symbol, period, interval)
            display_name = selected_symbol
        else:
            df = fetch_stock_data(symbol, period, interval)
            display_name = symbol
            
        # Calculate technical indicators
        df = calculate_indicators(df)
    
    # Main price chart
    st.subheader(f"{display_name} Price Chart")
    
    # Create a figure
    fig = go.Figure()
    
    # Add price candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    # Add EMA if selected
    if show_ema:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA_20'],
            name='EMA 20',
            line=dict(color='blue')
        ))
        
    # Update layout
    fig.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display technical indicators
    indicators_cols = st.columns(3)
    
    with indicators_cols[0]:
        if show_rsi:
            st.subheader("RSI")
            render_indicator_info("RSI", "Measures the magnitude of recent price changes to evaluate overbought or oversold conditions.")
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df.index, 
                y=df['RSI'], 
                name='RSI',
                line=dict(color='purple')
            ))
            
            # Add oversold/overbought lines
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            
            fig_rsi.update_layout(
                height=300,
                xaxis_title="Date",
                yaxis_title="RSI Value",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_rsi, use_container_width=True)
    
    with indicators_cols[1]:
        if show_macd:
            st.subheader("MACD")
            render_indicator_info("MACD", "Trend-following momentum indicator showing the relationship between two moving averages.")
            
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(
                x=df.index, 
                y=df['MACD'], 
                name='MACD',
                line=dict(color='blue')
            ))
            fig_macd.add_trace(go.Scatter(
                x=df.index, 
                y=df['MACD_Signal'], 
                name='Signal',
                line=dict(color='red')
            ))
            fig_macd.add_trace(go.Bar(
                x=df.index,
                y=df['MACD_Hist'],
                name='Histogram',
                marker_color=np.where(df['MACD_Hist'] >= 0, 'green', 'red')
            ))
            
            fig_macd.update_layout(
                height=300,
                xaxis_title="Date",
                yaxis_title="MACD Value"
            )
            
            st.plotly_chart(fig_macd, use_container_width=True)
    
    with indicators_cols[2]:
        if show_ema:
            st.subheader("EMA Comparison")
            render_indicator_info("EMA", "Exponential Moving Average gives more weight to recent prices, reacting more quickly to price changes.")
            
            fig_ema = go.Figure()
            fig_ema.add_trace(go.Scatter(
                x=df.index, 
                y=df['EMA_9'], 
                name='EMA 9',
                line=dict(color='orange')
            ))
            fig_ema.add_trace(go.Scatter(
                x=df.index, 
                y=df['EMA_20'], 
                name='EMA 20',
                line=dict(color='blue')
            ))
            fig_ema.add_trace(go.Scatter(
                x=df.index, 
                y=df['EMA_50'], 
                name='EMA 50',
                line=dict(color='green')
            ))
            
            fig_ema.update_layout(
                height=300,
                xaxis_title="Date",
                yaxis_title="Price"
            )
            
            st.plotly_chart(fig_ema, use_container_width=True)
    
    # Model predictions
    st.subheader("Price Prediction")
    
    # Model training and prediction
    model_container = st.container()
    
    with model_container:
        if train_button or 'model' in st.session_state:
            with st.spinner('Training model...'):
                if train_button or 'model' not in st.session_state:
                    model, scaler, features = train_model(df, forecast_days)
                    st.session_state['model'] = model
                    st.session_state['scaler'] = scaler
                    st.session_state['features'] = features
                
                # Make predictions
                forecast_dates, forecast_values, last_actual = make_predictions(
                    df, 
                    st.session_state['model'], 
                    st.session_state['scaler'], 
                    st.session_state['features'], 
                    forecast_days
                )
                
                # Show prediction chart
                fig_pred = go.Figure()
                
                # Actual price data
                fig_pred.add_trace(go.Scatter(
                    x=df.index[-30:],
                    y=df['Close'][-30:],
                    name='Actual Price',
                    line=dict(color='blue')
                ))
                
                # Predicted price data
                fig_pred.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=forecast_values,
                    name='Predicted Price',
                    line=dict(color='red', dash='dash')
                ))
                
                fig_pred.update_layout(
                    height=400,
                    xaxis_title="Date",
                    yaxis_title="Price",
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Calculate prediction metrics
                current_price = last_actual
                future_price = forecast_values[-1]
                price_change = future_price - current_price
                price_change_pct = (price_change / current_price) * 100
                
                # Display prediction summary
                metrics_cols = st.columns(4)
                metrics_cols[0].metric("Current Price", f"{format_currency(current_price)}")
                metrics_cols[1].metric("Predicted Price (in {} days)".format(forecast_days), 
                                       f"{format_currency(future_price)}")
                metrics_cols[2].metric("Predicted Change", 
                                       f"{format_currency(price_change)}", 
                                       f"{price_change_pct:.2f}%")
                
                # Trading signal based on prediction
                if price_change_pct > 1.0:
                    signal = "BUY"
                    signal_color = "green"
                elif price_change_pct < -1.0:
                    signal = "SELL"
                    signal_color = "red"
                else:
                    signal = "HOLD"
                    signal_color = "orange"
                
                metrics_cols[3].markdown(f"<h3 style='color:{signal_color};text-align:center'>{signal}</h3>", unsafe_allow_html=True)
                
                # Send alert if enabled and threshold exceeded
                if enable_alerts and abs(price_change_pct) >= alert_threshold:
                    # Save user alert preferences
                    db.save_user_preferences(
                        st.session_state['session_id'],
                        telegram_enabled=True,
                        alert_threshold=alert_threshold
                    )
                    
                    # Format the alert message
                    alert_message = format_alert_message(
                        symbol=display_name,
                        current_price=current_price,
                        predicted_price=future_price,
                        days=forecast_days,
                        signal=signal
                    )
                    
                    try:
                        # Send and store the alert
                        send_telegram_alert(
                            message=alert_message,
                            symbol=symbol,
                            market_type=market_type,
                            current_price=current_price,
                            predicted_price=future_price,
                            signal=signal
                        )
                        st.success("Alert sent to Telegram!")
                    except Exception as e:
                        # Store the alert even if sending fails
                        try:
                            db.store_alert(
                                symbol=symbol,
                                market_type=market_type,
                                current_price=current_price,
                                predicted_price=future_price,
                                signal=signal,
                                message=alert_message
                            )
                            st.warning(f"Failed to send Telegram alert: {str(e)}")
                            st.info("Alert saved in database and will be sent later.")
                        except Exception as db_error:
                            st.error(f"Failed to store alert: {str(db_error)}")
        else:
            st.info("Click 'Train Model' to generate predictions.")
            
    # Add a section for user preferences
    st.subheader("User Preferences")
    st.write("Your preferences are saved automatically and will be remembered next time you visit.")
    
    # Add favorite symbols
    if st.checkbox("Save current symbol as favorite", value=False):
        current_favorites = user_prefs.favorite_symbols.split(",") if user_prefs.favorite_symbols else []
        if symbol not in current_favorites:
            if not current_favorites[0]:  # Handle empty string case
                current_favorites = [symbol]
            else:
                current_favorites.append(symbol)
            db.save_user_preferences(st.session_state['session_id'], favorite_symbols=current_favorites)
            st.success(f"Added {display_name} to favorites")
    
    # Show favorites
    if user_prefs.favorite_symbols:
        st.write("Your favorite symbols:")
        favorite_list = user_prefs.favorite_symbols.split(",")
        for fav in favorite_list:
            if fav:  # Skip empty strings
                st.write(f"- {fav}")
                
    # Save time period preference
    db.save_user_preferences(
        st.session_state['session_id'],
        preferred_timeframe=period,
        preferred_interval=interval
    )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")
