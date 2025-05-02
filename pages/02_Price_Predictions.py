"""
Price Predictions page for the Forex & Stock Market Prediction System.
This page provides AI-powered price forecasts and trading signals.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data_fetcher import fetch_stock_data, fetch_forex_data
from technical_indicators import calculate_indicators
from model import train_model, make_predictions
from utils import format_currency
from shared_state import initialize_session
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme, apply_chart_theme
import database as db
from telegram_alerts import format_alert_message, send_telegram_alert

# Page configuration
st.set_page_config(
    page_title="Price Predictions - Forex & Stock Market Prediction",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
apply_theme()

# Initialize session state
user_prefs = initialize_session()

# Render sidebar
sidebar_state = render_sidebar()

# Page title
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.title("Price Predictions")
st.markdown("""
Get AI-powered price forecasts for your selected market.
Our machine learning model analyzes historical data and technical indicators to predict future price movements.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Model settings
st.sidebar.header("Model Settings")
forecast_days = st.sidebar.slider("Forecast Days", 1, 30, 7)
st.session_state['forecast_days'] = forecast_days

# Alert settings
st.sidebar.header("Alert Settings")
enable_alerts = st.sidebar.checkbox("Enable Telegram Alerts", value=st.session_state.get('enable_alerts', False))
st.session_state['enable_alerts'] = enable_alerts

alert_threshold = st.sidebar.slider("Alert Threshold (%)", 0.0, 5.0, 1.0, 0.1)
st.session_state['alert_threshold'] = alert_threshold

