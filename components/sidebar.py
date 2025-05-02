"""
Sidebar component for the Streamlit multi-page application.
This module provides a consistent sidebar across all pages.
"""

import streamlit as st
from shared_state import get_market_options, get_period_options, get_interval_options, save_user_preferences

def render_sidebar():
    """Render the sidebar with market selection and time period options"""
    
    st.sidebar.header("Market Settings")
    
    # Market selection
    market_type = st.sidebar.radio("Select Market", ["Forex", "Stock"], index=0 if st.session_state['market_type'] == "Forex" else 1)
    
    # Update session state if changed
    if market_type != st.session_state['market_type']:
        st.session_state['market_type'] = market_type
        # Reset to default symbol when market type changes
        if market_type == "Forex":
            st.session_state['symbol'] = "EURUSD=X"
            st.session_state['display_name'] = "EUR/USD"
        else:
            st.session_state['symbol'] = "AAPL"
            st.session_state['display_name'] = "AAPL"
    
    # Get options based on market type
    options = get_market_options()
    
    # Symbol selection
    option_labels = [opt[0] for opt in options]
    option_values = dict(options)
    
    # Find the index of the current symbol in the options
    try:
        current_index = [opt[1] for opt in options].index(st.session_state['symbol'])
    except ValueError:
        current_index = 0
    
    selected_option = st.sidebar.selectbox(
        f"Select {'Forex Pair' if market_type == 'Forex' else 'Stock'}", 
        options=option_labels,
        index=current_index
    )
    
    # Update symbol in session state
    symbol = option_values[selected_option]
    if symbol != st.session_state['symbol']:
        st.session_state['symbol'] = symbol
        
        # Update display name
        if market_type == "Forex":
            st.session_state['display_name'] = selected_option.split(" (")[0]
        else:
            st.session_state['display_name'] = selected_option.split(" - ")[0]
    
    # Time period selection
    st.sidebar.header("Time Settings")
    
    period_options = get_period_options()
    period_labels = list(period_options.keys())
    
    # Find the index of the current period
    try:
        period_index = list(period_options.values()).index(st.session_state['period'])
    except ValueError:
        period_index = 1  # Default to 1 month
    
    selected_period = st.sidebar.selectbox(
        "Select Time Period", 
        options=period_labels,
        index=period_index
    )
    
    # Update period in session state
    period = period_options[selected_period]
    if period != st.session_state['period']:
        st.session_state['period'] = period
    
    # Interval selection
    interval_options = get_interval_options()
    interval_labels = list(interval_options.keys())
    
    # Find the index of the current interval
    try:
        interval_index = list(interval_options.values()).index(st.session_state['interval'])
    except ValueError:
        interval_index = 0  # Default to 1 day
    
    selected_interval = st.sidebar.selectbox(
        "Select Interval", 
        options=interval_labels,
        index=interval_index
    )
    
    # Update interval in session state
    interval = interval_options[selected_interval]
    if interval != st.session_state['interval']:
        st.session_state['interval'] = interval
    
    # Technical indicator selection
    st.sidebar.header("Technical Indicators")
    
    show_rsi = st.sidebar.checkbox("RSI (Relative Strength Index)", value=st.session_state['show_rsi'])
    if show_rsi != st.session_state['show_rsi']:
        st.session_state['show_rsi'] = show_rsi
    
    show_macd = st.sidebar.checkbox("MACD (Moving Average Convergence Divergence)", value=st.session_state['show_macd'])
    if show_macd != st.session_state['show_macd']:
        st.session_state['show_macd'] = show_macd
    
    show_ema = st.sidebar.checkbox("EMA (Exponential Moving Average)", value=st.session_state['show_ema'])
    if show_ema != st.session_state['show_ema']:
        st.session_state['show_ema'] = show_ema
    
    # Save preferences when sidebar changes
    save_user_preferences()
    
    return {
        'market_type': st.session_state['market_type'],
        'symbol': st.session_state['symbol'],
        'display_name': st.session_state['display_name'],
        'period': st.session_state['period'],
        'interval': st.session_state['interval'],
        'show_rsi': st.session_state['show_rsi'],
        'show_macd': st.session_state['show_macd'],
        'show_ema': st.session_state['show_ema']
    }