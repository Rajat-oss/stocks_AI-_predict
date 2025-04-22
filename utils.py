import streamlit as st

def format_currency(value):
    """
    Format a numeric value as currency
    
    Args:
        value: Numeric value to format
        
    Returns:
        Formatted string
    """
    # Check if the value is large or small to determine format
    if abs(value) >= 1000:
        return f"${value:.2f}"
    elif abs(value) >= 1:
        return f"${value:.4f}"
    else:
        return f"${value:.6f}"

def render_indicator_info(name, description):
    """
    Render information about a technical indicator
    
    Args:
        name: Name of the indicator
        description: Description of the indicator
    """
    with st.expander(f"What is {name}?"):
        st.write(description)

def color_signal(signal):
    """
    Return appropriate color for trading signal
    
    Args:
        signal: The trading signal (BUY/SELL/HOLD)
        
    Returns:
        Color string
    """
    if signal == "BUY":
        return "green"
    elif signal == "SELL":
        return "red"
    else:  # HOLD
        return "orange"

def get_signal_emoji(signal):
    """
    Return emoji for trading signal
    
    Args:
        signal: The trading signal (BUY/SELL/HOLD)
        
    Returns:
        Emoji string
    """
    if signal == "BUY":
        return "🟢"
    elif signal == "SELL":
        return "🔴"
    else:  # HOLD
        return "🟠"
