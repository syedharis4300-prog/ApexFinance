import streamlit as st
import pandas as pd
import json
import os
import yfinance as yf
import plotly.graph_objects as go
from styles import render_metric_card

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_portfolio(portfolio):
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(portfolio, f, indent=4)
    except Exception as e:
        st.error(f"Error saving portfolio: {str(e)}")

# Fetch multiple tickers' current prices in a batch (cached for speed)
@st.cache_data(ttl=120)
def fetch_live_prices(symbols):
    prices = {}
    if not symbols:
        return prices
    try:
        # Fetching data in a single download call
        data = yf.download(list(symbols), period="1d", group_by="ticker", progress=False)
        for sym in symbols:
            try:
                # If yf.download returns a multi-index dataframe
                if len(symbols) > 1:
                    ticker_data = data[sym]
                else:
                    ticker_data = data
                
                if not ticker_data.empty:
                    # Get the last non-null close price
                    close_prices = ticker_data['Close'].dropna()
                    if not close_prices.empty:
                        prices[sym] = float(close_prices.iloc[-1])
                    else:
                        prices[sym] = None
                else:
                    prices[sym] = None
            except Exception:
                # Fallback to single lookup if batch fetch fails for this ticker
                try:
                    t = yf.Ticker(sym)
                    history = t.history(period="1d")
                    if not history.empty:
                        prices[sym] = float(history['Close'].iloc[-1])
                    else:
                        prices[sym] = None
                except Exception:
                    prices[sym] = None
    except Exception:
        # Fallback to individual tickers
        for sym in symbols:
            try:
                t = yf.Ticker(sym)
                history = t.history(period="1d")
                if not history.empty:
                    prices[sym] = float(history['Close'].iloc[-1])
                else:
                    prices[sym] = None
            except Exception:
                prices[sym] = None
    return prices

