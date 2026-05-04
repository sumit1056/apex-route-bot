import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os

# Page config
st.set_page_config(page_title="Dreamline Logistics | Executive Dashboard", layout="wide")

# Theme / CSS for Executive Dark Mode
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #D4AF37 !important; /* Gold */
        font-family: 'Inter', sans-serif;
    }
    .stMetric {
        background-color: #1E222D;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #D4AF37;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    .stDataFrame {
        border: 1px solid #333;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Supabase Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dlkgqtuucwflmsakacln.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsa2dxdHV1Y3dmbG1zYWthY2xuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4OTI4NDgsImV4cCI6MjA5MzQ2ODg0OH0.FKSY73XgIL0WoBoBosl8WsH-MvXMi6rvoN340FdJACc") # Dashboard uses anon key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_data():
    res = supabase.table("entries").select("*").order("date", desc=True).order("time", desc=True).execute()
    return pd.DataFrame(res.data)

# Header
st.title("🏆 Dreamline Logistics Executive Dashboard")
st.write("Real-time financial overview and operations tracking.")

# Load Data
df = get_data()

if not df.empty:
    # Ensure numeric columns are properly typed
    for col in ['bank_amount', 'cash_amount', 'credit_amount']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Calculations
    total_income  = df[df['type'] == 'Income']['bank_amount'].sum() + df[df['type'] == 'Income']['cash_amount'].sum()
    total_expense = df[df['type'] == 'Expense']['bank_amount'].sum() + df[df['type'] == 'Expense']['cash_amount'].sum() + df[df['type'] == 'Expense']['credit_amount'].sum()
    net_profit    = total_income - total_expense
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", f"₹{total_income:,.2f}", delta_color="normal")
    with col2:
        st.metric("Total Expenses", f"₹{total_expense:,.2f}", delta_color="inverse")
    with col3:
        profit_color = "normal" if net_profit >= 0 else "inverse"
        st.metric("Net Profit", f"₹{net_profit:,.2f}", delta_color=profit_color)

    st.markdown("---")

    # Filters
    st.sidebar.header("Filter Data")
    type_filter = st.sidebar.multiselect("Entry Type", options=df['type'].unique(), default=df['type'].unique())
    cat_filter  = st.sidebar.multiselect("Category", options=df['category'].unique(), default=df['category'].unique())
    
    filtered_df = df[df['type'].isin(type_filter) & df['category'].isin(cat_filter)]

    # Data Table
    st.subheader("📋 Recent Transactions")
    
    # Display table with styling
    st.dataframe(
        filtered_df[['date', 'time', 'type', 'category', 'payment_method', 'bank_amount', 'cash_amount', 'credit_amount', 'remarks']],
        use_container_width=True,
        hide_index=True
    )
    
    # Summary of Categories
    st.subheader("📊 Category-wise Breakdown")
    cat_summary = filtered_df.groupby('category').agg({
        'bank_amount': 'sum',
        'cash_amount': 'sum',
        'credit_amount': 'sum'
    })
    cat_summary['Total'] = cat_summary.sum(axis=1)
    st.table(cat_summary.sort_values('Total', ascending=False))

else:
    st.warning("No data found in the database. Start adding entries via the Telegram bot!")

if st.button("🔄 Refresh Data"):
    st.rerun()
