import streamlit as st
from src.data_processing import load_open_trades, clean_open_trades, get_open_trades_uPnl
from src.viz import plt_bar_oi_isBuy, plt_bar_oiImbalance
import time
import matplotlib.pyplot as plt

def main():
    st.title("Trading Dashboard")
    
    # Add a refresh button and auto-refresh option
    col1, col2 = st.columns([1, 3])
    with col1:
        refresh = st.button("Refresh Data")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    
    # Load data - only force update when refresh button is clicked or auto-refresh is enabled
    df = load_open_trades(updateInterval_min=1, forceUpdate=refresh)
    df = clean_open_trades(df)
    
    # Get latest uPnL data
    df = get_open_trades_uPnl(df)
    
    # Display Total Unrealized PnL metric
    st.metric('Total Unrealized Pnl', f"${int(df['uPnl'].sum()):,}")
    
    # Display PnL by pair chart
    st.subheader("PnL by Pair")
    df_pnl_pair = df.groupby('pair').sum().reset_index()[['pair', 'uPnl']].sort_values('uPnl')
    st.bar_chart(df_pnl_pair, x='pair', y='uPnl')
    
    # Display OI charts - with proper figure handling
    st.subheader("Open Interest by Buy/Sell")
    fig1 = plt_bar_oi_isBuy(df.copy())
    st.pyplot(fig1)
    plt.close(fig1)  # Close the figure to prevent memory leaks
    
    st.subheader("Open Interest Imbalance")
    fig2 = plt_bar_oiImbalance(df.copy())
    st.pyplot(fig2)
    plt.close(fig2)  # Close the figure to prevent memory leaks
    
    # Display positions table
    st.subheader("Positions")
    st.dataframe(
        df[['pair', 'isBuy', 'trader', 'notional', 'collateral', 'leverage', 'uPnl', 'openPrice', 'lastPrice']], 
        width=1200  # Adjust this value as needed
    )

    # Display PnL by trader
    st.subheader("PnL by Trader")
    trader_pnl = df[['trader', 'uPnl']].groupby('trader').sum().reset_index().sort_values('uPnl', ascending=False)
    st.dataframe(trader_pnl, width=800)
    
    # Auto-refresh the app only if the checkbox is checked
    if auto_refresh:
        st.empty()
        time.sleep(5)  # Wait for 5 seconds as mentioned in the checkbox label
        st.rerun()

if __name__ == '__main__':
    main()