# Main content
try:
    # Fetch data
    with st.spinner('Fetching market data...'):
        # Fetch data based on market type
        if sidebar_state['market_type'] == "Forex":
            df = fetch_forex_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
        else:
            df = fetch_stock_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
            
        # Calculate technical indicators
        df = calculate_indicators(df)
    
    # Model training section
    st.header("Model Training")
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("""
        Our prediction model uses a Random Forest algorithm trained on historical price data and technical indicators.
        The model analyzes patterns in price movements, volume, and various technical indicators to forecast future prices.
        """)
        
        # Model features
        st.subheader("Model Features")
        features = [
            "Historical price data (Open, High, Low, Close)",
            "Price momentum (Rate of change)",
            "Technical indicators (RSI, MACD, EMA)",
            "Price volatility",
            "Lagged price values"
        ]
        
        for feature in features:
            st.write(f"- {feature}")
    
    with col2:
        # Train button with styling
        st.markdown("""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding-top: 2rem;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🧠</div>
                <div style="opacity: 0.8; margin-bottom: 1rem;">Click to train the AI model</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        train_button = st.button("Train Model", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if train_button:
        st.session_state['train_requested'] = True
    
    # Model training and prediction
    if train_button or 'model' in st.session_state:
        with st.spinner('Training model and generating predictions...'):
            if train_button or 'model' not in st.session_state:
                # Train the model
                model, scaler, features = train_model(df, forecast_days)
                st.session_state['model'] = model
                st.session_state['scaler'] = scaler
                st.session_state['features'] = features
                st.session_state['last_trained_symbol'] = sidebar_state['symbol']
                st.session_state['last_trained_period'] = sidebar_state['period']
            
            # Check if we need to retrain (if symbol or period changed)
            elif (st.session_state.get('last_trained_symbol') != sidebar_state['symbol'] or 
                  st.session_state.get('last_trained_period') != sidebar_state['period']):
                # Retrain the model
                model, scaler, features = train_model(df, forecast_days)
                st.session_state['model'] = model
                st.session_state['scaler'] = scaler
                st.session_state['features'] = features
                st.session_state['last_trained_symbol'] = sidebar_state['symbol']
                st.session_state['last_trained_period'] = sidebar_state['period']
            
            # Make predictions
            forecast_dates, forecast_values, last_actual = make_predictions(
                df, 
                st.session_state['model'], 
                st.session_state['scaler'], 
                st.session_state['features'], 
                forecast_days
            )
        
        # Display model performance metrics
        st.subheader("Model Performance")
        
        # Display metrics
        metrics_cols = st.columns(2)
        
        with metrics_cols[0]:
            # For RandomForest, we can't directly access the training score this way
            # Instead, we'll show a placeholder or calculate it differently
            st.metric("Model Type", "Random Forest")
        
        with metrics_cols[1]:
            # Show the number of features used
            st.metric("Feature Count", f"{len(st.session_state['features'])}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Price Prediction Results
        st.header("Price Prediction Results")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Show prediction chart
        st.subheader(f"{sidebar_state['display_name']} Price Forecast")
        
        fig_pred = go.Figure()
        
        # Actual price data (last 30 days)
        fig_pred.add_trace(go.Scatter(
            x=df.index[-30:],
            y=df['Close'][-30:],
            name='Historical Price',
            line=dict(color='#2196f3', width=2)
        ))
        
        # Predicted price data
        fig_pred.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            name='Predicted Price',
            line=dict(color='#ff9800', width=2, dash='dash')
        ))
        
        # Add confidence interval (simplified)
        upper_bound = [val * 1.05 for val in forecast_values]  # 5% above prediction
        lower_bound = [val * 0.95 for val in forecast_values]  # 5% below prediction
        
        fig_pred.add_trace(go.Scatter(
            x=forecast_dates,
            y=upper_bound,
            fill=None,
            mode='lines',
            line_color='rgba(255, 152, 0, 0.1)',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig_pred.add_trace(go.Scatter(
            x=forecast_dates,
            y=lower_bound,
            fill='tonexty',
            mode='lines',
            line_color='rgba(255, 152, 0, 0.1)',
            line=dict(width=0),
            name='Confidence Interval (±5%)'
        ))
        
        # Add a vertical line at the current date
        last_date = df.index[-1]
        fig_pred.add_vline(
            x=last_date, 
            line_width=1, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Today",
            annotation_position="top right"
        )
        
        # Update layout with our theme
        fig_pred.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified"
        )
        
        # Apply our chart theme
        fig_pred = apply_chart_theme(fig_pred)
        
        st.plotly_chart(fig_pred, use_container_width=True)
        
        # Calculate prediction metrics
        current_price = last_actual
        future_price = forecast_values[-1]
        price_change = future_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Display prediction summary
        st.subheader("Prediction Summary")
        
        # Custom styled metrics
        summary_cols = st.columns(4)
        
        with summary_cols[0]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Current Price</div>
                <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(current_price)}</div>
                <div style="font-size: 0.9rem; color: gray;">Last closing price</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_cols[1]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Predicted Price</div>
                <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(future_price)}</div>
                <div style="font-size: 0.9rem; color: gray;">In {forecast_days} days</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_cols[2]:
            delta_color = "green" if price_change_pct >= 0 else "red"
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: var(--card-background); border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Predicted Change</div>
                <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(price_change)}</div>
                <div style="font-size: 0.9rem; color: {delta_color};">{price_change_pct:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Trading signal based on prediction
        if price_change_pct > 1.0:
            signal = "BUY"
            signal_color = "#198754"  # green
            signal_bg = "rgba(25, 135, 84, 0.1)"
            signal_icon = "📈"
        elif price_change_pct < -1.0:
            signal = "SELL"
            signal_color = "#dc3545"  # red
            signal_bg = "rgba(220, 53, 69, 0.1)"
            signal_icon = "📉"
        else:
            signal = "HOLD"
            signal_color = "#fd7e14"  # orange
            signal_bg = "rgba(253, 126, 20, 0.1)"
            signal_icon = "⏸️"
        
        with summary_cols[3]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background-color: {signal_bg}; border: 1px solid {signal_color}; border-radius: 8px; box-shadow: 0 2px 4px var(--shadow-color);">
                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">Trading Signal</div>
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{signal_icon}</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: {signal_color};">{signal}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed forecast table
        st.subheader("Detailed Forecast")
        
        # Create a dataframe with the forecast
        forecast_df = pd.DataFrame({
            'Date': [date.strftime('%Y-%m-%d') for date in forecast_dates],
            'Predicted Price': [format_currency(val) for val in forecast_values],
            'Lower Bound': [format_currency(val) for val in lower_bound],
            'Upper Bound': [format_currency(val) for val in upper_bound]
        })
        
        # Style the dataframe
        st.dataframe(
            forecast_df, 
            use_container_width=True,
            column_config={
                "Date": st.column_config.TextColumn("Date", width="medium"),
                "Predicted Price": st.column_config.TextColumn("Predicted Price", width="medium"),
                "Lower Bound": st.column_config.TextColumn("Lower Bound (-5%)", width="medium"),
                "Upper Bound": st.column_config.TextColumn("Upper Bound (+5%)", width="medium")
            },
            hide_index=True
        )
        
        # Close the custom card
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alert section
        st.header("Trading Alerts")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        if enable_alerts and abs(price_change_pct) >= alert_threshold:
            # Save user alert preferences
            db.save_user_preferences(
                st.session_state['session_id'],
                telegram_enabled=True,
                alert_threshold=alert_threshold
            )
            
            # Format the alert message
            alert_message = format_alert_message(
                symbol=sidebar_state['display_name'],
                current_price=current_price,
                predicted_price=future_price,
                days=forecast_days,
                signal=signal
            )
            
            # Create a styled alert box
            alert_color = "#198754" if price_change_pct > 0 else "#dc3545"
            st.markdown(f"""
            <div style="background-color: rgba({alert_color.lstrip('#')[:2]}, {alert_color.lstrip('#')[2:4]}, {alert_color.lstrip('#')[4:]}, 0.1); 
                        border: 1px solid {alert_color}; 
                        border-radius: 8px; 
                        padding: 1rem; 
                        margin-bottom: 1rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 2rem; margin-right: 1rem;">🔔</div>
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">Alert Triggered!</div>
                        <div>Price change of <strong>{price_change_pct:.2f}%</strong> exceeds threshold of {alert_threshold}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display alert message
            st.code(alert_message)
            
            # Send alert button
            if st.button("Send Alert Now", type="primary"):
                try:
                    # Send and store the alert
                    send_telegram_alert(
                        message=alert_message,
                        symbol=sidebar_state['symbol'],
                        market_type=sidebar_state['market_type'],
                        current_price=current_price,
                        predicted_price=future_price,
                        signal=signal
                    )
                    st.success("Alert sent to Telegram!")
                except Exception as e:
                    # Store the alert even if sending fails
                    try:
                        db.store_alert(
                            symbol=sidebar_state['symbol'],
                            market_type=sidebar_state['market_type'],
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
            if not enable_alerts:
                st.markdown(f"""
                <div style="background-color: rgba(13, 202, 240, 0.1); 
                            border: 1px solid #0dcaf0; 
                            border-radius: 8px; 
                            padding: 1rem; 
                            margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 2rem; margin-right: 1rem;">ℹ️</div>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">Alerts Disabled</div>
                            <div>Enable Telegram alerts in the sidebar to receive trading signals.</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif abs(price_change_pct) < alert_threshold:
                st.markdown(f"""
                <div style="background-color: rgba(13, 202, 240, 0.1); 
                            border: 1px solid #0dcaf0; 
                            border-radius: 8px; 
                            padding: 1rem; 
                            margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 2rem; margin-right: 1rem;">ℹ️</div>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">No Alert Triggered</div>
                            <div>Price change of <strong>{price_change_pct:.2f}%</strong> is below threshold of {alert_threshold}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Close the custom card
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Click 'Train Model' to generate predictions.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")