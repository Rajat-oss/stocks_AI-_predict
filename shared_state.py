"""
Shared state management for the Streamlit multi-page application.
This module provides functions to initialize and access session state across pages.
"""

import streamlit as st
import uuid
import database as db
from data_fetcher import FOREX_PAIRS, POPULAR_STOCKS, get_available_stocks

def initialize_session():
    """Initialize session state variables if they don't exist"""
    
    # Initialize session ID for user tracking
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    
    # Initialize market selection
    if 'market_type' not in st.session_state:
        st.session_state['market_type'] = "Stock"
    
    # Initialize symbol selection
    if 'symbol' not in st.session_state:
        st.session_state['symbol'] = "AAPL"
    
    if 'display_name' not in st.session_state:
        st.session_state['display_name'] = "AAPL"
    
    # Initialize time period and interval
    if 'period' not in st.session_state:
        st.session_state['period'] = "1mo"
    
    if 'interval' not in st.session_state:
        st.session_state['interval'] = "1d"
    
    # Initialize technical indicator settings
    if 'show_rsi' not in st.session_state:
        st.session_state['show_rsi'] = True
    
    if 'show_macd' not in st.session_state:
        st.session_state['show_macd'] = True
    
    if 'show_ema' not in st.session_state:
        st.session_state['show_ema'] = True
    
    # Initialize model settings
    if 'forecast_days' not in st.session_state:
        st.session_state['forecast_days'] = 7
    
    # Initialize alert settings
    if 'enable_alerts' not in st.session_state:
        st.session_state['enable_alerts'] = False
    
    if 'alert_threshold' not in st.session_state:
        st.session_state['alert_threshold'] = 1.0
    
    # Initialize available stocks
    if 'available_stocks' not in st.session_state:
        st.session_state['available_stocks'] = get_available_stocks()
    
    # Get user preferences from database - create a new session for this operation
    session = db.get_session()
    try:
        # Query for user preferences
        user_prefs = session.query(db.UserPreference).filter_by(session_id=st.session_state['session_id']).first()
        
        # Create new preferences if not found
        if not user_prefs:
            user_prefs = db.UserPreference(session_id=st.session_state['session_id'])
            session.add(user_prefs)
            session.commit()
        
        # Apply user preferences if available
        if user_prefs.preferred_timeframe:
            st.session_state['period'] = user_prefs.preferred_timeframe
        
        if user_prefs.preferred_interval:
            st.session_state['interval'] = user_prefs.preferred_interval
        
        if user_prefs.alert_threshold:
            st.session_state['alert_threshold'] = user_prefs.alert_threshold
        
        if user_prefs.telegram_enabled is not None:
            st.session_state['enable_alerts'] = user_prefs.telegram_enabled
            
        # Return a copy of the user preferences
        return {
            'session_id': user_prefs.session_id,
            'favorite_symbols': user_prefs.favorite_symbols,
            'preferred_timeframe': user_prefs.preferred_timeframe,
            'preferred_interval': user_prefs.preferred_interval,
            'alert_threshold': user_prefs.alert_threshold,
            'telegram_enabled': user_prefs.telegram_enabled
        }
    finally:
        session.close()

def get_market_options():
    """Get market selection options based on current market type"""
    if st.session_state['market_type'] == "Forex":
        # Forex pair options
        forex_options = [(f"{s['name']} ({s['symbol'].replace('=X', '')})", s['symbol']) for s in FOREX_PAIRS]
        return forex_options
    else:
        # Stock options
        if st.session_state['available_stocks']:
            stocks = st.session_state['available_stocks']
        else:
            stocks = POPULAR_STOCKS
        
        stock_options = [(f"{s['symbol']} - {s['name']}", s['symbol']) for s in stocks]
        return stock_options

def get_period_options():
    """Get time period options"""
    return {
        "1 Week": "1wk",
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }

def get_interval_options():
    """Get interval options"""
    return {
        "1 Day": "1d",
        "1 Hour": "1h",
        "15 Minutes": "15m",
        "5 Minutes": "5m",
        "1 Minute": "1m"
    }

def save_user_preferences():
    """Save current user preferences to database"""
    db.save_user_preferences(
        st.session_state['session_id'],
        preferred_timeframe=st.session_state['period'],
        preferred_interval=st.session_state['interval'],
        alert_threshold=st.session_state['alert_threshold'],
        telegram_enabled=st.session_state['enable_alerts']
    )