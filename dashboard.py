import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dreamline Logistics | Executive Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0A0C10;
        color: #E0E0E0;
    }

    /* Glassmorphism Card Style */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
    }

    /* Titles */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F1218;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0C10;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True)

# Supabase Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dlkgqtuucwflmsakacln.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsa2dxdHV1Y3dmbG1zYWthY2xuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4OTI4NDgsImV4cCI6MjA5MzQ2ODg0OH0.FKSY73XgIL0WoBoBosl8WsH-MvXMi6rvoN340FdJACc")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=60)
def get_data():
    try:
        res = supabase.table("entries").select("*").order("date", desc=True).order("time", desc=True).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            for col in ['bank_amount', 'cash_amount', 'credit_amount']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            df['total_amount'] = df['bank_amount'] + df['cash_amount'] + df['credit_amount']
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 24px;'>DREAMLINE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>LOGISTICS TRACKER</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🛠️ Control Panel")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.subheader("🔍 Filters")
    
    df_raw = get_data()
    
    if not df_raw.empty:
        types = st.multiselect("Entry Types", options=df_raw['type'].unique(), default=df_raw['type'].unique())
        categories = st.multiselect("Categories", options=df_raw['category'].unique(), default=df_raw['category'].unique())
        
        # Date range
        min_date = df_raw['date'].min().date()
        max_date = df_raw['date'].max().date()
        date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        # Apply filters
        df = df_raw[
            (df_raw['type'].isin(types)) & 
            (df_raw['category'].isin(categories))
        ]
        if len(date_range) == 2:
            df = df[(df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]
    else:
        df = df_raw

# --- MAIN CONTENT ---
st.markdown("<h1 style='margin-bottom: 0;'>📈 Executive Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888; font-size: 18px;'>Financial Performance Overview</p>", unsafe_allow_html=True)

if not df.empty:
    # --- KPI CALCULATIONS ---
    total_income = df[df['type'] == 'Income']['total_amount'].sum()
    total_expense = df[df['type'] == 'Expense']['total_amount'].sum()
    net_profit = total_income - total_expense
    margin = (net_profit / total_income * 100) if total_income > 0 else 0
    
    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #888; margin:0;'>Total Revenue</p>
                <h2 style='margin:0;'>₹{total_income:,.0f}</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #888; margin:0;'>Total Expenses</p>
                <h2 style='margin:0; color: #FF4B4B !important;'>₹{total_expense:,.0f}</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
        p_color = "#D4AF37" if net_profit >= 0 else "#FF4B4B"
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #888; margin:0;'>Net Profit</p>
                <h2 style='margin:0; color: {p_color} !important;'>₹{net_profit:,.0f}</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi4:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #888; margin:0;'>Profit Margin</p>
                <h2 style='margin:0;'>{margin:.1f}%</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS SECTION ---
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.subheader("📅 Financial Trends")
        # Group by date and type
        daily_trend = df.groupby(['date', 'type'])['total_amount'].sum().reset_index()
        fig_trend = px.line(
            daily_trend, 
            x='date', 
            y='total_amount', 
            color='type',
            color_discrete_map={'Income': '#D4AF37', 'Expense': '#FF4B4B'},
            template='plotly_dark',
            line_shape='spline'
        )
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with chart_col2:
        st.subheader("🏷️ Category Mix")
        cat_data = df[df['type'] == 'Expense'].groupby('category')['total_amount'].sum().reset_index()
        if not cat_data.empty:
            fig_pie = px.pie(
                cat_data, 
                values='total_amount', 
                names='category',
                hole=0.6,
                color_discrete_sequence=px.colors.sequential.YlOrBr_r,
                template='plotly_dark'
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data for pie chart.")

    # --- RECENT TRANSACTIONS ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Detailed Records")
    
    # Styled Table
    def color_type(val):
        color = '#D4AF37' if val == 'Income' else '#FF4B4B'
        return f'color: {color}; font-weight: bold;'

    display_df = df[['date', 'time', 'type', 'category', 'payment_method', 'total_amount', 'remarks']]
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "total_amount": st.column_config.NumberColumn("Amount", format="₹%d"),
            "type": st.column_config.TextColumn("Type"),
            "category": st.column_config.TextColumn("Category"),
            "payment_method": st.column_config.TextColumn("Method"),
        }
    )

else:
    st.info("👋 No data matching your filters. Try adjusting the date range or adding entries via Telegram!")
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h3 style='color: #555 !important;'>Start by sending /start to your Telegram Bot</h3>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #444;'>© 2026 Dreamline Logistics | Powered by Supabase & Streamlit</p>", unsafe_allow_html=True)
