"""
Technical Analysis page for the Forex & Stock Market Prediction System.
This page provides detailed technical indicators and chart analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from data_fetcher import fetch_stock_data, fetch_forex_data
from technical_indicators import calculate_indicators
from utils import format_currency, render_indicator_info
from shared_state import initialize_session
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme, apply_chart_theme

# Page configuration
st.set_page_config(
    page_title="Technical Analysis - Forex & Stock Market Prediction",
    page_icon="📊",
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
st.title("Technical Analysis")
st.markdown("""
Analyze market data with advanced technical indicators and chart patterns.
Use these insights to identify potential trading opportunities.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Main content
try:
    # Fetch data
    with st.spinner('Fetching market data...'):
        # Fetch data based on market type
        if sidebar_state['market_type'] == "Forex":
            df = fetch_forex_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
        else:
            df = fetch_stock_data(sidebar_state['symbol'], sidebar_state['period'], sidebar_state['interval'])
            
        # Calculate technical indicators
        df = calculate_indicators(df)
    
    # Display technical indicators
    st.header(f"Technical Indicators for {sidebar_state['display_name']}")
    
    # Create tabs for different indicator groups
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    tabs = st.tabs(["Price & Volume", "Momentum Indicators", "Trend Indicators", "Volatility Indicators"])
    
    # Tab 1: Price & Volume
    with tabs[0]:
        st.subheader("Price Chart with Volume")
        
        # Create subplot with shared x-axis
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.7, 0.3])
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price",
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # Add volume bar chart
        if 'Volume' in df.columns:
            # Color volume bars based on price movement
            colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' for i in range(len(df))]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name="Volume",
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            title=f"{sidebar_state['display_name']} Price & Volume",
            yaxis_title="Price",
            yaxis2_title="Volume",
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Apply theme to chart
        fig = apply_chart_theme(fig)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Momentum Indicators
    with tabs[1]:
        st.subheader("Momentum Indicators")
        
        # Create columns for indicators
        momentum_cols = st.columns(2)
        
        # RSI Chart
        with momentum_cols[0]:
            if sidebar_state['show_rsi'] and 'RSI' in df.columns:
                st.subheader("RSI (Relative Strength Index)")
                render_indicator_info("RSI", "Measures the magnitude of recent price changes to evaluate overbought or oversold conditions.")
                
                # Create RSI figure
                fig_rsi = go.Figure()
                
                # Add RSI line
                fig_rsi.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['RSI'], 
                    name='RSI',
                    line=dict(color='#9c27b0', width=2)
                ))
                
                # Add colored background zones
                fig_rsi.add_hrect(
                    y0=70, y1=100, 
                    fillcolor="rgba(255, 0, 0, 0.1)", 
                    line_width=0,
                    annotation_text="Overbought",
                    annotation_position="top right"
                )
                
                fig_rsi.add_hrect(
                    y0=0, y1=30, 
                    fillcolor="rgba(0, 255, 0, 0.1)", 
                    line_width=0,
                    annotation_text="Oversold",
                    annotation_position="bottom right"
                )
                
                # Add oversold/overbought lines
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1)
                
                # Update layout
                fig_rsi.update_layout(
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="RSI Value",
                    yaxis=dict(range=[0, 100]),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                
                # Apply theme to chart
                fig_rsi = apply_chart_theme(fig_rsi)
                
                st.plotly_chart(fig_rsi, use_container_width=True)
                
                # RSI interpretation with styled badges
                current_rsi = df['RSI'].iloc[-1]
                
                if current_rsi > 70:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--danger-color); color: white;">OVERBOUGHT</div>
                        <div style="margin-left: 0.5rem;">Current RSI: <strong>{current_rsi:.2f}</strong> - Potential sell signal</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif current_rsi < 30:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--success-color); color: white;">OVERSOLD</div>
                        <div style="margin-left: 0.5rem;">Current RSI: <strong>{current_rsi:.2f}</strong> - Potential buy signal</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--info-color); color: white;">NEUTRAL</div>
                        <div style="margin-left: 0.5rem;">Current RSI: <strong>{current_rsi:.2f}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # MACD Chart
        with momentum_cols[1]:
            if sidebar_state['show_macd'] and 'MACD' in df.columns:
                st.subheader("MACD (Moving Average Convergence Divergence)")
                render_indicator_info("MACD", "Trend-following momentum indicator showing the relationship between two moving averages.")
                
                # Create MACD figure
                fig_macd = go.Figure()
                
                # Add MACD line
                fig_macd.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['MACD'], 
                    name='MACD',
                    line=dict(color='#2196f3', width=2)
                ))
                
                # Add Signal line
                fig_macd.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['MACD_Signal'], 
                    name='Signal',
                    line=dict(color='#ff9800', width=2)
                ))
                
                # Add Histogram with improved colors
                colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df['MACD_Hist']]
                
                fig_macd.add_trace(go.Bar(
                    x=df.index,
                    y=df['MACD_Hist'],
                    name='Histogram',
                    marker_color=colors,
                    opacity=0.7
                ))
                
                # Add zero line
                fig_macd.add_hline(y=0, line_dash="solid", line_color="gray", line_width=1)
                
                # Update layout
                fig_macd.update_layout(
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="MACD Value",
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Apply theme to chart
                fig_macd = apply_chart_theme(fig_macd)
                
                st.plotly_chart(fig_macd, use_container_width=True)
                
                # MACD interpretation with styled badges
                if df['MACD_Hist'].iloc[-1] > 0 and df['MACD_Hist'].iloc[-2] <= 0:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--success-color); color: white;">BULLISH CROSSOVER</div>
                        <div style="margin-left: 0.5rem;">MACD crossed above signal line - <strong>Potential buy signal</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                elif df['MACD_Hist'].iloc[-1] < 0 and df['MACD_Hist'].iloc[-2] >= 0:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--danger-color); color: white;">BEARISH CROSSOVER</div>
                        <div style="margin-left: 0.5rem;">MACD crossed below signal line - <strong>Potential sell signal</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                elif df['MACD_Hist'].iloc[-1] > 0:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--success-color); color: white;">BULLISH</div>
                        <div style="margin-left: 0.5rem;">MACD is above signal line - <strong>Bullish momentum</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <div class="signal-badge" style="background-color: var(--danger-color); color: white;">BEARISH</div>
                        <div style="margin-left: 0.5rem;">MACD is below signal line - <strong>Bearish momentum</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tab 3: Trend Indicators
    with tabs[2]:
        st.subheader("Trend Indicators")
        
        # Create columns for indicators
        trend_cols = st.columns(2)
        
        # EMA Chart
        with trend_cols[0]:
            if sidebar_state['show_ema'] and 'EMA_9' in df.columns:
                st.subheader("EMA (Exponential Moving Average)")
                render_indicator_info("EMA", "Exponential Moving Average gives more weight to recent prices, reacting more quickly to price changes.")
                
                fig_ema = go.Figure()
                
                # Add price
                fig_ema.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    name='Close Price',
                    line=dict(color='black', width=1)
                ))
                
                # Add EMAs
                fig_ema.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['EMA_9'], 
                    name='EMA 9',
                    line=dict(color='orange')
                ))
                fig_ema.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['EMA_20'], 
                    name='EMA 20',
                    line=dict(color='blue')
                ))
                fig_ema.add_trace(go.Scatter(
                    x=df.index, 
                    y=df['EMA_50'], 
                    name='EMA 50',
                    line=dict(color='green')
                ))
                
                fig_ema.update_layout(
                    height=400,
                    xaxis_title="Date",
                    yaxis_title="Price"
                )
                
                st.plotly_chart(fig_ema, use_container_width=True)
                
                # EMA interpretation
                if df['Close'].iloc[-1] > df['EMA_50'].iloc[-1] and df['EMA_9'].iloc[-1] > df['EMA_20'].iloc[-1]:
                    st.success("Price above EMA 50 and EMA 9 above EMA 20 - Strong uptrend")
                elif df['Close'].iloc[-1] < df['EMA_50'].iloc[-1] and df['EMA_9'].iloc[-1] < df['EMA_20'].iloc[-1]:
                    st.warning("Price below EMA 50 and EMA 9 below EMA 20 - Strong downtrend")
                elif df['Close'].iloc[-1] > df['EMA_20'].iloc[-1]:
                    st.info("Price above EMA 20 - Moderate uptrend")
                else:
                    st.info("Price below EMA 20 - Moderate downtrend")
        
        # Add another trend indicator in the future
        with trend_cols[1]:
            st.subheader("Price Rate of Change (ROC)")
            st.info("Shows the percentage change in price over a specific period, indicating momentum.")
            
            # Calculate ROC for different periods
            periods = [5, 10, 20]
            for period in periods:
                df[f'ROC_{period}'] = df['Close'].pct_change(period) * 100
            
            # Create ROC chart
            fig_roc = go.Figure()
            
            for period in periods:
                fig_roc.add_trace(go.Scatter(
                    x=df.index,
                    y=df[f'ROC_{period}'],
                    name=f'ROC {period}',
                ))
            
            # Add zero line
            fig_roc.add_hline(y=0, line_dash="dash", line_color="black")
            
            fig_roc.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Rate of Change (%)"
            )
            
            st.plotly_chart(fig_roc, use_container_width=True)
            
            # ROC interpretation
            current_roc = df['ROC_10'].iloc[-1]
            if current_roc > 5:
                st.success(f"10-day ROC: {current_roc:.2f}% - Strong positive momentum")
            elif current_roc < -5:
                st.warning(f"10-day ROC: {current_roc:.2f}% - Strong negative momentum")
            else:
                st.info(f"10-day ROC: {current_roc:.2f}% - Neutral momentum")
    
    # Tab 4: Volatility Indicators
    with tabs[3]:
        st.subheader("Volatility Indicators")
        
        # Create columns for indicators
        volatility_cols = st.columns(2)
        
        # Bollinger Bands
        with volatility_cols[0]:
            st.subheader("Bollinger Bands")
            st.info("Bollinger Bands consist of a middle band (20-day SMA) with upper and lower bands at 2 standard deviations, indicating volatility.")
            
            # Calculate Bollinger Bands
            window = 20
            df['SMA_20'] = df['Close'].rolling(window=window).mean()
            df['STD_20'] = df['Close'].rolling(window=window).std()
            df['BB_Upper'] = df['SMA_20'] + 2 * df['STD_20']
            df['BB_Lower'] = df['SMA_20'] - 2 * df['STD_20']
            
            # Create Bollinger Bands chart
            fig_bb = go.Figure()
            
            # Add price
            fig_bb.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                name='Close Price',
                line=dict(color='black')
            ))
            
            # Add Bollinger Bands
            fig_bb.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                name='SMA 20',
                line=dict(color='blue')
            ))
            fig_bb.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                name='Upper Band',
                line=dict(color='red', dash='dash')
            ))
            fig_bb.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                name='Lower Band',
                line=dict(color='green', dash='dash')
            ))
            
            fig_bb.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Price"
            )
            
            st.plotly_chart(fig_bb, use_container_width=True)
            
            # Bollinger Bands interpretation
            current_price = df['Close'].iloc[-1]
            upper_band = df['BB_Upper'].iloc[-1]
            lower_band = df['BB_Lower'].iloc[-1]
            
            if current_price > upper_band:
                st.warning(f"Price ({format_currency(current_price)}) above upper band ({format_currency(upper_band)}) - Overbought condition")
            elif current_price < lower_band:
                st.success(f"Price ({format_currency(current_price)}) below lower band ({format_currency(lower_band)}) - Oversold condition")
            else:
                st.info(f"Price ({format_currency(current_price)}) within bands - Normal volatility")
        
        # Average True Range (ATR)
        with volatility_cols[1]:
            st.subheader("Average True Range (ATR)")
            st.info("ATR measures market volatility by decomposing the entire range of an asset price for a period.")
            
            # Calculate ATR
            df['TR'] = np.maximum(
                np.maximum(
                    df['High'] - df['Low'],
                    abs(df['High'] - df['Close'].shift(1))
                ),
                abs(df['Low'] - df['Close'].shift(1))
            )
            df['ATR_14'] = df['TR'].rolling(window=14).mean()
            
            # Create ATR chart
            fig_atr = go.Figure()
            
            fig_atr.add_trace(go.Scatter(
                x=df.index,
                y=df['ATR_14'],
                name='ATR (14)',
                line=dict(color='purple')
            ))
            
            fig_atr.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="ATR Value"
            )
            
            st.plotly_chart(fig_atr, use_container_width=True)
            
            # ATR interpretation
            current_atr = df['ATR_14'].iloc[-1]
            avg_price = df['Close'].mean()
            atr_percent = (current_atr / avg_price) * 100
            
            if atr_percent > 3:
                st.warning(f"ATR: {format_currency(current_atr)} ({atr_percent:.2f}% of avg price) - High volatility")
            elif atr_percent < 1:
                st.info(f"ATR: {format_currency(current_atr)} ({atr_percent:.2f}% of avg price) - Low volatility")
            else:
                st.info(f"ATR: {format_currency(current_atr)} ({atr_percent:.2f}% of avg price) - Moderate volatility")
    
    # Close the custom-card div for tabs
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Technical Analysis Summary
    st.header("Technical Analysis Summary")
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # Create a summary of all indicators
    summary_cols = st.columns(3)
    
    with summary_cols[0]:
        st.subheader("Momentum")
        
        if 'RSI' in df.columns:
            current_rsi = df['RSI'].iloc[-1]
            if current_rsi > 70:
                st.warning(f"RSI: {current_rsi:.2f} - Overbought")
            elif current_rsi < 30:
                st.success(f"RSI: {current_rsi:.2f} - Oversold")
            else:
                st.info(f"RSI: {current_rsi:.2f} - Neutral")
        
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]:
                st.success("MACD: Above signal line - Bullish")
            else:
                st.warning("MACD: Below signal line - Bearish")
    
    with summary_cols[1]:
        st.subheader("Trend")
        
        if 'EMA_20' in df.columns and 'EMA_50' in df.columns:
            if df['Close'].iloc[-1] > df['EMA_50'].iloc[-1]:
                st.success("Price above EMA 50 - Uptrend")
            else:
                st.warning("Price below EMA 50 - Downtrend")
            
            if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1]:
                st.success("EMA 20 above EMA 50 - Bullish crossover")
            else:
                st.warning("EMA 20 below EMA 50 - Bearish crossover")
    
    with summary_cols[2]:
        st.subheader("Volatility")
        
        if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
            bb_width = (df['BB_Upper'].iloc[-1] - df['BB_Lower'].iloc[-1]) / df['SMA_20'].iloc[-1]
            st.info(f"Bollinger Band Width: {bb_width:.2f}")
            
            if df['Close'].iloc[-1] > df['BB_Upper'].iloc[-1]:
                st.warning("Price above upper Bollinger Band - Overbought")
            elif df['Close'].iloc[-1] < df['BB_Lower'].iloc[-1]:
                st.success("Price below lower Bollinger Band - Oversold")
        
        if 'ATR_14' in df.columns:
            st.info(f"ATR (14): {df['ATR_14'].iloc[-1]:.4f}")
    
    # Overall signal
    st.subheader("Overall Signal")
    
    # Count bullish and bearish signals
    bullish_signals = 0
    bearish_signals = 0
    
    # RSI
    if 'RSI' in df.columns:
        if df['RSI'].iloc[-1] < 30:
            bullish_signals += 1
        elif df['RSI'].iloc[-1] > 70:
            bearish_signals += 1
    
    # MACD
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]:
            bullish_signals += 1
        else:
            bearish_signals += 1
    
    # EMA
    if 'EMA_20' in df.columns and 'EMA_50' in df.columns:
        if df['Close'].iloc[-1] > df['EMA_50'].iloc[-1]:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1]:
            bullish_signals += 1
        else:
            bearish_signals += 1
    
    # Bollinger Bands
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        if df['Close'].iloc[-1] < df['BB_Lower'].iloc[-1]:
            bullish_signals += 1
        elif df['Close'].iloc[-1] > df['BB_Upper'].iloc[-1]:
            bearish_signals += 1
    
    # Determine overall signal
    if bullish_signals > bearish_signals + 1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div class="signal-badge" style="background-color: var(--success-color); color: white; font-size: 1.2rem; padding: 0.5rem 1rem;">STRONG BUY</div>
            <div style="margin-left: 1rem; font-size: 1.1rem;">Bullish: {bullish_signals}, Bearish: {bearish_signals}</div>
        </div>
        """, unsafe_allow_html=True)
    elif bullish_signals > bearish_signals:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div class="signal-badge" style="background-color: var(--success-color); color: white; font-size: 1.2rem; padding: 0.5rem 1rem;">MODERATE BUY</div>
            <div style="margin-left: 1rem; font-size: 1.1rem;">Bullish: {bullish_signals}, Bearish: {bearish_signals}</div>
        </div>
        """, unsafe_allow_html=True)
    elif bearish_signals > bullish_signals + 1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div class="signal-badge" style="background-color: var(--danger-color); color: white; font-size: 1.2rem; padding: 0.5rem 1rem;">STRONG SELL</div>
            <div style="margin-left: 1rem; font-size: 1.1rem;">Bullish: {bullish_signals}, Bearish: {bearish_signals}</div>
        </div>
        """, unsafe_allow_html=True)
    elif bearish_signals > bullish_signals:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div class="signal-badge" style="background-color: var(--danger-color); color: white; font-size: 1.2rem; padding: 0.5rem 1rem;">MODERATE SELL</div>
            <div style="margin-left: 1rem; font-size: 1.1rem;">Bullish: {bullish_signals}, Bearish: {bearish_signals}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div class="signal-badge" style="background-color: var(--warning-color); color: black; font-size: 1.2rem; padding: 0.5rem 1rem;">NEUTRAL</div>
            <div style="margin-left: 1rem; font-size: 1.1rem;">Bullish: {bullish_signals}, Bearish: {bearish_signals}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Close the custom-card div for summary
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your input parameters and try again.")