import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        data: DataFrame with price data
        window: RSI calculation period
    
    Returns:
        Series with RSI values
    """
    delta = data.diff()
    up, down = delta.copy(), delta.copy()
    
    up[up < 0] = 0
    down[down > 0] = 0
    down = down.abs()
    
    avg_gain = up.rolling(window=window).mean()
    avg_loss = down.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate Moving Average Convergence Divergence (MACD)
    
    Args:
        data: DataFrame with price data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
    
    Returns:
        Tuple of (MACD, Signal, Histogram)
    """
    # Fast EMA
    ema_fast = data.ewm(span=fast_period, adjust=False).mean()
    
    # Slow EMA
    ema_slow = data.ewm(span=slow_period, adjust=False).mean()
    
    # MACD Line
    macd_line = ema_fast - ema_slow
    
    # Signal Line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_ema(data, periods=[9, 20, 50]):
    """
    Calculate Exponential Moving Average (EMA) for multiple periods
    
    Args:
        data: DataFrame with price data
        periods: List of periods for EMA calculation
    
    Returns:
        Dictionary with EMA values for each period
    """
    ema_values = {}
    
    for period in periods:
        ema_values[f'EMA_{period}'] = data.ewm(span=period, adjust=False).mean()
    
    return ema_values

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    Calculate Bollinger Bands
    
    Args:
        data: DataFrame with price data
        window: Moving average window
        num_std: Number of standard deviations
        
    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    """
    middle_band = data.rolling(window=window).mean()
    std_dev = data.rolling(window=window).std()
    
    upper_band = middle_band + (std_dev * num_std)
    lower_band = middle_band - (std_dev * num_std)
    
    return upper_band, middle_band, lower_band

def calculate_indicators(df):
    """
    Calculate all technical indicators for a DataFrame
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with added technical indicators
    """
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # RSI
    result['RSI'] = calculate_rsi(result['Close'])
    
    # MACD
    macd_line, signal_line, histogram = calculate_macd(result['Close'])
    result['MACD'] = macd_line
    result['MACD_Signal'] = signal_line
    result['MACD_Hist'] = histogram
    
    # EMA
    ema_values = calculate_ema(result['Close'])
    for key, value in ema_values.items():
        result[key] = value
    
    # Bollinger Bands
    upper_band, middle_band, lower_band = calculate_bollinger_bands(result['Close'])
    result['BB_Upper'] = upper_band
    result['BB_Middle'] = middle_band
    result['BB_Lower'] = lower_band
    
    return result
