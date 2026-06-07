import streamlit as st

def inject_custom_css():
    """Injects custom CSS to style the Streamlit app to look like a premium modern SaaS dashboard."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global styling */
    * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Main container background */
    .stApp {
        background-color: #0d0f14;
        color: #f3f4f6;
    }
    
    /* Clean sidebar */
    [data-testid="stSidebar"] {
        background-color: #121620;
        border-right: 1px solid #1f293d;
    }
    
    [data-testid="stSidebar"] * {
        color: #9ca3af;
    }
    
    /* Custom container glassmorphism cards */
    .dashboard-card {
        background: rgba(22, 28, 45, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(14, 165, 233, 0.15);
        border-color: rgba(14, 165, 233, 0.3);
    }
    
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(22, 28, 45, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
    }
    
    .metric-card.gain::after {
        background: linear-gradient(90deg, #10b981, #059669);
    }
    
    .metric-card.loss::after {
        background: linear-gradient(90deg, #ef4444, #dc2626);
    }
    
    .metric-title {
        font-size: 14px;
        color: #9ca3af;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 28px;
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    
    .metric-change {
        font-size: 14px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .change-up {
        color: #10b981;
    }
    
    .change-down {
        color: #ef4444;
    }
    
    .change-neutral {
        color: #9ca3af;
    }

    /* Subsections and typography */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #0ea5e9 0%, #a855f7 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Input fields and buttons */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #161c2d !important;
        border: 1px solid #2d3748 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #0ea5e9 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: opacity 0.2s;
    }
    
    .stButton>button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3) !important;
    }
    
    /* Table modifications */
    .dataframe {
        background-color: #161c2d !important;
        border: 1px solid #1f293d !important;
        color: #f3f4f6 !important;
    }
    
    /* Footer hide */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Adjust main content padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* News card style */
    .news-card {
        background: rgba(22, 28, 45, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    
    .news-card:hover {
        transform: translateX(4px);
        border-color: rgba(14, 165, 233, 0.2);
    }
    
    .news-title {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        text-decoration: none;
        margin-bottom: 8px;
        display: block;
    }
    
    .news-title:hover {
        color: #0ea5e9;
    }
    
    .news-meta {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .sentiment-bullish {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .sentiment-bearish {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .sentiment-neutral {
        background-color: rgba(156, 163, 175, 0.15);
        color: #9ca3af;
        border: 1px solid rgba(156, 163, 175, 0.3);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_metric_card(title, value, change_str, change_direction="up"):
    """Renders a beautiful glassmorphic metric card with custom styling."""
    direction_class = "change-up"
    arrow = "▲"
    card_class = "gain"
    
    if change_direction == "down":
        direction_class = "change-down"
        arrow = "▼"
        card_class = "loss"
    elif change_direction == "neutral":
        direction_class = "change-neutral"
        arrow = "●"
        card_class = ""
        
    html = f"""
    <div class="metric-card {card_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-change {direction_class}">
            <span>{arrow}</span> <span>{change_str}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
