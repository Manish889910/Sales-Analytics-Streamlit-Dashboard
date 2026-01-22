import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Retail Sales Analytics Dashboard", page_icon="📊", layout="wide")
st.title("📊 Retail Sales Analytics Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# ---------------- INTRO ----------------
st.info("""
This dashboard is a reusable Business Intelligence tool built using the Superstore dataset.
It supports structurally similar retail datasets after automatic validation and cleaning.
""")

# ---------------- DATASET REQUIREMENTS ----------------
with st.expander("📌 Dataset Requirements"):
    st.markdown("""
**Required Columns:**
- Order Date  
- Region  
- State  
- City  
- Category  
- Sub-Category  
- Sales  
- Profit  
- Quantity  
- Segment  
""")

# ---------------- FILE UPLOAD ----------------
fl = st.file_uploader("📂 Upload your retail sales dataset", type=['csv', 'xlsx', 'xls'])

if fl is not None:
    if fl.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(fl)
    else:
        df = pd.read_csv(fl, encoding='ISO-8859-1')
else:
    df = pd.read_csv("Sample_Superstore.csv", encoding='ISO-8859-1')

# ---------------- COLUMN CLEANING ----------------
df.columns = df.columns.str.replace('ï»¿', '', regex=False)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(".", "_").str.replace("-", "_")

# ---------------- SMART COLUMN MAPPING ----------------
column_mapping = {
    "order_date": "Order Date",
    "orderdate": "Order Date",
    "order_date_": "Order Date",
    "order_date__": "Order Date",
    "orderdate_": "Order Date",

    "category": "Category",
    "product_category": "Category",

    "sub_category": "Sub-Category",
    "subcategory": "Sub-Category",
    "sub_category_name": "Sub-Category",
    "sub_category_": "Sub-Category",
    "sub_category__": "Sub-Category",

    "sales": "Sales",
    "profit": "Profit",
    "quantity": "Quantity",

    "region": "Region",
    "market": "Region",

    "state": "State",
    "province": "State",

    "city": "City",

    "segment": "Segment",
    "customer_segment": "Segment"
}

df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

# ---------------- REMOVE DUPLICATE COLUMNS ----------------
df = df.loc[:, ~df.columns.duplicated()]

# ---------------- DATA VALIDATION ----------------
required_columns = [
    "Order Date", "Region", "State", "City",
    "Category", "Sub-Category", "Sales",
    "Profit", "Quantity", "Segment"
]

missing_cols = [col for col in required_columns if col not in df.columns]

if missing_cols:
    st.error(
        f"❌ Uploaded file is not compatible.\n\n"
        f"Missing required columns: {missing_cols}\n\n"
        "Please upload a retail dataset similar to Superstore.\n"
        "You may use Global Superstore or Sample Superstore datasets."
    )
    st.stop()

# ---------------- DATA CLEANING ----------------
df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
df = df.dropna(subset=["Order Date"])

# ---------------- DATE FILTER ----------------
col1, col2 = st.columns(2)
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]

# ---------------- SIDEBAR FILTERS (FIXED) ----------------
st.sidebar.header("🔎 Filter Your Data")

region_list = df["Region"].dropna().unique().tolist()
region = st.sidebar.multiselect("Region", region_list, default=region_list)

state_list = df[df["Region"].isin(region)]["State"].dropna().unique().tolist()
state = st.sidebar.multiselect("State", state_list, default=state_list)

city_list = df[df["State"].isin(state)]["City"].dropna().unique().tolist()
city = st.sidebar.multiselect("City", city_list, default=city_list)

filtered_df = df.copy()
if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

if filtered_df.empty:
    st.warning("⚠ No data available for selected filters.")
    st.stop()

# ---------------- CATEGORY SALES ----------------
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Category-wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text_auto='.2s')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region-wise Sales")
    fig = px.pie(filtered_df, names="Region", values="Sales", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TIME SERIES ----------------
filtered_df["Month_Year"] = filtered_df["Order Date"].dt.to_period("M").astype(str)
ts = filtered_df.groupby("Month_Year")["Sales"].sum().reset_index()

st.subheader("Time Series Analysis")
fig2 = px.line(ts, x="Month_Year", y="Sales")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- TREEMAP ----------------
st.subheader("Hierarchical Sales View")
fig3 = px.treemap(filtered_df, path=['Region', 'Category', 'Sub-Category'], values='Sales')
st.plotly_chart(fig3, use_container_width=True)

# ---------------- PIE CHARTS ----------------
c1, c2 = st.columns(2)
with c1:
    st.subheader("Segment-wise Sales")
    fig = px.pie(filtered_df, names="Segment", values="Sales", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Category-wise Sales Share")
    fig = px.pie(filtered_df, names="Category", values="Sales", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- SCATTER ----------------
st.subheader("Sales vs Profit Relationship")
fig4 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
st.plotly_chart(fig4, use_container_width=True)

# ---------------- DATA PREVIEW ----------------
with st.expander("🔍 Preview Filtered Data"):
    st.dataframe(filtered_df.head(100))

# ---------------- DOWNLOAD ----------------
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("⬇ Download Filtered Dataset", csv, "Filtered_Sales_Data.csv", "text/csv")
