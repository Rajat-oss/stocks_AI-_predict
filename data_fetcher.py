import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_stock_data(symbol, period, interval):
    """
    Fetch stock data using yfinance
    
    Args:
        symbol: Stock ticker symbol
        period: Time period to fetch (e.g., '1d', '1mo', '1y')
        interval: Time interval between points (e.g., '1m', '1h', '1d')
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        data = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            progress=False
        )
        
        # Check if data is empty
        if data.empty:
            st.error(f"No data available for {symbol}")
            return pd.DataFrame()
        
        # Make sure the index is a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
            
        return data
    
    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_forex_data(symbol, period, interval):
    """
    Fetch forex data using yfinance
    
    Args:
        symbol: Forex pair in yfinance format (e.g., 'EURUSD=X')
        period: Time period to fetch (e.g., '1d', '1mo', '1y')
        interval: Time interval between points (e.g., '1m', '1h', '1d')
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        data = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            progress=False
        )
        
        # Check if data is empty
        if data.empty:
            st.error(f"No data available for {symbol}")
            return pd.DataFrame()
        
        # Make sure the index is a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
            
        return data
    
    except Exception as e:
        st.error(f"Error fetching forex data: {str(e)}")
        return pd.DataFrame()
