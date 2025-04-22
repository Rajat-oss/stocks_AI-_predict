import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import os
from dotenv import load_dotenv
import database as db

# Load environment variables
load_dotenv()

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
        # Convert period to datetime for database check
        end_date = datetime.now()
        
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "1wk":
            start_date = end_date - timedelta(weeks=1)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 1 month
        
        # Check if we have this data in the database
        if db.check_data_exists(symbol, start_date, end_date):
            st.info(f"Loading {symbol} data from database...")
            return db.get_market_data(symbol, start_date, end_date)
        
        # Otherwise fetch from yfinance
        st.info(f"Fetching {symbol} data from Yahoo Finance...")
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
        
        # Store data in the database
        try:
            db.store_market_data(data, symbol, 'Stock')
            st.success(f"Stored {len(data)} records for {symbol} in database")
        except Exception as db_error:
            st.warning(f"Failed to store data in database: {str(db_error)}")
            
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
        # Convert period to datetime for database check
        end_date = datetime.now()
        
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "1wk":
            start_date = end_date - timedelta(weeks=1)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 1 month
        
        # Check if we have this data in the database
        if db.check_data_exists(symbol, start_date, end_date):
            st.info(f"Loading {symbol} data from database...")
            return db.get_market_data(symbol, start_date, end_date)
        
        # Otherwise fetch from yfinance
        st.info(f"Fetching {symbol} data from Yahoo Finance...")
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
        
        # Store data in the database
        try:
            db.store_market_data(data, symbol, 'Forex')
            st.success(f"Stored {len(data)} records for {symbol} in database")
        except Exception as db_error:
            st.warning(f"Failed to store data in database: {str(db_error)}")
            
        return data
    
    except Exception as e:
        st.error(f"Error fetching forex data: {str(e)}")
        return pd.DataFrame()
