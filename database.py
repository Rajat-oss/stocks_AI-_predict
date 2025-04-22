import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create declarative base
Base = declarative_base()

class MarketData(Base):
    """Table for storing historical market data"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    market_type = Column(String(10), nullable=False)  # 'Forex' or 'Stock'
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float)
    
    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    ema_9 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="market_data")
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', timestamp='{self.timestamp}', close_price={self.close_price})>"

class Prediction(Base):
    """Table for storing model predictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    market_data_id = Column(Integer, ForeignKey('market_data.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    prediction_date = Column(DateTime, nullable=False)  # Date the prediction is for
    predicted_price = Column(Float, nullable=False)
    model_version = Column(String(50))  # To track different model versions
    confidence = Column(Float)  # Optional confidence score
    
    # Relationship
    market_data = relationship("MarketData", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(prediction_date='{self.prediction_date}', predicted_price={self.predicted_price})>"

class Alert(Base):
    """Table for storing generated alerts"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    market_type = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    signal = Column(String(10), nullable=False)  # BUY, SELL, or HOLD
    message = Column(Text)
    sent = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Alert(symbol='{self.symbol}', timestamp='{self.timestamp}', signal='{self.signal}')>"

class UserPreference(Base):
    """Table for storing user preferences"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, unique=True)
    favorite_symbols = Column(Text)  # Stored as comma-separated values
    preferred_timeframe = Column(String(20))
    preferred_interval = Column(String(20))
    alert_threshold = Column(Float)
    telegram_enabled = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreference(session_id='{self.session_id}')>"

# Create all tables
def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

# Function to store market data in the database
def store_market_data(df, symbol, market_type):
    """
    Store market data from a pandas DataFrame into the database
    
    Args:
        df: DataFrame with OHLCV and technical indicator data
        symbol: Trading symbol
        market_type: 'Forex' or 'Stock'
    
    Returns:
        Number of records inserted
    """
    try:
        # Create list of MarketData objects
        records = []
        
        for index, row in df.iterrows():
            # Create MarketData object
            market_data = MarketData(
                symbol=symbol,
                market_type=market_type,
                timestamp=index,
                open_price=row['Open'],
                high_price=row['High'],
                low_price=row['Low'],
                close_price=row['Close'],
                volume=row.get('Volume', 0),
                
                # Technical indicators (if available)
                rsi=row.get('RSI'),
                macd=row.get('MACD'),
                macd_signal=row.get('MACD_Signal'),
                macd_hist=row.get('MACD_Hist'),
                ema_9=row.get('EMA_9'),
                ema_20=row.get('EMA_20'),
                ema_50=row.get('EMA_50'),
                bb_upper=row.get('BB_Upper'),
                bb_middle=row.get('BB_Middle'),
                bb_lower=row.get('BB_Lower')
            )
            
            records.append(market_data)
        
        # Bulk insert
        session.bulk_save_objects(records)
        session.commit()
        
        return len(records)
        
    except Exception as e:
        session.rollback()
        raise e

# Function to store a prediction
def store_prediction(market_data_id, prediction_date, predicted_price, model_version=None, confidence=None):
    """
    Store a prediction in the database
    
    Args:
        market_data_id: ID of the corresponding market data record
        prediction_date: Date the prediction is for
        predicted_price: Predicted price
        model_version: Version of the model used
        confidence: Confidence score (optional)
    
    Returns:
        Created Prediction object
    """
    try:
        prediction = Prediction(
            market_data_id=market_data_id,
            prediction_date=prediction_date,
            predicted_price=predicted_price,
            model_version=model_version,
            confidence=confidence
        )
        
        session.add(prediction)
        session.commit()
        
        return prediction
        
    except Exception as e:
        session.rollback()
        raise e

# Function to store an alert
def store_alert(symbol, market_type, current_price, predicted_price, signal, message=None):
    """
    Store an alert in the database
    
    Args:
        symbol: Trading symbol
        market_type: 'Forex' or 'Stock'
        current_price: Current price
        predicted_price: Predicted price
        signal: Trading signal (BUY, SELL, or HOLD)
        message: Alert message (optional)
    
    Returns:
        Created Alert object
    """
    try:
        alert = Alert(
            symbol=symbol,
            market_type=market_type,
            current_price=current_price,
            predicted_price=predicted_price,
            signal=signal,
            message=message,
            sent=False
        )
        
        session.add(alert)
        session.commit()
        
        return alert
        
    except Exception as e:
        session.rollback()
        raise e

# Function to mark an alert as sent
def mark_alert_sent(alert_id):
    """
    Mark an alert as sent
    
    Args:
        alert_id: ID of the alert
    
    Returns:
        Updated Alert object
    """
    try:
        alert = session.query(Alert).filter_by(id=alert_id).first()
        
        if alert:
            alert.sent = True
            session.commit()
            
        return alert
        
    except Exception as e:
        session.rollback()
        raise e

# Function to get or create user preferences
def get_or_create_user_preferences(session_id):
    """
    Get or create user preferences for a session
    
    Args:
        session_id: Session ID
    
    Returns:
        UserPreference object
    """
    try:
        pref = session.query(UserPreference).filter_by(session_id=session_id).first()
        
        if not pref:
            pref = UserPreference(session_id=session_id)
            session.add(pref)
            session.commit()
            
        return pref
        
    except Exception as e:
        session.rollback()
        raise e

# Function to save user preferences
def save_user_preferences(session_id, favorite_symbols=None, preferred_timeframe=None, 
                         preferred_interval=None, alert_threshold=None, telegram_enabled=None):
    """
    Save user preferences
    
    Args:
        session_id: Session ID
        favorite_symbols: List of favorite symbols
        preferred_timeframe: Preferred timeframe
        preferred_interval: Preferred interval
        alert_threshold: Alert threshold
        telegram_enabled: Whether Telegram alerts are enabled
    
    Returns:
        Updated UserPreference object
    """
    try:
        pref = get_or_create_user_preferences(session_id)
        
        if favorite_symbols is not None:
            if isinstance(favorite_symbols, list):
                pref.favorite_symbols = ','.join(favorite_symbols)
            else:
                pref.favorite_symbols = favorite_symbols
                
        if preferred_timeframe is not None:
            pref.preferred_timeframe = preferred_timeframe
            
        if preferred_interval is not None:
            pref.preferred_interval = preferred_interval
            
        if alert_threshold is not None:
            pref.alert_threshold = alert_threshold
            
        if telegram_enabled is not None:
            pref.telegram_enabled = telegram_enabled
            
        session.commit()
        
        return pref
        
    except Exception as e:
        session.rollback()
        raise e

# Function to check if data exists for a symbol and timeframe
def check_data_exists(symbol, start_date, end_date=None):
    """
    Check if data exists for a symbol and timeframe
    
    Args:
        symbol: Trading symbol
        start_date: Start date
        end_date: End date (optional, defaults to current time)
    
    Returns:
        Boolean indicating whether data exists
    """
    if end_date is None:
        end_date = datetime.utcnow()
        
    count = session.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.timestamp >= start_date,
        MarketData.timestamp <= end_date
    ).count()
    
    return count > 0

# Function to get market data from the database
def get_market_data(symbol, start_date, end_date=None):
    """
    Get market data from the database
    
    Args:
        symbol: Trading symbol
        start_date: Start date
        end_date: End date (optional, defaults to current time)
    
    Returns:
        Pandas DataFrame with market data
    """
    if end_date is None:
        end_date = datetime.utcnow()
        
    data = session.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.timestamp >= start_date,
        MarketData.timestamp <= end_date
    ).order_by(MarketData.timestamp).all()
    
    # Convert to DataFrame
    if data:
        df = pd.DataFrame([{
            'timestamp': d.timestamp,
            'Open': d.open_price,
            'High': d.high_price,
            'Low': d.low_price,
            'Close': d.close_price,
            'Volume': d.volume,
            'RSI': d.rsi,
            'MACD': d.macd,
            'MACD_Signal': d.macd_signal,
            'MACD_Hist': d.macd_hist,
            'EMA_9': d.ema_9,
            'EMA_20': d.ema_20,
            'EMA_50': d.ema_50,
            'BB_Upper': d.bb_upper,
            'BB_Middle': d.bb_middle,
            'BB_Lower': d.bb_lower
        } for d in data])
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        return df
    
    return pd.DataFrame()

# Initialize the database if this script is run directly
if __name__ == "__main__":
    init_db()