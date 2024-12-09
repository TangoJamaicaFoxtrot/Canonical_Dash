import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page title
st.title("Canonical Sales Dashboard FY2025")

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv("canonical_sales_data_final_corrected.csv")
    return data

data = load_data()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    with st.expander("Time Period"):
        # Date Range Selector
        sales_quarters = data['Sales_Quarter'].unique()
        selected_quarters = st.multiselect("Select Quarter(s):", options=sales_quarters, default=sales_quarters)

    with st.expander("Region"):
        # Region Selector
        regions = data['Region'].unique()
        selected_regions = st.multiselect("Select Region(s):", options=regions, default=regions)

# Apply filters
data_filtered = data[
    (data['Sales_Quarter'].isin(selected_quarters)) &
    (data['Region'].isin(selected_regions)) 
]

# Sticky Filters
with st.expander("### Filtered Data"):
    st.dataframe(data_filtered)

# Display Key Metrics
with st.expander("Key Metrics"):
    # Calculate metrics
    total_pipeline_value = data_filtered[~data_filtered['Deal_Stage'].isin(['Closed-Won', 'Closed-Lost'])]['Deal_Value_USD'].sum()
    total_closed_won = data_filtered[data_filtered['Deal_Stage'] == 'Closed-Won']['Deal_Value_USD'].sum()
    total_closed_lost = data_filtered[data_filtered['Deal_Stage'] == 'Closed-Lost']['Deal_Value_USD'].sum()
    closed_won = data_filtered[data_filtered['Deal_Stage'] == 'Closed-Won'].shape[0]
    total_deals = data_filtered.shape[0]
    win_rate = (closed_won / total_deals) * 100 if total_deals > 0 else 0
    avg_time_to_close = data_filtered['Time_to_Close_Days'].mean()
    avg_csat = data_filtered['Customer_Satisfaction_Score'].mean()
    avg_engagement = data_filtered['Engagement_Score'].mean()

    # Display metrics in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Total Value in Pipeline", value=f"${total_pipeline_value:,.2f}")
        st.metric(label="Total Closed Won", value=f"${total_closed_won:,.2f}")
        st.metric(label="Win Rate", value=f"{win_rate:.2f}%")

    with col2:
        st.metric(label="Total Closed Lost", value=f"${total_closed_lost:,.2f}")
        st.metric(label="Average Time to Close (Days)", value=f"{avg_time_to_close:.1f}" if not pd.isna(avg_time_to_close) else "N/A")
        st.metric(label="Average CSAT Score", value=f"{avg_csat:.2f}" if not pd.isna(avg_csat) else "N/A")
        st.metric(label="Average Engagement Score", value=f"{avg_engagement:.2f}" if not pd.isna(avg_engagement) else "N/A")

# Regional Performance
with st.expander("Regional Performance"):
    # Add Deal Stage filter
    deal_stages = data['Deal_Stage'].unique()
    selected_deal_stages = st.multiselect("Select Deal Stage(s):", options=deal_stages, default=deal_stages)

    # Filter data by Deal Stage
    region_filtered_data = data_filtered[data_filtered['Deal_Stage'].isin(selected_deal_stages)]

    # Interactive Bar Chart: Total Revenue by Region and Product Category
    region_category_revenue = region_filtered_data.groupby(['Region', 'Product_Category'])['Deal_Value_USD'].sum().reset_index()
    category_colors = {
        'Ubuntu OS': '#636EFA',
        'Public Cloud': '#EF553B',
        'Private Cloud': '#00CC96',
        'Kubernetes': '#AB63FA',
        'Virtualisation': '#FFA15A',
        'Security and Support': '#19D3F3',
        'AI and Data': '#FF6692',
        'Hardware': '#B6E880',
        'IoT and edge': '#FF97FF',
        'Developer Tools': '#FECB52'
    }
    fig = px.bar(region_category_revenue, 
                 x='Region', 
                 y='Deal_Value_USD', 
                 color='Product_Category', 
                 title="Total Revenue by Region and Product Category",
                 labels={"Deal_Value_USD": "Total Revenue (USD)", "Region": "Region", "Product_Category": "Product Category"},
                 barmode='group',
                 color_discrete_map=category_colors)
    st.plotly_chart(fig)

# Leaderboard: Top Performers
with st.expander("Salesperson Leaderboard"):
    leaderboard = (data_filtered[data_filtered['Deal_Stage'] == 'Closed-Won']
                   .groupby(['Salesperson_ID', 'Region'])
                   .agg(Total_Closed_Won=('Deal_Value_USD', 'sum'),
                        Average_Deal_Value=('Deal_Value_USD', 'mean'))
                   .reset_index()
                   .sort_values(by='Total_Closed_Won', ascending=False)
                   .head(10))
    st.dataframe(leaderboard, use_container_width=True)


# Product Category Insights
with st.expander("Product Category Insights"):
    # Pie Chart: Revenue Distribution by Product Category (Closed-Won only)
    category_revenue_closed_won = data_filtered[data_filtered['Deal_Stage'] == 'Closed-Won']
    category_revenue = category_revenue_closed_won.groupby('Product_Category')['Deal_Value_USD'].sum().reset_index()
    fig_pie = px.pie(category_revenue, 
                     names='Product_Category', 
                     values='Deal_Value_USD', 
                     title="Revenue Distribution by Product Category (Closed-Won Only)",
                     labels={"Deal_Value_USD": "Total Revenue (USD)", "Product_Category": "Product Category"},
                     hole=0.4)
    fig_pie.update_traces(pull=[0.1 if i == category_revenue['Deal_Value_USD'].idxmax() else 0 for i in range(len(category_revenue))])
    st.plotly_chart(fig_pie)

    # Bar Chart: Average Deal Value by Product Category
    category_avg_deal = data_filtered.groupby('Product_Category')['Deal_Value_USD'].mean().reset_index()
    fig_bar = px.bar(category_avg_deal, 
                     x='Product_Category', 
                     y='Deal_Value_USD', 
                     title="Average Deal Value by Product Category",
                     labels={"Deal_Value_USD": "Average Deal Value (USD)", "Product_Category": "Product Category"},
                     color='Product_Category',
                     color_discrete_map=category_colors)
    st.plotly_chart(fig_bar)

# Lead Source Insights
with st.expander("Lead Source Insights"):
    lead_source_data = data_filtered.groupby(['Lead_Source', 'Deal_Stage'])['Deal_Value_USD'].sum().reset_index()
    stage_colors = {
        'Closed-Lost': '#ff5533',
        'Closed-Won': '#86f920',
        'Negotiation': '#ADD8E6',
        'Proposal Sent': '#fff933'
    }
    fig_lead_source = px.bar(lead_source_data, 
                             x='Lead_Source', 
                             y='Deal_Value_USD', 
                             color='Deal_Stage', 
                             title="Pipeline Value by Lead Source and Deal Stage",
                             labels={"Deal_Value_USD": "Pipeline Value (USD)", "Lead_Source": "Lead Source", "Deal_Stage": "Deal Stage"},
                             barmode='stack',
                             color_discrete_map=stage_colors)
    st.plotly_chart(fig_lead_source)
