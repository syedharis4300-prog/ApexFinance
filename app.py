import streamlit as st

# Configure page metadata and layout.
# Note: st.set_page_config MUST be the very first Streamlit command in the script.
st.set_page_config(
    page_title="ApexFinance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from styles import inject_custom_css
from market import render_market_tab
from portfolio import render_portfolio_tab
from budget import render_budget_tab
from news import render_news_tab

def main():
    # Inject premium styles
    inject_custom_css()
    
    # Sidebar navigation
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='margin:0; font-size: 24px; color: #ffffff;'>⚡ <span class='gradient-text'>ApexFinance</span></h2>
        <p style='color: #6b7280; font-size: 12px; margin-top:5px;'>Intelligent Wealth Tracker</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    navigation_options = {
        "📈 Market Overview": "market",
        "💼 Portfolio Tracker": "portfolio",
        "📊 Budget & Planning": "budget",
        "📰 Sentiment News": "news"
    }
    
    selected_page = st.sidebar.radio(
        "Navigation",
        list(navigation_options.keys()),
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Sidebar footer
    st.sidebar.markdown("""
    <div style='position: fixed; bottom: 20px; font-size: 11px; color: #4b5563;'>
        ApexFinance Engine v1.0.0<br/>
        Local Database Connected
    </div>
    """, unsafe_allow_html=True)
    
    # Header Banner on Main Area
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 2rem;">
        <div>
            <h1 style="margin:0;"><span class="gradient-text">ApexFinance</span> Dashboard</h1>
            <p style="color: #9ca3af; margin: 5px 0 0 0;">Real-time analytical terminal for personal wealth and asset tracking.</p>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 8px; font-size:13px; color: #9ca3af;">
            🟢 System Active
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Route to sub-components based on user selection
    page_key = navigation_options[selected_page]
    
    if page_key == "market":
        render_market_tab()
    elif page_key == "portfolio":
        render_portfolio_tab()
    elif page_key == "budget":
        render_budget_tab()
    elif page_key == "news":
        render_news_tab()

if __name__ == "__main__":
    main()
