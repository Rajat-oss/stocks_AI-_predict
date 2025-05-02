"""
Alerts Management page for the Forex & Stock Market Prediction System.
This page allows users to manage and configure trading alerts.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import custom modules
from shared_state import initialize_session
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme, apply_chart_theme
import database as db
from telegram_alerts import send_telegram_alert, send_pending_alerts
from utils import format_currency

# Page configuration
st.set_page_config(
    page_title="Alerts Management - Forex & Stock Market Prediction",
    page_icon="🔔",
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
st.title("Alerts Management")
st.markdown("""
Configure and manage your trading alerts. Receive notifications when our AI predicts significant price movements.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Alert settings
st.sidebar.header("Alert Settings")
enable_alerts = st.sidebar.checkbox("Enable Telegram Alerts", value=st.session_state.get('enable_alerts', False))
st.session_state['enable_alerts'] = enable_alerts

alert_threshold = st.sidebar.slider("Alert Threshold (%)", 0.0, 5.0, 1.0, 0.1)
st.session_state['alert_threshold'] = alert_threshold

# Save preferences
db.save_user_preferences(
    st.session_state['session_id'],
    telegram_enabled=enable_alerts,
    alert_threshold=alert_threshold
)

# Main content
try:
    # Telegram setup section
    st.header("Telegram Alert Setup")
    
    setup_cols = st.columns([2, 1])
    
    with setup_cols[0]:
        st.write("""
        To receive alerts via Telegram, you need to:
        1. Create a Telegram bot using BotFather
        2. Get your bot token and chat ID
        3. Configure these in the application settings
        """)
        
        # Check if Telegram credentials are configured
        telegram_configured = False
        
        try:
            import os
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            if bot_token and chat_id:
                telegram_configured = True
        except Exception:
            telegram_configured = False
        
        if telegram_configured:
            st.success("Telegram is configured and ready to send alerts.")
        else:
            st.warning("Telegram is not configured. Please set up your credentials in the .env file.")
            
            with st.expander("How to set up Telegram credentials"):
                st.write("""
                1. Talk to [BotFather](https://t.me/botfather) on Telegram
                2. Create a new bot with the command `/newbot`
                3. Copy the bot token provided by BotFather
                4. Start a chat with your bot
                5. Get your chat ID using the `/getid` command in your bot
                6. Add these credentials to your .env file:
                ```
                TELEGRAM_BOT_TOKEN=your_bot_token_here
                TELEGRAM_CHAT_ID=your_chat_id_here
                ```
                """)
    
    with setup_cols[1]:
        # Test alert button
        if st.button("Send Test Alert"):
            if telegram_configured:
                try:
                    test_message = f"""
*TEST ALERT*

Symbol: {sidebar_state['display_name']}
Current Price: $100.00
Test Message: This is a test alert

_Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""
                    send_telegram_alert(message=test_message)
                    st.success("Test alert sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send test alert: {str(e)}")
            else:
                st.error("Cannot send test alert. Telegram is not configured.")
    
    # Alert history
    st.header("Alert History")
    
    # Get alerts from database
    session = db.get_session()
    try:
        alerts = session.query(db.Alert).order_by(db.Alert.timestamp.desc()).limit(50).all()
        
        if alerts:
            # Convert to dataframe
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    'ID': alert.id,
                    'Symbol': alert.symbol,
                    'Market': alert.market_type,
                    'Timestamp': alert.timestamp,
                    'Current Price': format_currency(alert.current_price),
                    'Predicted Price': format_currency(alert.predicted_price),
                    'Signal': alert.signal,
                    'Sent': "Yes" if alert.sent else "No"
                })
            
            alerts_df = pd.DataFrame(alerts_data)
            
            # Display alerts
            st.dataframe(alerts_df, use_container_width=True)
            
            # Resend pending alerts
            pending_count = sum(1 for alert in alerts if not alert.sent)
            
            if pending_count > 0:
                if st.button(f"Resend {pending_count} Pending Alerts"):
                    sent_count = send_pending_alerts()
                    st.success(f"Sent {sent_count} pending alerts.")
        else:
            st.info("No alerts found in the database.")
    finally:
        session.close()
    
    # Alert configuration
    st.header("Alert Configuration")
    
    config_cols = st.columns(2)
    
    with config_cols[0]:
        st.subheader("Alert Conditions")
        
        # Price change threshold
        st.write("**Price Change Threshold**")
        st.write(f"Current setting: {alert_threshold}%")
        st.write("Alerts will be triggered when the predicted price change exceeds this threshold.")
        
        # Alert frequency
        st.write("**Alert Frequency**")
        alert_frequency = st.radio("How often would you like to receive alerts?", 
                                  ["Every prediction", "Daily summary", "Only significant changes"])
        
        if alert_frequency != "Every prediction":
            st.info("This feature will be implemented in a future update.")
    
    with config_cols[1]:
        st.subheader("Alert Content")
        
        # Alert content options
        st.write("**Alert Information**")
        
        include_options = {
            "include_price": st.checkbox("Include current price", value=True),
            "include_prediction": st.checkbox("Include predicted price", value=True),
            "include_signal": st.checkbox("Include trading signal (BUY/SELL/HOLD)", value=True),
            "include_chart": st.checkbox("Include chart image", value=False)
        }
        
        if include_options["include_chart"]:
            st.info("Chart images in alerts will be implemented in a future update.")
    
    # Custom alerts
    st.header("Custom Price Alerts")
    
    st.write("""
    Set up custom price alerts for specific price levels.
    You'll receive a notification when the price crosses these levels.
    """)
    
    custom_cols = st.columns(2)
    
    with custom_cols[0]:
        # Price target
        price_target = st.number_input("Price Target", min_value=0.0, step=0.01)
        
        # Alert direction
        alert_direction = st.radio("Alert Direction", ["Price rises above target", "Price falls below target"])
    
    with custom_cols[1]:
        # Alert name
        alert_name = st.text_input("Alert Name (optional)", placeholder="e.g., AAPL resistance level")
        
        # Set alert button
        if st.button("Set Custom Alert"):
            if price_target > 0:
                # In a real implementation, you would store this in the database
                st.success(f"Custom alert set: {alert_direction} {format_currency(price_target)}")
                st.info("Custom price alerts will be fully implemented in a future update.")
            else:
                st.error("Please enter a valid price target.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")