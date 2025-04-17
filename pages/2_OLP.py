import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.vault import load_clean_olp_prices
from src.utils.APR import APR_SMA_table
import numpy as np

df = load_clean_olp_prices()

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

df_APR_modelling = APR_SMA_table(
    prices=list(df.sort_values('day', ascending=False)['price']),
    N=30,
    K=15
)

# Apply background color formatting based on value intensity
def color_scale_background(val):
    """
    Takes a scalar and returns a string with css background-color property.
    The color intensity is based on the value's position between global min and max.
    Red for negative, Green for positive values.
    """
    if val is None:
        return ''
    try:
        val_float = float(val)
        if val_float == 0:
            return 'background-color: #FFFFFF'
        
        # Get global min/max for scaling
        all_values = df_APR_modelling.select_dtypes(include=['float64', 'int64']).values.ravel()
        all_values = all_values[~np.isnan(all_values)]  # Remove NaN values
        val_min, val_max = min(all_values), max(all_values)
        
        if val_float > 0:
            # Scale from white to green (positive values)
            intensity = val_float / val_max
            intensity = min(intensity, 1.0)  # Cap at 1
            return f'background-color: rgba(0, 255, 0, {intensity * 0.5})'
        else:
            # Scale from white to red (negative values)
            intensity = val_float / val_min
            intensity = min(intensity, 1.0)  # Cap at 1
            return f'background-color: rgba(255, 0, 0, {abs(intensity) * 0.5})'
    except (ValueError, TypeError):
        return ''

# Apply the styling to the dataframe
styled_df = df_APR_modelling.style.applymap(color_scale_background)

# Variables Description
st.write('n: how many days back are used to extrapolate APR')
st.write('- APR = ln(price[today] / price[n days ago]) * 365 / n')
st.write('- if n is 30, it uses the price today and 30 days ago')


st.write('k: how many APR data points are used of the Simple Moving Average')
st.write('- the bigger k, produces a smoother APR change')
st.write('- APR increases and decreases more slowly')

# Display the styled dataframe
st.write(styled_df)