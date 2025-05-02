import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import os
from dotenv import load_dotenv
import database as db

# Load environment variables
load_dotenv()

# Define popular stock tickers for dropdown
POPULAR_STOCKS = [
    # Technology
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"symbol": "GOOG", "name": "Alphabet Inc. Class C"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "ADBE", "name": "Adobe Inc."},
    {"symbol": "CSCO", "name": "Cisco Systems Inc."},
    {"symbol": "INTC", "name": "Intel Corporation"},
    {"symbol": "CRM", "name": "Salesforce Inc."},
    {"symbol": "AMD", "name": "Advanced Micro Devices Inc."},
    {"symbol": "ORCL", "name": "Oracle Corporation"},
    {"symbol": "IBM", "name": "International Business Machines"},
    {"symbol": "QCOM", "name": "Qualcomm Inc."},
    {"symbol": "TXN", "name": "Texas Instruments Inc."},
    {"symbol": "NFLX", "name": "Netflix Inc."},
    {"symbol": "PYPL", "name": "PayPal Holdings Inc."},
    {"symbol": "UBER", "name": "Uber Technologies Inc."},
    {"symbol": "ABNB", "name": "Airbnb Inc."},
    
    # Financial
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "V", "name": "Visa Inc."},
    {"symbol": "MA", "name": "Mastercard Inc."},
    {"symbol": "BAC", "name": "Bank of America Corp."},
    {"symbol": "WFC", "name": "Wells Fargo & Co."},
    {"symbol": "C", "name": "Citigroup Inc."},
    {"symbol": "GS", "name": "Goldman Sachs Group Inc."},
    {"symbol": "MS", "name": "Morgan Stanley"},
    {"symbol": "AXP", "name": "American Express Co."},
    {"symbol": "BLK", "name": "BlackRock Inc."},
    
    # Healthcare
    {"symbol": "JNJ", "name": "Johnson & Johnson"},
    {"symbol": "UNH", "name": "UnitedHealth Group Inc."},
    {"symbol": "PFE", "name": "Pfizer Inc."},
    {"symbol": "MRK", "name": "Merck & Co. Inc."},
    {"symbol": "ABBV", "name": "AbbVie Inc."},
    {"symbol": "LLY", "name": "Eli Lilly and Co."},
    {"symbol": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"symbol": "ABT", "name": "Abbott Laboratories"},
    {"symbol": "BMY", "name": "Bristol-Myers Squibb Co."},
    {"symbol": "MDT", "name": "Medtronic plc"},
    
    # Consumer
    {"symbol": "WMT", "name": "Walmart Inc."},
    {"symbol": "PG", "name": "Procter & Gamble Co."},
    {"symbol": "HD", "name": "Home Depot Inc."},
    {"symbol": "KO", "name": "Coca-Cola Co."},
    {"symbol": "PEP", "name": "PepsiCo Inc."},
    {"symbol": "COST", "name": "Costco Wholesale Corp."},
    {"symbol": "MCD", "name": "McDonald's Corp."},
    {"symbol": "NKE", "name": "Nike Inc."},
    {"symbol": "DIS", "name": "Walt Disney Co."},
    {"symbol": "SBUX", "name": "Starbucks Corp."},
    
    # Energy & Industrial
    {"symbol": "XOM", "name": "Exxon Mobil Corporation"},
    {"symbol": "CVX", "name": "Chevron Corporation"},
    {"symbol": "RTX", "name": "Raytheon Technologies Corp."},
    {"symbol": "HON", "name": "Honeywell International Inc."},
    {"symbol": "UPS", "name": "United Parcel Service Inc."},
    {"symbol": "CAT", "name": "Caterpillar Inc."},
    {"symbol": "BA", "name": "Boeing Co."},
    {"symbol": "GE", "name": "General Electric Co."},
    {"symbol": "MMM", "name": "3M Co."},
    {"symbol": "DE", "name": "Deere & Co."},
    
    # Telecommunications
    {"symbol": "VZ", "name": "Verizon Communications Inc."},
    {"symbol": "T", "name": "AT&T Inc."},
    {"symbol": "TMUS", "name": "T-Mobile US Inc."},
    
    # Indian Stocks
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd."},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd."},
    {"symbol": "INFY.NS", "name": "Infosys Ltd."},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd."},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Ltd."},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd."},
    {"symbol": "SBIN.NS", "name": "State Bank of India"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd."},
    {"symbol": "ITC.NS", "name": "ITC Ltd."},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd."}
]