def render_portfolio_tab():
    st.markdown("## 💼 Personal Investment Portfolio")
    st.markdown("Track your stocks, cryptos, and ETFs. Your data is stored locally in `portfolio.json`.")
    
    # Load holdings
    portfolio = load_portfolio()
    
    # Form to add asset
    with st.expander("➕ Add New Transaction", expanded=len(portfolio) == 0):
        with st.form("add_asset_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                sym_input = st.text_input("Ticker Symbol", placeholder="AAPL").upper().strip()
            with c2:
                qty_input = st.number_input("Quantity", min_value=0.0, step=0.1, value=0.0)
            with c3:
                price_input = st.number_input("Purchase Price ($)", min_value=0.0, step=0.01, value=0.0)
            with c4:
                date_input = st.date_input("Purchase Date")
                
            submitted = st.form_submit_button("Add to Portfolio")
            
            if submitted:
                if not sym_input:
                    st.error("Please enter a valid ticker symbol.")
                elif qty_input <= 0:
                    st.error("Quantity must be greater than zero.")
                elif price_input <= 0:
                    st.error("Purchase price must be greater than zero.")
                else:
                    # Validate ticker exists using yfinance
                    with st.spinner(f"Verifying ticker '{sym_input}'..."):
                        try:
                            ticker = yf.Ticker(sym_input)
                            hist = ticker.history(period="1d")
                            if hist.empty:
                                st.error(f"Ticker '{sym_input}' could not be verified. Double check the symbol.")
                            else:
                                # Save transaction
                                new_txn = {
                                    "symbol": sym_input,
                                    "qty": qty_input,
                                    "buy_price": price_input,
                                    "date": str(date_input)
                                }
                                portfolio.append(new_txn)
                                save_portfolio(portfolio)
                                st.success(f"Added {qty_input} shares of {sym_input} successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error validating ticker: {str(e)}")

    if not portfolio:
        st.info("Your portfolio is currently empty. Add transactions above to start tracking performance.")
        return
        
    # Process portfolio data
    symbols = list(set([item['symbol'] for item in portfolio]))
    
    with st.spinner("Fetching current market prices..."):
        current_prices = fetch_live_prices(symbols)
        
    # Construct dataframe of current holdings
    processed_items = []
    
    for i, item in enumerate(portfolio):
        sym = item['symbol']
        qty = item['qty']
        buy_p = item['buy_price']
        curr_p = current_prices.get(sym)
        
        # Fallback if current price isn't found
        if curr_p is None:
            curr_p = buy_p
            
        cost_basis = qty * buy_p
        market_value = qty * curr_p
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        processed_items.append({
            "idx": i,
            "Symbol": sym,
            "Purchase Date": item['date'],
            "Qty": qty,
            "Avg Buy Price": f"${buy_p:,.2f}",
            "Current Price": f"${curr_p:,.2f}",
            "Cost Basis": cost_basis,
            "Market Value": market_value,
            "Gain/Loss ($)": gain_loss,
            "Gain/Loss (%)": gain_loss_pct,
            "raw_gain_loss": gain_loss,
            "raw_gain_loss_pct": gain_loss_pct
        })
        
    df_portfolio = pd.DataFrame(processed_items)
    
    # Portfolio Totals
    total_cost = df_portfolio["Cost Basis"].sum()
    total_value = df_portfolio["Market Value"].sum()
    total_gl = total_value - total_cost
    total_gl_pct = (total_gl / total_cost) * 100 if total_cost > 0 else 0
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        render_metric_card(
            "Portfolio Value",
            f"${total_value:,.2f}",
            f"Cost Basis: ${total_cost:,.2f}",
            change_direction="neutral"
        )
        
    with p2:
        gl_direction = "up" if total_gl >= 0 else "down"
        gl_sign = "+" if total_gl >= 0 else ""
        render_metric_card(
            "Total Gain / Loss",
            f"{gl_sign}${total_gl:,.2f}",
            f"{total_gl_pct:+.2f}% overall return",
            change_direction=gl_direction
        )
        
    with p3:
        # Group by asset for allocation
        df_grouped = df_portfolio.groupby("Symbol").agg({
            "Cost Basis": "sum",
            "Market Value": "sum",
            "Gain/Loss ($)": "sum"
        }).reset_index()
        
        best_asset = "None"
        best_return = -999999
        
        for idx, row in df_grouped.iterrows():
            asset_ret = (row["Gain/Loss ($)"] / row["Cost Basis"]) * 100 if row["Cost Basis"] > 0 else 0
            if asset_ret > best_return:
                best_return = asset_ret
                best_asset = row["Symbol"]
                
        best_return_str = f"{best_return:+.2f}%" if best_asset != "None" else "N/A"
        render_metric_card(
            "Top Performer",
            best_asset,
            f"ROI: {best_return_str}",
            change_direction="up" if best_return >= 0 else "down"
        )

    # Charts and Holdings Lists
    col_chart, col_allocation = st.columns([2, 1])
    
    with col_chart:
        st.markdown("#### Performance Breakdown by Asset")
        
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Bar(
            x=df_grouped["Symbol"],
            y=df_grouped["Gain/Loss ($)"],
            marker_color=[
                '#10b981' if gl >= 0 else '#ef4444' 
                for gl in df_grouped["Gain/Loss ($)"]
            ],
            hovertemplate='%{x}: %{y:+$val,.2f}<extra></extra>'
        ))
        
        fig_perf.update_layout(
            paper_bgcolor='#161c2d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)', linecolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)', linecolor='rgba(255,255,255,0.1)', tickformat='$,.2f'),
            margin=dict(l=40, r=40, t=10, b=40),
            height=300
        )
        st.plotly_chart(fig_perf, use_container_width=True)
        
    with col_allocation:
        st.markdown("#### Asset Allocation")
        fig_alloc = go.Figure(data=[go.Pie(
            labels=df_grouped["Symbol"],
            values=df_grouped["Market Value"],
            hole=.4,
            hoverinfo="label+percent+value",
            textinfo="label",
            marker=dict(colors=['#0ea5e9', '#a855f7', '#6366f1', '#10b981', '#f59e0b', '#ec4899'])
        )])
        fig_alloc.update_layout(
            paper_bgcolor='#161c2d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    # Detailed holdings list
    st.markdown("#### Holdings Details")
    
    # Render table nicely
    display_cols = ["Symbol", "Purchase Date", "Qty", "Avg Buy Price", "Current Price", "Cost Basis", "Market Value", "Gain/Loss ($)", "Gain/Loss (%)"]
    df_display = df_portfolio[display_cols].copy()
    
    # Format currency columns for representation
    df_display["Cost Basis"] = df_display["Cost Basis"].map(lambda x: f"${x:,.2f}")
    df_display["Market Value"] = df_display["Market Value"].map(lambda x: f"${x:,.2f}")
    
    # Custom colored styling for profit/loss in columns using pandas styler or display
    def style_gain_loss(val):
        color = '#10b981' if val >= 0 else '#ef4444'
        sign = '+' if val >= 0 else ''
        return f'<span style="color: {color}; font-weight:600;">{sign}{val:,.2f}</span>'
        
    def style_pct(val):
        color = '#10b981' if val >= 0 else '#ef4444'
        sign = '+' if val >= 0 else ''
        return f'<span style="color: {color}; font-weight:600;">{sign}{val:.2f}%</span>'
        
    df_display["Gain/Loss ($)"] = df_portfolio["raw_gain_loss"].apply(style_gain_loss)
    df_display["Gain/Loss (%)"] = df_portfolio["raw_gain_loss_pct"].apply(style_pct)
    
    table_html = df_display.to_html(escape=False, index=False, classes="dataframe")
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Remove transactions section
    st.markdown("#### 🗑️ Manage Transactions")
    del_cols = st.columns([3, 1])
    with del_cols[0]:
        options = [f"#{item['idx']}: {item['Symbol']} - {item['Qty']} shares @ {item['Avg Buy Price']} ({item['Purchase Date']})" for item in processed_items]
        to_delete = st.selectbox("Select holding to remove:", options)
    with del_cols[1]:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Delete Transaction", use_container_width=True):
            idx_to_del = int(to_delete.split(":")[0].replace("#", ""))
            portfolio.pop(idx_to_del)
            save_portfolio(portfolio)
            st.success("Transaction removed!")
            st.rerun()
