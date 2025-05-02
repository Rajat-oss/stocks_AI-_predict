"""
Settings page for the Forex & Stock Market Prediction System.
This page allows users to configure application preferences.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Import custom modules
from shared_state import initialize_session
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme, apply_chart_theme
import database as db

# Page configuration
st.set_page_config(
    page_title="Settings - Forex & Stock Market Prediction",
    page_icon="⚙️",
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
st.title("Settings")
st.markdown("""
Configure your application preferences and manage your account settings.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Main content
try:
    # User preferences section
    st.header("User Preferences")
    
    prefs_cols = st.columns(2)
    
    with prefs_cols[0]:
        st.subheader("Default Market Settings")
        
        # Default market type
        default_market = st.radio(
            "Default Market Type", 
            ["Forex", "Stock"], 
            index=0 if st.session_state['market_type'] == "Forex" else 1
        )
        
        # Default time period
        period_options = {
            "1 Week": "1wk",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        
        period_labels = list(period_options.keys())
        period_values = list(period_options.values())
        
        try:
            default_period_index = period_values.index(st.session_state['period'])
        except ValueError:
            default_period_index = 1  # Default to 1 month
        
        default_period = st.selectbox(
            "Default Time Period",
            options=period_labels,
            index=default_period_index
        )
        
        # Default interval
        interval_options = {
            "1 Day": "1d",
            "1 Hour": "1h",
            "15 Minutes": "15m",
            "5 Minutes": "5m",
            "1 Minute": "1m"
        }
        
        interval_labels = list(interval_options.keys())
        interval_values = list(interval_options.values())
        
        try:
            default_interval_index = interval_values.index(st.session_state['interval'])
        except ValueError:
            default_interval_index = 0  # Default to 1 day
        
        default_interval = st.selectbox(
            "Default Interval",
            options=interval_labels,
            index=default_interval_index
        )
    
    with prefs_cols[1]:
        st.subheader("Favorite Symbols")
        
        # Get current favorites
        current_favorites = user_prefs['favorite_symbols'].split(",") if user_prefs['favorite_symbols'] else []
        if current_favorites and current_favorites[0] == '':
            current_favorites = []
        
        # Display current favorites
        st.write("Your favorite symbols:")
        
        if current_favorites:
            # Create a dataframe for favorites
            favorites_data = []
            for i, fav in enumerate(current_favorites):
                if fav:  # Skip empty strings
                    favorites_data.append({
                        "Symbol": fav,
                        "Remove": False  # Checkbox for removal
                    })
            
            if favorites_data:
                favorites_df = pd.DataFrame(favorites_data)
                
                # Display with checkboxes for removal
                edited_df = st.data_editor(
                    favorites_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Symbol": st.column_config.TextColumn("Symbol"),
                        "Remove": st.column_config.CheckboxColumn("Remove")
                    }
                )
                
                # Check for symbols to remove
                symbols_to_remove = edited_df[edited_df["Remove"]]["Symbol"].tolist()
                
                if symbols_to_remove and st.button("Remove Selected Symbols"):
                    # Remove selected symbols
                    updated_favorites = [fav for fav in current_favorites if fav not in symbols_to_remove]
                    
                    # Save updated favorites
                    db.save_user_preferences(
                        st.session_state['session_id'],
                        favorite_symbols=",".join(updated_favorites) if updated_favorites else ""
                    )
                    
                    st.success(f"Removed {len(symbols_to_remove)} symbol(s) from favorites.")
                    st.rerun()
            else:
                st.info("No favorite symbols found.")
        else:
            st.info("No favorite symbols found. Add symbols to your favorites from the dashboard.")
        
        # Add current symbol to favorites
        if st.button(f"Add Current Symbol ({sidebar_state['symbol']}) to Favorites"):
            if sidebar_state['symbol'] not in current_favorites:
                updated_favorites = current_favorites + [sidebar_state['symbol']]
                
                # Save updated favorites
                db.save_user_preferences(
                    st.session_state['session_id'],
                    favorite_symbols=",".join(updated_favorites)
                )
                
                st.success(f"Added {sidebar_state['display_name']} to favorites.")
                st.rerun()
            else:
                st.info(f"{sidebar_state['display_name']} is already in your favorites.")
    
    # Save default settings
    if st.button("Save Default Settings"):
        # Update session state
        st.session_state['market_type'] = default_market
        st.session_state['period'] = period_options[default_period]
        st.session_state['interval'] = interval_options[default_interval]
        
        # Save to database
        db.save_user_preferences(
            st.session_state['session_id'],
            preferred_timeframe=period_options[default_period],
            preferred_interval=interval_options[default_interval]
        )
        
        st.success("Default settings saved successfully!")
    
    # Application settings
    st.header("Application Settings")
    
    app_cols = st.columns(2)
    
    with app_cols[0]:
        st.subheader("Display Settings")
        
        # Dark theme info
        st.markdown("""
        <div style="background-color: #495057; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 0.5rem;">🌙</div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">Dark Mode</div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">The application is optimized for dark mode for better visibility of financial charts and data.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chart style
        chart_style = st.selectbox(
            "Chart Style",
            ["Default", "Classic", "Modern", "Minimal"]
        )
        
        if chart_style != "Default":
            st.info("Chart style customization will be implemented in a future update.")
    
    with app_cols[1]:
        st.subheader("Data Settings")
        
        # Data refresh rate
        refresh_rate = st.selectbox(
            "Data Refresh Rate",
            ["Manual only", "Every 1 minute", "Every 5 minutes", "Every 15 minutes", "Every hour"]
        )
        
        if refresh_rate != "Manual only":
            st.info("Automatic data refresh will be implemented in a future update.")
        
        # Cache settings
        cache_data = st.checkbox("Cache market data", value=True)
        
        if cache_data:
            cache_duration = st.slider("Cache Duration (minutes)", 1, 60, 5)
            st.info(f"Data will be cached for {cache_duration} minutes.")
        else:
            st.info("Data will be fetched fresh on every request.")
    
    # Database management
    st.header("Database Management")
    
    db_cols = st.columns(2)
    
    with db_cols[0]:
        st.subheader("Database Information")
        
        # Get database stats
        session = db.get_session()
        try:
            market_data_count = session.query(db.MarketData).count()
            predictions_count = session.query(db.Prediction).count()
            alerts_count = session.query(db.Alert).count()
            users_count = session.query(db.UserPreference).count()
            
            # Display stats
            st.write(f"Market Data Records: {market_data_count}")
            st.write(f"Prediction Records: {predictions_count}")
            st.write(f"Alert Records: {alerts_count}")
            st.write(f"User Preference Records: {users_count}")
            
            # Database file info
            db_file = "marketprophet.db"
            if os.path.exists(db_file):
                db_size = os.path.getsize(db_file) / (1024 * 1024)  # Convert to MB
                db_modified = datetime.fromtimestamp(os.path.getmtime(db_file))
                
                st.write(f"Database Size: {db_size:.2f} MB")
                st.write(f"Last Modified: {db_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            session.close()
    
    with db_cols[1]:
        st.subheader("Database Maintenance")
        
        # Clear old data
        if st.button("Clear Old Market Data (>30 days)"):
            session = db.get_session()
            try:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                deleted_count = session.query(db.MarketData).filter(
                    db.MarketData.timestamp < thirty_days_ago
                ).delete()
                session.commit()
                
                st.success(f"Deleted {deleted_count} old market data records.")
            except Exception as e:
                session.rollback()
                st.error(f"Failed to delete old data: {str(e)}")
            finally:
                session.close()
        
        # Clear all alerts
        if st.button("Clear All Alerts"):
            session = db.get_session()
            try:
                deleted_count = session.query(db.Alert).delete()
                session.commit()
                
                st.success(f"Deleted {deleted_count} alert records.")
            except Exception as e:
                session.rollback()
                st.error(f"Failed to delete alerts: {str(e)}")
            finally:
                session.close()
    
    # About section
    st.header("About")
    
    about_cols = st.columns(2)
    
    with about_cols[0]:
        st.subheader("Application Information")
        
        st.write("**Forex & Stock Market Prediction System**")
        st.write("Version: 1.0.0")
        st.write("A Streamlit-based application for Forex and stock market prediction with technical indicators, ML forecasting, and Telegram alerts.")
        
        st.write("**Features:**")
        features = [
            "Data collection from free financial APIs (yFinance)",
            "Preprocessing with technical indicators (RSI, MACD, EMA)",
            "Time series forecasting model",
            "Interactive dashboard with price charts and predictions",
            "Telegram alerting functionality for trade signals"
        ]
        
        for feature in features:
            st.write(f"- {feature}")
    
    with about_cols[1]:
        st.subheader("Session Information")
        
        st.write(f"Session ID: {st.session_state['session_id']}")
        st.write(f"Current Market Type: {st.session_state['market_type']}")
        st.write(f"Current Symbol: {st.session_state['symbol']}")
        st.write(f"Current Period: {st.session_state['period']}")
        st.write(f"Current Interval: {st.session_state['interval']}")
        
        # Clear session button
        if st.button("Reset Session"):
            # Clear session state (except session_id)
            session_id = st.session_state['session_id']
            st.session_state.clear()
            st.session_state['session_id'] = session_id
            
            st.success("Session reset successfully!")
            st.rerun()

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")