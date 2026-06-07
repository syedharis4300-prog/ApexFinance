import streamlit as st
import yfinance as yf
import datetime
import pandas as pd

# Cache news fetching for 10 minutes to save API requests
@st.cache_data(ttl=600)
def fetch_raw_news(symbols):
    all_news = []
    seen_titles = set()
    
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            news_items = ticker.news
            if not news_items:
                continue
                
            for item in news_items:
                title = item.get("title", "")
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                
                # Extract details
                publish_time = item.get("providerPublishTime", 0)
                publisher = item.get("publisher", "Unknown Source")
                link = item.get("link", "#")
                
                all_news.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "time": publish_time,
                    "ticker": sym
                })
        except Exception:
            continue
            
    # Sort by time descending
    all_news.sort(key=lambda x: x["time"], reverse=True)
    return all_news[:15] # Return top 15 news items

def analyze_sentiment(title):
    title_lower = title.lower()
    
    bullish_keywords = [
        "gain", "rise", "grow", "growth", "positive", "surge", "jump", "high", "record", 
        "beat", "upgrade", "buy", "optimistic", "profit", "rally", "soar", "bullish", 
        "upbeat", "boost", "strong", "outperform", "higher"
    ]
    
    bearish_keywords = [
        "loss", "fall", "decline", "negative", "drop", "slip", "low", "miss", "downgrade", 
        "sell", "pessimistic", "debt", "crash", "slide", "slump", "recession", "bearish", 
        "risk", "sink", "hit", "weak", "concern", "plunge", "down", "lower"
    ]
    
    bullish_score = sum(1 for word in bullish_keywords if word in title_lower)
    bearish_score = sum(1 for word in bearish_keywords if word in title_lower)
    
    if bullish_score > bearish_score:
        return "BULLISH", "sentiment-bullish"
    elif bearish_score > bullish_score:
        return "BEARISH", "sentiment-bearish"
    else:
        return "NEUTRAL", "sentiment-neutral"

def render_news_tab():
    st.markdown("## 📰 Financial News & Market Sentiment")
    st.markdown("Aggregated live news feed across major market tickers with heuristic sentiment tags.")
    
    symbols_to_query = ["^GSPC", "AAPL", "MSFT", "TSLA", "BTC-USD"]
    
    with st.spinner("Fetching latest market headlines..."):
        news = fetch_raw_news(symbols_to_query)
        
    if not news:
        # Fallback news if API returns empty/fails
        st.warning("Could not retrieve live news at this time. Here are some general finance market feeds.")
        news = [
            {
                "title": "Fed hints at keeping interest rates steady amid stubborn inflation data",
                "publisher": "Financial Times",
                "link": "https://finance.yahoo.com",
                "time": int(datetime.datetime.now().timestamp()) - 3600,
                "ticker": "^GSPC"
            },
            {
                "title": "Bitcoin consolidation continues as long-term holders stack BTC",
                "publisher": "CoinDesk",
                "link": "https://finance.yahoo.com",
                "time": int(datetime.datetime.now().timestamp()) - 7200,
                "ticker": "BTC-USD"
            },
            {
                "title": "Apple expands AI ecosystem integrations in upcoming iOS releases",
                "publisher": "Bloomberg",
                "link": "https://finance.yahoo.com",
                "time": int(datetime.datetime.now().timestamp()) - 10800,
                "ticker": "AAPL"
            }
        ]
        
    for item in news:
        # Parse time
        try:
            pub_date = datetime.datetime.fromtimestamp(item["time"])
            time_str = pub_date.strftime("%B %d, %Y - %I:%M %p")
        except Exception:
            time_str = "Recently"
            
        sentiment_label, sentiment_class = analyze_sentiment(item["title"])
        
        # Display news card
        news_html = f"""
        <div class="news-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:12px; font-weight:600; color:#0ea5e9; background:rgba(14,165,233,0.1); padding:2px 8px; border-radius:4px;">{item["ticker"]}</span>
                <span class="sentiment-badge {sentiment_class}">{sentiment_label}</span>
            </div>
            <a href="{item["link"]}" target="_blank" class="news-title">{item["title"]}</a>
            <div class="news-meta">
                <span>Published by <strong>{item["publisher"]}</strong></span> &bull; <span>{time_str}</span>
            </div>
        </div>
        """
        st.markdown(news_html, unsafe_allow_html=True)
