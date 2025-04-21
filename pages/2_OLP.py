import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.vault import load_clean_olp_prices
from src.utils.APR import APR_p
import numpy as np

df = load_clean_olp_prices()
prices = list(df['price'])

# Calculate price changes
today = pd.Timestamp.today().normalize()  # Normalize to start of day

# Function to calculate price change
def calculate_price_change(df, days):
    if df.empty:
        return None
    
    # Make sure day column is datetime
    df['day'] = pd.to_datetime(df['day'])
    
    # Sort by date
    df = df.sort_values('day')
    
    # Get latest price
    latest_price = df.iloc[-1]['price']
    
    # Get comparison price
    comparison_date = today - timedelta(days=days)
    comparison_df = df[df['day'] <= comparison_date]
    
    if comparison_df.empty:
        return None
    
    comparison_price = comparison_df.iloc[-1]['price']
    
    # Calculate percentage change
    percent_change = ((latest_price - comparison_price) / comparison_price) * 100
    return percent_change

# Calculate price changes
price_change_24h = calculate_price_change(df, 1)
price_change_7d = calculate_price_change(df, 7)
price_change_15d = calculate_price_change(df, 15)

# Display price change cards in a row
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "24h Change", 
        f"{price_change_24h:.2f}%" if price_change_24h is not None else "N/A",
        delta=f"{price_change_24h:.2f}%" if price_change_24h is not None else None
    )

with col2:
    st.metric(
        "7d Change", 
        f"{price_change_7d:.2f}%" if price_change_7d is not None else "N/A",
        delta=f"{price_change_7d:.2f}%" if price_change_7d is not None else None
    )

with col3:
    st.metric(
        "15d Change", 
        f"{price_change_15d:.2f}%" if price_change_15d is not None else "N/A",
        delta=f"{price_change_15d:.2f}%" if price_change_15d is not None else None
    )

# Add date range filter
date_range = st.radio(
    "Select date range:",
    ["Last 7 days", "Last 14 days", "Last 30 days", "All time"],
    horizontal=True
)

# Filter data based on selected date range
today = pd.Timestamp.today().normalize()  # Normalize to start of day
if date_range == "Last 7 days":
    filtered_df = df[df['day'] >= (today - timedelta(days=7))]
elif date_range == "Last 14 days":
    filtered_df = df[df['day'] >= (today - timedelta(days=14))]
elif date_range == "Last 30 days":
    filtered_df = df[df['day'] >= (today - timedelta(days=30))]
else:  # All time
    filtered_df = df

# Ensure we have data to display
if filtered_df.empty:
    st.warning("No data available for the selected date range.")
else:
    # Get global min and max for y-axis
    y_min = df['price'].min()
    y_max = df['price'].max()
    
    # Make sure day column is properly formatted as datetime
    filtered_df['day'] = pd.to_datetime(filtered_df['day'])
    
    # Sort by date to ensure proper line chart display
    filtered_df = filtered_df.sort_values('day')
    
    # Create matplotlib figure and axis
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the data
    ax.plot(filtered_df['day'], filtered_df['price'], marker='o', linestyle='-')
    
    # Set labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('OLP Price Over Time')
    
    # Set y-axis limits based on global min/max
    ax.set_ylim(y_min, y_max)
    
    # Format x-axis dates
    fig.autofmt_xdate()
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Display the plot in Streamlit
    st.pyplot(fig)

# Display price change cards in a row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "24h Change", 
        f"{APR_p(prices, 1):.2f}%" if APR_p(prices, 1) is not None else "N/A",
    )

with col2:
    st.metric(
        "7d Change", 
        f"{APR_p(prices, 7):.2f}%" if APR_p(prices, 7) is not None else "N/A"
    )

with col3:
    st.metric(
        "15d Change", 
        f"{APR_p(prices, 15):.2f}%" if APR_p(prices, 15) is not None else "N/A",
    )

with col4:
    st.metric(
        "30d Change", 
        f"{APR_p(prices, 30):.2f}%" if APR_p(prices, 30) is not None else "N/A",
    )