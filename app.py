import streamlit as st
import pandas as pd
import plotly.express as px
# import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Superstore Sales Dashboard")

st.markdown('<style>div.block-container{padding-top:2rem;}</styl>', unsafe_allow_html=True)
st.info("""
The analysis in the accompanying report is based on the Sample Superstore dataset.
This dashboard is designed as a reusable decision-support tool and allows users
to upload structurally similar sales datasets after validation and basic cleaning.
""")

#how user can upload their own data
fl = st.file_uploader(" :file_folder: Upload a file", type=['csv','xlsx','xls','txt'])
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = 'ISO-8859-1')
else:
    # os.chdir("C:/Users/hp/Documents")
    df = pd.read_csv("Sample_Superstore.csv", encoding = 'ISO-8859-1')


# now creating 2 columns from user can select data 
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#getting the min and max date
startDate = pd.to_datetime(df["Order Date"].min())
endDate = pd.to_datetime(df["Order Date"].max())

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

#filtering data based on date selection
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]

# now create side filter so user can filter data based on their need
st.sidebar.header("Choose your filter:")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
#if not selected then all region will be selected
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)] # this will filter data based on region selection

#now same for state
state = st.sidebar.multiselect("Pick your State", df2["State"].unique()) #this mans user can select multiple states
if not state:
    df3 = df2.copy()    
else:
    df3 = df2[df2["State"].isin(state)] # this will filter data based on state selection

#create same for city
city = st.sidebar.multiselect("Pick your City", df3["City"].unique()) #this mans user can select multiple cities
if not city:
    df4 = df3.copy()    
else:
    df4 = df3[df3["City"].isin(city)] # this will filter data based on city selection

# Filter the data based on user selections
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not state:
    filtered_df = df[df["City"].isin(city)]
elif state and city : 
    filtered_df = df3[df3["State"].isin(state)& df3["City"].isin(city)]
elif region and city:
    filtered_df = df2[df2["Region"].isin(region)& df2["City"].isin(city)]
elif region and state:
    filtered_df = df2[df2["Region"].isin(region)& df2["State"].isin(state)] 
elif city:
    filtered_df = df[df["City"].isin(city)]
else:
    filtered_df  = df3[df['Region'].isin(region)& df3['State'].isin(state)& df3['City'].isin(city)]


category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum() # this will group data based on category and sum of sales

with col1:
    st.subheader("Category-wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],template = "seaborn")  
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region-wise Sales")
    fig = px.pie(filtered_df, names="Region", values="Sales", hole = 0.5)
    fig.update_traces(text = filtered_df['Region'], textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download data as CSV", data=csv, file_name='Category_ViewData.csv', mime='text/csv',
                           help="Click to download data!")
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = ["Region"], as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download data as CSV", data=csv, file_name='Region.csv', mime='text/csv',
                           help="Click to download data!")
        
# time series analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df ["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales",labels={"Sales": "Amount"},height=500,width=1000,template="gridon")
st.plotly_chart(fig2, use_container_width=True)

#download option for time series data
with st.expander("Time_Series_ViewData"):
    st.write(linechart.style.background_gradient(cmap="Greens"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download data as CSV", data=csv, file_name='Time_Series_ViewData.csv', mime='text/csv',
                       help="Click to download data!")
    
#create treemap  based on region , category , sub-category
st.subheader("Hierarchical view of sales using Treemap")
fig3 = px.treemap(filtered_df, path= ['Region', 'Category', 'Sub-Category'], values='Sales',
                  color='Sub-Category', hover_data=['Sales'],
                  )
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment-wise Sales")
    fig = px.pie(filtered_df, names="Segment", values="Sales", hole = 0.5,template = "plotly_dark")
    fig.update_traces(text = filtered_df['Segment'], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category-wise Ship Mode Sales")
    fig = px.pie(filtered_df, names="Category", values="Sales", hole = 0.5,template = "ggplot2")
    fig.update_traces(text = filtered_df['Category'], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)


import plotly.figure_factory as ff
st.subheader(":point_right: Month wise sub-category sales Summary")
with st.expander("Summary_table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-category Table")
    filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(filtered_df, values='Sales', index=['Sub-Category'], columns=['Month'])
    st.write(sub_category_Year.style.background_gradient(cmap="Purples"))


#create Scatterplot
data1 = px.scatter(
    filtered_df,
    x="Sales",
    y="Profit",
    size="Quantity"
)

data1.update_layout(
    title={
        "text": "Relationship between Sales and Profits using Scatter plot",
        "font": {"size": 20}
    },
    xaxis={
        "title": {"text": "Sales", "font": {"size": 15}}
    },
    yaxis={
        "title": {"text": "Profit", "font": {"size": 15}}
    }
)

st.plotly_chart(data1, use_container_width=True)


with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="pink"))

# how to download whole data set
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(label="Download Complete data as CSV", data=csv, file_name='Complete_Superstore_data.csv', mime='text/csv')
