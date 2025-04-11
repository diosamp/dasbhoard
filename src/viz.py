import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


def plt_bar_oi_isBuy(df: pd.DataFrame, save_path=None):
    df_oi_pair_direction = df[['pair', 'isBuy', 'notional']].groupby(['pair', 'isBuy']).sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.barplot(data=df_oi_pair_direction, x='pair', y='notional', hue='isBuy', 
                palette=['#ff9999', '#66b3ff'], dodge=True, ax=ax)
    
    ax.set_title('Notional Value by Pair and Direction', fontsize=14)
    ax.set_xlabel('Trading Pair', fontsize=12)
    ax.set_ylabel('Notional Value / $', fontsize=12)
    
    ax.legend(title='Direction', labels=['Sell', 'Buy'])
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close(fig)
    
    return fig

def plt_bar_oiImbalance(df: pd.DataFrame, save_path=None):
    df['imbalance'] = df.apply(lambda row: abs(row['notional']) if row['isBuy'] else -abs(row['notional']), axis=1)
    # Create bar plot of imbalances by pair
    imbalance_data = df[['pair', 'imbalance']].groupby('pair').sum().reset_index()
    
    # Add a color column to the dataframe
    imbalance_data['color'] = ['Sell' if val < 0 else 'Buy' for val in imbalance_data['imbalance']]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Use hue instead of palette with custom colors
    sns.barplot(data=imbalance_data, x='pair', y='imbalance', hue='color', 
                palette={'Sell': '#ff9999', 'Buy': '#66b3ff'}, ax=ax, legend=False)
    
    ax.set_title('Buy/Sell Imbalance by Trading Pair', fontsize=14)
    ax.set_xlabel('Trading Pair', fontsize=12)
    ax.set_ylabel('Imbalance (Positive = Net Buy, Negative = Net Sell)', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close(fig)
    
    return fig