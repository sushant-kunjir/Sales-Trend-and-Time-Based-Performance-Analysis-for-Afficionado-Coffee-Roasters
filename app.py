import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Afficionado Coffee Roasters Dashboard",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("☕ Afficionado Coffee Roasters Analytics Dashboard")

st.markdown("""
This dashboard provides time-based sales analysis for
Afficionado Coffee Roasters.
""")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Afficionado Coffee Roasters.xlsx")

    # Convert datetime
    df['transaction_time'] = pd.to_datetime(
    df['transaction_time'].astype(str),
    format='%H:%M:%S'
)

    # Revenue column
    df['Revenue'] = df['transaction_qty'] * df['unit_price']

    # Hour
    df['Hour'] = df['transaction_time'].dt.hour

    # Day name
    df['Day_Name'] = df['transaction_time'].dt.day_name()

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

# Store filter
store = st.sidebar.multiselect(
    "Select Store Location",
    options=df['store_location'].unique(),
    default=df['store_location'].unique()
)

# Day filter
days = st.sidebar.multiselect(
    "Select Day",
    options=df['Day_Name'].unique(),
    default=df['Day_Name'].unique()
)

# Hour range slider
hour_range = st.sidebar.slider(
    "Select Hour Range",
    0, 23,
    (0, 23)
)

# Revenue vs Quantity Toggle
metric = st.sidebar.radio(
    "Select Metric",
    ["Revenue", "transaction_qty"]
)

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_df = df[
    (df['store_location'].isin(store)) &
    (df['Day_Name'].isin(days)) &
    (df['Hour'] >= hour_range[0]) &
    (df['Hour'] <= hour_range[1])
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Revenue",
    f"${filtered_df['Revenue'].sum():,.2f}"
)

col2.metric(
    "Total Transactions",
    filtered_df['transaction_id'].nunique()
)

col3.metric(
    "Total Quantity Sold",
    int(filtered_df['transaction_qty'].sum())
)

# -----------------------------
# SALES TREND
# -----------------------------
st.subheader("📈 Overall Sales Trend")

hourly_sales = filtered_df.groupby('Hour')[metric].sum().reset_index()

fig1 = px.line(
    hourly_sales,
    x='Hour',
    y=metric,
    markers=True,
    title="Hourly Sales Trend"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# DAY OF WEEK ANALYSIS
# -----------------------------
st.subheader("📅 Day-of-Week Performance")

day_sales = filtered_df.groupby('Day_Name')[metric].sum().reset_index()

days_order = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

day_sales['Day_Name'] = pd.Categorical(
    day_sales['Day_Name'],
    categories=days_order,
    ordered=True
)

day_sales = day_sales.sort_values('Day_Name')

fig2 = px.bar(
    day_sales,
    x='Day_Name',
    y=metric,
    color='Day_Name',
    title="Day-wise Performance"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# HEATMAP
# -----------------------------
st.subheader("🔥 Hourly Demand Heatmap")

heatmap_data = filtered_df.pivot_table(
    values=metric,
    index='Day_Name',
    columns='Hour',
    aggfunc='sum'
)

fig, ax = plt.subplots(figsize=(15,5))

sns.heatmap(
    heatmap_data,
    cmap='YlOrRd',
    annot=True,
    fmt='.0f'
)

st.pyplot(fig)

# -----------------------------
# STORE COMPARISON
# -----------------------------
st.subheader("🏪 Store Location Comparison")

store_sales = filtered_df.groupby('store_location')[metric].sum().reset_index()

fig3 = px.bar(
    store_sales,
    x='store_location',
    y=metric,
    color='store_location',
    title="Store Performance Comparison"
)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TIME BUCKET ANALYSIS
# -----------------------------
st.subheader("⏰ Time Bucket Analysis")

def time_bucket(hour):
    if 6 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 16:
        return 'Afternoon'
    elif 17 <= hour <= 21:
        return 'Evening'
    else:
        return 'Late Hours'

filtered_df['Time_Bucket'] = filtered_df['Hour'].apply(time_bucket)

bucket_sales = filtered_df.groupby('Time_Bucket')[metric].sum().reset_index()

fig4 = px.pie(
    bucket_sales,
    names='Time_Bucket',
    values=metric,
    title="Revenue Distribution by Time Bucket"
)

st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# RAW DATA
# -----------------------------
st.subheader("🗂 View Dataset")

st.dataframe(filtered_df)

# -----------------------------
# DOWNLOAD OPTION
# -----------------------------
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Filtered Data",
    data=csv,
    file_name='filtered_sales_data.csv',
    mime='text/csv'
)