# Define forex pairs
FOREX_PAIRS = [
    # Major Pairs
    {"symbol": "EURUSD=X", "name": "EUR/USD"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD"},
    {"symbol": "USDJPY=X", "name": "USD/JPY"},
    {"symbol": "AUDUSD=X", "name": "AUD/USD"},
    {"symbol": "USDCAD=X", "name": "USD/CAD"},
    {"symbol": "USDCHF=X", "name": "USD/CHF"},
    {"symbol": "NZDUSD=X", "name": "NZD/USD"},
    
    # Cross Pairs - EUR
    {"symbol": "EURJPY=X", "name": "EUR/JPY"},
    {"symbol": "EURGBP=X", "name": "EUR/GBP"},
    {"symbol": "EURAUD=X", "name": "EUR/AUD"},
    {"symbol": "EURCHF=X", "name": "EUR/CHF"},
    {"symbol": "EURCAD=X", "name": "EUR/CAD"},
    {"symbol": "EURNZD=X", "name": "EUR/NZD"},
    
    # Cross Pairs - GBP
    {"symbol": "GBPJPY=X", "name": "GBP/JPY"},
    {"symbol": "GBPAUD=X", "name": "GBP/AUD"},
    {"symbol": "GBPCAD=X", "name": "GBP/CAD"},
    {"symbol": "GBPCHF=X", "name": "GBP/CHF"},
    {"symbol": "GBPNZD=X", "name": "GBP/NZD"},
    
    # Cross Pairs - JPY
    {"symbol": "AUDJPY=X", "name": "AUD/JPY"},
    {"symbol": "CADJPY=X", "name": "CAD/JPY"},
    {"symbol": "CHFJPY=X", "name": "CHF/JPY"},
    {"symbol": "NZDJPY=X", "name": "NZD/JPY"},
    
    # Other Cross Pairs
    {"symbol": "AUDCAD=X", "name": "AUD/CAD"},
    {"symbol": "AUDCHF=X", "name": "AUD/CHF"},
    {"symbol": "AUDNZD=X", "name": "AUD/NZD"},
    {"symbol": "CADCHF=X", "name": "CAD/CHF"},
    {"symbol": "NZDCAD=X", "name": "NZD/CAD"},
    {"symbol": "NZDCHF=X", "name": "NZD/CHF"},
    
    # Exotic Pairs
    {"symbol": "USDSEK=X", "name": "USD/SEK"},
    {"symbol": "USDNOK=X", "name": "USD/NOK"},
    {"symbol": "USDDKK=X", "name": "USD/DKK"},
    {"symbol": "USDSGD=X", "name": "USD/SGD"},
    {"symbol": "USDHKD=X", "name": "USD/HKD"},
    {"symbol": "USDTRY=X", "name": "USD/TRY"},
    {"symbol": "USDZAR=X", "name": "USD/ZAR"},
    {"symbol": "USDMXN=X", "name": "USD/MXN"},
    {"symbol": "USDBRL=X", "name": "USD/BRL"},
    {"symbol": "USDINR=X", "name": "USD/INR"}
]

def get_available_stocks():
    """
    Return a list of popular stocks from predefined list
    Returns a list of dictionaries with stock information
    """
    try:
        # Use our predefined list of popular stocks
        stocks = POPULAR_STOCKS
        
        # Cache the results
        st.session_state["available_stocks"] = stocks
        return stocks
        
    except Exception as e:
        st.error(f"Error fetching available stocks: {str(e)}")
        return []

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_stock_data(symbol, period, interval):
    """
    Fetch stock data using Yahoo Finance API (yfinance)
    
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
        start_date = calculate_start_date(period, end_date)
        
        # Check if we have this data in the database
        if db.check_data_exists(symbol, start_date, end_date):
            st.info(f"Loading {symbol} data from database...")
            return db.get_market_data(symbol, start_date, end_date)
        
        # Otherwise fetch from Yahoo Finance API
        st.info(f"Fetching {symbol} data from Yahoo Finance API...")
        
        # Create a Ticker object
        ticker = yf.Ticker(symbol)
        
        # Download the data
        df = ticker.history(period=period, interval=interval)
        
        # Check if data is empty
        if df.empty:
            st.error(f"No data available for {symbol}")
            return pd.DataFrame()
        
        # Ensure column names are correct (yfinance already uses the right format)
        # But let's make sure they're consistent
        df = df.rename(columns={
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        })
        
        # Store data in the database
        try:
            db.store_market_data(df, symbol, 'Stock')
            st.success(f"Stored {len(df)} records for {symbol} in database")
        except Exception as db_error:
            st.warning(f"Failed to store data in database: {str(db_error)}")
            
        return df
    
    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_forex_data(symbol, period, interval):
    """
    Fetch forex data using Yahoo Finance API (yfinance)
    
    Args:
        symbol: Forex pair in Yahoo format (e.g., 'EURUSD=X')
        period: Time period to fetch (e.g., '1d', '1mo', '1y')
        interval: Time interval between points (e.g., '1m', '1h', '1d')
    
    Returns:
        DataFrame with OHLCV data
    """
    # For forex, we use the same function as stocks since yfinance handles both
    return fetch_stock_data(symbol, period, interval)

def calculate_start_date(period, end_date):
    """Helper function to calculate start date based on period"""
    period_map = {
        "1d": timedelta(days=1),
        "1wk": timedelta(weeks=1),
        "1mo": timedelta(days=30),
        "3mo": timedelta(days=90),
        "6mo": timedelta(days=180),
        "1y": timedelta(days=365),
        "2y": timedelta(days=730),
        "5y": timedelta(days=1825)
    }
    return end_date - period_map.get(period, timedelta(days=30))
