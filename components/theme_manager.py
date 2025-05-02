"""
Theme manager component for the Streamlit multi-page application.
This module provides functionality for switching between light and dark modes.
"""

import streamlit as st
import os

def load_css():
    """Load custom CSS"""
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "css", "style.css")
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
    return css

def apply_theme():
    """Apply the current theme to the page"""
    # Always use dark theme
    st.session_state['theme'] = 'dark'
    
    # Load custom CSS
    css = load_css()
    
    # Apply CSS
    st.markdown(css, unsafe_allow_html=True)
    
    # Add theme attribute to html
    theme_script = """
    <script>
        document.querySelector('html').setAttribute('data-theme', 'dark');
    </script>
    """
    st.markdown(theme_script, unsafe_allow_html=True)

def render_card(content, key=None):
    """Render content inside a styled card"""
    card_html = f"""
    <div class="custom-card" {'id="' + key + '"' if key else ''}>
        {content}
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

def get_chart_theme():
    """Get the current theme's chart colors"""
    # Always return dark theme
    return {
        'bgcolor': '#343a40',
        'gridcolor': 'rgba(255, 255, 255, 0.1)',
        'linecolor': '#495057',
        'paper_bgcolor': '#343a40',
        'plot_bgcolor': '#343a40',
        'font': {'color': '#f8f9fa'},
        'colorway': ['#0d6efd', '#dc3545', '#198754', '#ffc107', '#0dcaf0', '#6f42c1', '#fd7e14', '#20c997']
    }

def apply_chart_theme(fig):
    """Apply the current theme to a plotly figure"""
    theme = get_chart_theme()
    
    fig.update_layout(
        paper_bgcolor=theme['paper_bgcolor'],
        plot_bgcolor=theme['plot_bgcolor'],
        font=theme['font'],
        colorway=theme['colorway'],
        xaxis=dict(
            gridcolor=theme['gridcolor'],
            zerolinecolor=theme['gridcolor'],
            linecolor=theme['linecolor']
        ),
        yaxis=dict(
            gridcolor=theme['gridcolor'],
            zerolinecolor=theme['gridcolor'],
            linecolor=theme['linecolor']
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    return fig