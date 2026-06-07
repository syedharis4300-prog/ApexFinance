import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from styles import render_metric_card

# Cache ticker information for 10 minutes to avoid hitting rate limits
@st.cache_data(ttl=600)
def get_ticker_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # Safeguard if info is empty or errors
        if not info or len(info) < 5:
            return None
        return info
    except Exception as e:
        st.warning(f"Could not fetch info for symbol {symbol}: {str(e)}")
        return None

# Cache historical data for 5 minutes
@st.cache_data(ttl=300)
def get_historical_data(symbol, period="1mo", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Error fetching history for {symbol}: {str(e)}")
        return None

def format_number(val, is_currency=True, decimals=2):
    if val is None or pd.isna(val):
        return "N/A"
    
    prefix = "$" if is_currency else ""
    
    if abs(val) >= 1e12:
        return f"{prefix}{val / 1e12:.2f}T"
    elif abs(val) >= 1e9:
        return f"{prefix}{val / 1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"{prefix}{val / 1e6:.2f}M"
    else:
        return f"{prefix}{val:,.{decimals}f}"

def render_market_tab():
    st.markdown("## 📈 Market Analysis & Stock Tracker")
    st.markdown("Search for real-time stocks, cryptocurrencies, indices, or ETFs.")
    
    # Pre-defined quick tickers
    quick_tickers = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "NVIDIA": "NVDA",
        "Tesla": "TSLA",
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD"
    }
    
    cols = st.columns(len(quick_tickers))
    selected_quick_ticker = None
    
    # We display them as small buttons or inline options
    st.markdown("##### Quick Select:")
    btn_cols = st.columns(len(quick_tickers))
    for i, (name, symbol) in enumerate(quick_tickers.items()):
        if btn_cols[i].button(name, key=f"quick_{symbol}", use_container_width=True):
            st.session_state.search_symbol = symbol

    # Search Bar
    if "search_symbol" not in st.session_state:
        st.session_state.search_symbol = "AAPL"
        
    search_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, BTC-USD, TSLA, ^GSPC):", 
                                  value=st.session_state.search_symbol).upper().strip()
    
    if search_input:
        st.session_state.search_symbol = search_input
        
    symbol = st.session_state.search_symbol
    
    with st.spinner(f"Fetching data for {symbol}..."):
        info = get_ticker_info(symbol)
        
        # Period/interval map
        periods = {
            "1 Day": ("1d", "5m"),
            "5 Days": ("5d", "15m"),
            "1 Month": ("1mo", "1d"),
            "6 Months": ("6mo", "1d"),
            "1 Year": ("1y", "1d"),
            "5 Years": ("5y", "1d"),
            "Max": ("max", "1wk")
        }
        
        col_ctrl1, col_ctrl2 = st.columns([1, 2])
        
        with col_ctrl1:
            time_range = st.selectbox("Time Horizon", list(periods.keys()), index=2)
            chart_type = st.radio("Chart Style", ["Line", "Candlestick"], horizontal=True)
            
        with col_ctrl2:
            st.markdown("**Technical Indicators**")
            show_sma20 = st.checkbox("Simple Moving Average (20-day SMA)", value=False)
            show_sma50 = st.checkbox("Simple Moving Average (50-day SMA)", value=False)
            show_ema20 = st.checkbox("Exponential Moving Average (20-day EMA)", value=False)
            show_bb = st.checkbox("Bollinger Bands (20-day, 2σ)", value=False)
            
        period_val, interval_val = periods[time_range]
        df = get_historical_data(symbol, period=period_val, interval=interval_val)
        
        if df is None or df.empty:
            st.error(f"Could not retrieve historical data for symbol '{symbol}'. Verify the ticker is correct.")
            return

        # Fetch current price and change details
        if info:
            name = info.get("longName", info.get("shortName", symbol))
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            
            # fallback for crypto or assets that don't have currentPrice
            if current_price is None and not df.empty:
                current_price = df['Close'].iloc[-1]
            if prev_close is None and not df.empty and len(df) > 1:
                prev_close = df['Close'].iloc[-2]
                
            if current_price and prev_close:
                price_change = current_price - prev_close
                pct_change = (price_change / prev_close) * 100
                change_dir = "up" if price_change >= 0 else "down"
                change_str = f"${price_change:+,.2f} ({pct_change:+,.2f}%) Today"
            else:
                current_price = df['Close'].iloc[-1] if not df.empty else 0
                change_str = "Change data unavailable"
                change_dir = "neutral"
        else:
            name = symbol
            current_price = df['Close'].iloc[-1] if not df.empty else 0
            if len(df) > 1:
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                pct_change = (price_change / df['Close'].iloc[-2]) * 100
                change_dir = "up" if price_change >= 0 else "down"
                change_str = f"${price_change:+,.2f} ({pct_change:+,.2f}%) Today"
            else:
                change_str = "Change data unavailable"
                change_dir = "neutral"

        # Display header
        st.markdown(f"### {name} <span style='color: #6b7280; font-size:18px;'>({symbol})</span>", unsafe_allow_html=True)
        
        # Display high level metrics
        m1, m2, m3, m4 = st.columns(4)
        
        currency_symbol = info.get("currency", "USD") if info else "USD"
        
        with m1:
            render_metric_card(
                "Current Price",
                f"{current_price:,.2f} {currency_symbol}",
                change_str,
                change_direction=change_dir
            )
            
        with m2:
            high_price = info.get("dayHigh") if info else df['High'].max()
            low_price = info.get("dayLow") if info else df['Low'].min()
            if high_price and low_price:
                render_metric_card(
                    "24h High / Low",
                    f"{high_price:,.2f} / {low_price:,.2f}",
                    f"Range today ({currency_symbol})",
                    change_direction="neutral"
                )
            else:
                render_metric_card("24h Range", "N/A", "Data unavailable", "neutral")
                
        with m3:
            volume = info.get("volume") if info else df['Volume'].iloc[-1]
            avg_volume = info.get("averageVolume")
            vol_str = format_number(volume, is_currency=False)
            avg_vol_str = format_number(avg_volume, is_currency=False) if avg_volume else "N/A"
            render_metric_card(
                "Volume",
                vol_str,
                f"Avg Vol: {avg_vol_str}",
                change_direction="neutral"
            )
            
        with m4:
            mcap = info.get("marketCap") if info else None
            mcap_str = format_number(mcap) if mcap else "N/A"
            pe = info.get("trailingPE") if info else None
            pe_str = f"{pe:.2f}" if pe else "N/A"
            render_metric_card(
                "Market Cap",
                mcap_str,
                f"P/E Ratio: {pe_str}",
                change_direction="neutral"
            )

        # Plotly figure creation
        # Compute indicator series
        df_ind = df.copy()
        if show_sma20:
            df_ind['SMA20'] = df_ind['Close'].rolling(window=20).mean()
        if show_sma50:
            df_ind['SMA50'] = df_ind['Close'].rolling(window=50).mean()
        if show_ema20:
            df_ind['EMA20'] = df_ind['Close'].ewm(span=20, adjust=False).mean()
        if show_bb:
            df_ind['BB_mid'] = df_ind['Close'].rolling(window=20).mean()
            df_ind['BB_std'] = df_ind['Close'].rolling(window=20).std()
            df_ind['BB_up'] = df_ind['BB_mid'] + (df_ind['BB_std'] * 2)
            df_ind['BB_down'] = df_ind['BB_mid'] - (df_ind['BB_std'] * 2)

        # Create plot with primary and secondary Y-axis (Price & Volume)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.08, 
            row_heights=[0.8, 0.2]
        )
        
        # Color palettes
        line_color = '#0ea5e9' if change_dir == 'up' else '#ef4444'
        fill_color = 'rgba(14, 165, 233, 0.1)' if change_dir == 'up' else 'rgba(239, 68, 68, 0.1)'
        
        # Primary price trace
        if chart_type == "Line":
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index, 
                    y=df_ind['Close'], 
                    mode='lines', 
                    name='Price',
                    line=dict(color=line_color, width=2.5),
                    fill='tozeroy',
                    fillcolor=fill_color,
                    hovertemplate='Price: %{y:,.2f}<extra></extra>'
                ),
                row=1, col=1
            )
        else: # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df_ind.index,
                    open=df_ind['Open'],
                    high=df_ind['High'],
                    low=df_ind['Low'],
                    close=df_ind['Close'],
                    name='Price',
                    increasing_line_color='#10b981', 
                    decreasing_line_color='#ef4444',
                    increasing_fillcolor='#10b981',
                    decreasing_fillcolor='#ef4444'
                ),
                row=1, col=1
            )

        # Overlays
        if show_sma20:
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['SMA20'], mode='lines', name='SMA 20', line=dict(color='#f59e0b', width=1.5, dash='dash')),
                row=1, col=1
            )
        if show_sma50:
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['SMA50'], mode='lines', name='SMA 50', line=dict(color='#8b5cf6', width=1.5, dash='dash')),
                row=1, col=1
            )
        if show_ema20:
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['EMA20'], mode='lines', name='EMA 20', line=dict(color='#ec4899', width=1.5)),
                row=1, col=1
            )
        if show_bb:
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['BB_up'], mode='lines', name='BB Upper', line=dict(color='rgba(255,255,255,0.2)', width=1)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['BB_down'], mode='lines', name='BB Lower', line=dict(color='rgba(255,255,255,0.2)', width=1), fill='tonexty', fillcolor='rgba(255,255,255,0.02)'),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df_ind.index, y=df_ind['BB_mid'], mode='lines', name='BB Mid', line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dot')),
                row=1, col=1
            )

        # Volume Chart
        volume_colors = [
            '#10b981' if df_ind['Close'].iloc[i] >= df_ind['Open'].iloc[i] else '#ef4444' 
            for i in range(len(df_ind))
        ]
        fig.add_trace(
            go.Bar(
                x=df_ind.index,
                y=df_ind['Volume'],
                name='Volume',
                marker_color=volume_colors,
                opacity=0.7,
                hovertemplate='Volume: %{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # Update styling of the chart
        fig.update_layout(
            paper_bgcolor='#161c2d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
            xaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.05)', 
                rangeslider=dict(visible=False),
                linecolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.05)', 
                title='Price',
                side='left',
                linecolor='rgba(255,255,255,0.1)',
                tickformat=',.2f'
            ),
            yaxis2=dict(
                gridcolor='rgba(255, 255, 255, 0.02)', 
                title='Volume',
                side='right',
                linecolor='rgba(255,255,255,0.1)'
            ),
            margin=dict(l=40, r=40, t=10, b=40),
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                bgcolor='rgba(0,0,0,0)'
            ),
            height=550
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Extra details cards
        if info:
            st.markdown("#### Company Details / Fundamental Stats")
            c1, c2 = st.columns(2)
            
            with c1:
                details_html = f"""
                <div class="dashboard-card" style="height: 100%;">
                    <h5 style="margin-top:0;">Profile</h5>
                    <p style="font-size:14px; line-height:1.5; color:#9ca3af;">{info.get('longBusinessSummary', 'No summary available.')[:380]}...</p>
                    <table style="width:100%; font-size:14px; margin-top:10px;">
                        <tr><td style="color:#6b7280; padding:6px 0;">Sector</td><td style="text-align:right; font-weight:600;">{info.get('sector', 'N/A')}</td></tr>
                        <tr><td style="color:#6b7280; padding:6px 0;">Industry</td><td style="text-align:right; font-weight:600;">{info.get('industry', 'N/A')}</td></tr>
                        <tr><td style="color:#6b7280; padding:6px 0;">Country</td><td style="text-align:right; font-weight:600;">{info.get('country', 'N/A')}</td></tr>
                    </table>
                </div>
                """
                st.markdown(details_html, unsafe_allow_html=True)
                
            with c2:
                yield_val = info.get("dividendYield")
                yield_str = f"{yield_val*100:.2f}%" if yield_val else "N/A"
                beta_val = info.get("beta")
                beta_str = f"{beta_val:.2f}" if beta_val else "N/A"
                eps_val = info.get("trailingEps")
                eps_str = f"{eps_val:.2f}" if eps_val else "N/A"
                recommendation = info.get("recommendationKey", "N/A").upper()
                
                details_html2 = f"""
                <div class="dashboard-card" style="height: 100%;">
                    <h5 style="margin-top:0;">Key Financial Metrics</h5>
                    <table style="width:100%; font-size:14px;">
                        <tr><td style="color:#6b7280; padding:8px 0;">52 Week High</td><td style="text-align:right; font-weight:600; color:#10b981;">${info.get('fiftyTwoWeekHigh', 0):,.2f}</td></tr>
                        <tr><td style="color:#6b7280; padding:8px 0;">52 Week Low</td><td style="text-align:right; font-weight:600; color:#ef4444;">${info.get('fiftyTwoWeekLow', 0):,.2f}</td></tr>
                        <tr><td style="color:#6b7280; padding:8px 0;">Trailing EPS</td><td style="text-align:right; font-weight:600;">{eps_str}</td></tr>
                        <tr><td style="color:#6b7280; padding:8px 0;">Dividend Yield</td><td style="text-align:right; font-weight:600;">{yield_str}</td></tr>
                        <tr><td style="color:#6b7280; padding:8px 0;">Beta (Volatility)</td><td style="text-align:right; font-weight:600;">{beta_str}</td></tr>
                        <tr><td style="color:#6b7280; padding:8px 0;">Analyst Consensus</td><td style="text-align:right; font-weight:700; color:#0ea5e9;">{recommendation}</td></tr>
                    </table>
                </div>
                """
                st.markdown(details_html2, unsafe_allow_html=True)
