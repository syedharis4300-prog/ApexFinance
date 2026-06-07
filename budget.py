import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from styles import render_metric_card

def calculate_savings_growth(initial, monthly, rate_annual, years):
    months = years * 12
    monthly_rate = (1 + rate_annual / 100) ** (1 / 12) - 1
    
    balances = []
    contributions = []
    dates = []
    
    curr_balance = initial
    curr_contribution = initial
    
    # Starting point (Month 0)
    balances.append(curr_balance)
    contributions.append(curr_contribution)
    dates.append(0)
    
    for month in range(1, months + 1):
        curr_balance = curr_balance * (1 + monthly_rate) + monthly
        curr_contribution += monthly
        
        balances.append(curr_balance)
        contributions.append(curr_contribution)
        dates.append(month / 12.0)
        
    return pd.DataFrame({
        "Years": dates,
        "Total Value": balances,
        "Total Contributions": contributions,
        "Interest Earned": np.array(balances) - np.array(contributions)
    })

def render_budget_tab():
    st.markdown("## 📊 Personal Budget & Financial Planner")
    st.markdown("Structure your monthly cashflow and project your long-term wealth growth.")
    
    tab1, tab2 = st.tabs(["Monthly Cashflow Planner", "Savings & Growth Simulator"])
    
    with tab1:
        st.markdown("### 💵 Income vs Expenses Planner")
        st.markdown("Evaluate your monthly cashflow, savings rate, and category breakdowns.")
        
        # Inputs setup
        col_inc, col_exp = st.columns(2)
        
        with col_inc:
            st.markdown("##### Monthly Income Sources")
            salary = st.number_input("Primary Salary / Wages ($)", min_value=0.0, step=100.0, value=5000.0)
            freelance = st.number_input("Side Hustles / Freelance ($)", min_value=0.0, step=50.0, value=800.0)
            invest_inc = st.number_input("Dividends & Interest ($)", min_value=0.0, step=10.0, value=200.0)
            other_inc = st.number_input("Other Income ($)", min_value=0.0, step=10.0, value=0.0)
            
            total_income = salary + freelance + invest_inc + other_inc
            
        with col_exp:
            st.markdown("##### Monthly Expenses")
            rent_mortgage = st.number_input("Housing (Rent / Mortgage) ($)", min_value=0.0, step=100.0, value=1500.0)
            groceries = st.number_input("Food & Groceries ($)", min_value=0.0, step=50.0, value=600.0)
            utilities = st.number_input("Utilities & Bills ($)", min_value=0.0, step=20.0, value=300.0)
            transport = st.number_input("Transportation ($)", min_value=0.0, step=20.0, value=250.0)
            entertainment = st.number_input("Entertainment & Dining ($)", min_value=0.0, step=20.0, value=400.0)
            shopping = st.number_input("Shopping & Apparel ($)", min_value=0.0, step=20.0, value=250.0)
            insurance_med = st.number_input("Insurance & Medical ($)", min_value=0.0, step=50.0, value=300.0)
            other_exp = st.number_input("Miscellaneous ($)", min_value=0.0, step=10.0, value=150.0)
            
            total_expenses = rent_mortgage + groceries + utilities + transport + entertainment + shopping + insurance_med + other_exp

        # Summary KPIs
        st.markdown("---")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income) * 100 if total_income > 0 else 0
        
        with kpi1:
            render_metric_card("Total Income", f"${total_income:,.2f}", "Monthly cash inflow", "neutral")
        with kpi2:
            render_metric_card("Total Expenses", f"${total_expenses:,.2f}", f"{total_expenses/total_income*100:.1f}% of income spent" if total_income > 0 else "0% spent", "neutral")
        with kpi3:
            render_metric_card(
                "Net Monthly Savings",
                f"${net_savings:,.2f}",
                f"{'+' if net_savings >= 0 else ''}${net_savings:,.2f} net flow",
                change_direction="up" if net_savings >= 0 else "down"
            )
        with kpi4:
            render_metric_card(
                "Savings Rate",
                f"{savings_rate:.1f}%",
                "Target benchmark: > 20%" if savings_rate < 20 else "Excellent savings rate!",
                change_direction="up" if savings_rate >= 20 else ("down" if savings_rate < 0 else "neutral")
            )
            
        # visual breakdown
        col_gauge, col_pie = st.columns([1, 1])
        
        with col_gauge:
            st.markdown("##### Budget Allocation Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = savings_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Savings Rate (%)", 'font': {'size': 16, 'color': '#ffffff'}},
                gauge = {
                    'axis': {'range': [-50, 100], 'tickwidth': 1, 'tickcolor': "#9ca3af"},
                    'bar': {'color': "#0ea5e9"},
                    'bgcolor': "#161c2d",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255,255,255,0.1)",
                    'steps': [
                        {'range': [-50, 0], 'color': '#ef4444'},
                        {'range': [0, 20], 'color': '#f59e0b'},
                        {'range': [20, 100], 'color': '#10b981'}
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='#161c2d',
                font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
                margin=dict(l=30, r=30, t=50, b=30),
                height=280
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_pie:
            st.markdown("##### Expense Category Breakdown")
            
            categories = ["Housing", "Food & Groceries", "Utilities & Bills", "Transportation", "Entertainment", "Shopping", "Insurance & Med", "Misc"]
            values = [rent_mortgage, groceries, utilities, transport, entertainment, shopping, insurance_med, other_exp]
            
            # Filter zero entries
            cat_filtered = [c for c, v in zip(categories, values) if v > 0]
            val_filtered = [v for v in values if v > 0]
            
            if val_filtered:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=cat_filtered,
                    values=val_filtered,
                    hole=.4,
                    hoverinfo="label+percent+value",
                    textinfo="label",
                    marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'])
                )])
                fig_pie.update_layout(
                    paper_bgcolor='#161c2d',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False,
                    height=280
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expenses entered yet.")

    with tab2:
        st.markdown("### 🔮 Wealth Growth Simulator")
        st.markdown("Project the future value of your investments over time using compound interest.")
        
        c_sim1, c_sim2 = st.columns([1, 2])
        
        with c_sim1:
            st.markdown("##### Investment Inputs")
            init_principal = st.slider("Initial Investment ($)", min_value=0, max_value=500000, step=1000, value=10000)
            monthly_contrib = st.slider("Monthly Contribution ($)", min_value=0, max_value=20000, step=50, value=500)
            annual_return = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=25.0, step=0.5, value=8.0)
            sim_years = st.slider("Time Horizon (Years)", min_value=1, max_value=40, step=1, value=15)
            
        with c_sim2:
            df_growth = calculate_savings_growth(init_principal, monthly_contrib, annual_return, sim_years)
            
            final_val = df_growth["Total Value"].iloc[-1]
            final_contrib = df_growth["Total Contributions"].iloc[-1]
            final_interest = df_growth["Interest Earned"].iloc[-1]
            
            st.markdown("##### Simulation Summary")
            cs1, cs2, cs3 = st.columns(3)
            with cs1:
                render_metric_card("Projected Portfolio Value", f"${final_val:,.2f}", "Total at end of term", "neutral")
            with cs2:
                render_metric_card("Total Contributions", f"${final_contrib:,.2f}", "Total amount deposited", "neutral")
            with cs3:
                render_metric_card("Compound Growth Earned", f"${final_interest:,.2f}", f"{final_interest/final_contrib*100:.1f}% increase on deposits" if final_contrib > 0 else "0% increase", "up")
                
            # Line chart
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(
                x=df_growth["Years"],
                y=df_growth["Total Value"],
                mode='lines',
                name='Total Portfolio Value',
                line=dict(color='#10b981', width=3),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.05)',
                hovertemplate='Year %{x:.1f}: %{y:$,.2f}<extra></extra>'
            ))
            
            fig_sim.add_trace(go.Scatter(
                x=df_growth["Years"],
                y=df_growth["Total Contributions"],
                mode='lines',
                name='Total Contributions',
                line=dict(color='#6366f1', width=2, dash='dash'),
                hovertemplate='Year %{x:.1f} Deposits: %{y:$,.2f}<extra></extra>'
            ))
            
            fig_sim.update_layout(
                paper_bgcolor='#161c2d',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3af', family='Plus Jakarta Sans'),
                xaxis=dict(
                    title="Years elapsed",
                    gridcolor='rgba(255, 255, 255, 0.05)', 
                    linecolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title="Balance ($)",
                    gridcolor='rgba(255, 255, 255, 0.05)', 
                    linecolor='rgba(255,255,255,0.1)',
                    tickformat='$,.0f'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(l=40, r=40, t=10, b=40),
                hovermode='x unified',
                height=300
            )
            st.plotly_chart(fig_sim, use_container_width=True)
