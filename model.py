import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

def prepare_features(df):
    """
    Prepare features for the prediction model
    
    Args:
        df: DataFrame with price and indicators data
    
    Returns:
        DataFrame with features for modeling
    """
    # Use only complete rows (drop NaN values)
    data = df.dropna().copy()
    
    # Select features (technical indicators and price data)
    features = data[['Close', 'RSI', 'MACD', 'MACD_Signal', 'EMA_9', 'EMA_20', 'EMA_50']].copy()
    
    # Add lag features (previous day's close price)
    for i in range(1, 6):
        features[f'Close_lag_{i}'] = features['Close'].shift(i)
    
    # Add return features
    features['Return_1d'] = features['Close'].pct_change(1)
    features['Return_5d'] = features['Close'].pct_change(5)
    
    # Add volatility feature (standard deviation over 5 days)
    features['Volatility_5d'] = features['Close'].rolling(window=5).std()
    
    # Drop rows with NaN values after creating lagged features
    features = features.dropna()
    
    return features

def create_sequences(data, target_col, sequence_length=5, forecast_horizon=1):
    """
    Create sequences for time series forecasting
    
    Args:
        data: DataFrame with features
        target_col: Target column name
        sequence_length: Number of previous time steps to use
        forecast_horizon: Number of steps to forecast
        
    Returns:
        X (features), y (targets)
    """
    X, y = [], []
    
    for i in range(len(data) - sequence_length - forecast_horizon + 1):
        X.append(data.iloc[i:i+sequence_length].values)
        y.append(data.iloc[i+sequence_length+forecast_horizon-1][target_col])
    
    return np.array(X), np.array(y)

def train_model(df, forecast_days=7):
    """
    Train a time series forecasting model
    
    Args:
        df: DataFrame with price and indicator data
        forecast_days: Number of days to forecast
        
    Returns:
        Trained model, scaler and feature set
    """
    # Prepare features
    features = prepare_features(df)
    
    # Separate target variable (Close price)
    X = features.drop('Close', axis=1)
    y = features['Close']
    
    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)
    
    # Split into train and test sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, shuffle=False
    )
    
    # Train Random Forest model (simpler and faster than LSTM for this demo)
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Display model performance
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    st.write(f"Model R² score (training): {train_score:.4f}")
    st.write(f"Model R² score (testing): {test_score:.4f}")
    
    return model, scaler, X.columns

def make_predictions(df, model, scaler, feature_names, forecast_days=7):
    """
    Make forecasts using the trained model
    
    Args:
        df: DataFrame with price and indicator data
        model: Trained model
        scaler: Fitted scaler
        feature_names: Feature columns
        forecast_days: Number of days to forecast
        
    Returns:
        Future dates and predicted values
    """
    # Get the most recent data
    recent_data = prepare_features(df).tail(1)
    last_date = recent_data.index[-1]
    last_close = recent_data['Close'].values[-1]
    
    # Create a list to store predictions
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days+1)]
    predicted_prices = []
    
    # Make a copy of the most recent data for iterative prediction
    current_data = recent_data.drop('Close', axis=1).copy()
    
    # Iteratively predict future values
    for i in range(forecast_days):
        # Scale the current data
        current_scaled = scaler.transform(current_data.values.reshape(1, -1))
        
        # Make prediction for the next day
        next_pred = model.predict(current_scaled)[0]
        predicted_prices.append(next_pred)
        
        # Update current data for next iteration
        # This is a simplified update that would need to be more sophisticated in a real model
        new_row = current_data.copy()
        
        # Update lag features
        if 'Close_lag_1' in new_row.columns:
            new_row['Close_lag_1'] = next_pred
            for j in range(2, 6):
                if f'Close_lag_{j}' in new_row.columns:
                    new_row[f'Close_lag_{j}'] = current_data[f'Close_lag_{j-1}'].values[0]
        
        # Update technical indicators (simplified)
        if 'EMA_9' in new_row.columns:
            alpha_9 = 2/(9+1)
            new_row['EMA_9'] = next_pred * alpha_9 + new_row['EMA_9'].values[0] * (1-alpha_9)
            
        if 'EMA_20' in new_row.columns:
            alpha_20 = 2/(20+1)
            new_row['EMA_20'] = next_pred * alpha_20 + new_row['EMA_20'].values[0] * (1-alpha_20)
            
        if 'EMA_50' in new_row.columns:
            alpha_50 = 2/(50+1)
            new_row['EMA_50'] = next_pred * alpha_50 + new_row['EMA_50'].values[0] * (1-alpha_50)
        
        # Update current data for next iteration
        current_data = new_row
    
    return forecast_dates, predicted_prices, last_close
