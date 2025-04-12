import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def open_trades_endpoint():
    # Define the GraphQL endpoint URL
    url = os.getenv('OST_SUBGRAPH_URL')

    # Define the GraphQL query
    query = """
    query getTrades {
      trades(where: {isOpen:true}, first: 10000) {
        timestamp
        pair {
          from
          to
        }
        index
        tradeID
        tradeType
        takeProfitPrice
        stopLossPrice
        trader
        collateral
        leverage
        notional
        tradeNotional
        openPrice
        closePrice
        isBuy
        isOpen
        funding
        rollover
      }
    }
    """

    # Create the request payload
    payload = {
        "query": query
    }

    # Make the POST request to the GraphQL endpoint
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Set last timestamp in lastUpdate
        
        print(f"Retrieved {len(data.get('data', {}).get('trades', []))} open trades")
        
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None


def load_open_trades(updateInterval_min, forceUpdate=False):
    # Define the file path
    file_path = '../data/trades_data.json'
    
    # Check if we need to update the data
    should_update = forceUpdate
    
    if not should_update and os.path.exists(file_path):
        # Check if file exists and if it's recent enough based on updateInterval
        file_modified_time = os.path.getmtime(file_path)
        current_time = datetime.now().timestamp()
        time_diff = current_time - file_modified_time
        
        # If file is older than updateInterval (in seconds), update it
        if time_diff/60 > updateInterval_min:
            should_update = True
    else:
        # File doesn't exist, so we need to update
        should_update = True
    
    # If we need to update, call the API
    if should_update:
        print("Fetching fresh data from API...")
        data = open_trades_endpoint()
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the data to file
        if data:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data saved to {file_path}")
            # return loaded dataframe
            return pd.DataFrame(data['data']['trades'])
        else:
            print("Failed to fetch data from API")
            # If API call fails but file exists, fall back to file
            if os.path.exists(file_path):
                print(f"Falling back to existing file: {file_path}")
            else:
                print(f"No existing file found at {file_path}")
                return None
    
    # Read from file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"Loaded data from {file_path}")
        df = pd.DataFrame(data['data']['trades'])
        return df
    except Exception as e:
        print(f"Error loading data from file: {e}")
        return None

def clean_open_trades(df: pd.DataFrame) -> pd.DataFrame:
    # Prepare trades data
    df['openPrice'] = df['openPrice'].astype(float) / 1e18
    df['takeProfitPrice'] = df['takeProfitPrice'].astype(float) / 1e18
    df['stopLossPrice'] = df['openPrice'].astype(float) / 1e18
    df['funding'] = df['funding'].astype(float) / 1e18
    df['rollover'] = df['rollover'].astype(float) / 1e18
    df['notional'] = df['notional'].astype(float) / 1e6
    df['tradeNotional'] = df['tradeNotional'].astype(float) / 1e18
    df['leverage'] = df['leverage'].astype(float) / 1e2
    df['collateral'] = df['collateral'].astype(float) / 1e6

    df['pair'] = df['pair'].apply(lambda x: x['from'] + x['to'])
    
    df_clean = df.copy()

    return df_clean

def latest_prices_endpoint() -> pd.DataFrame:
    # Define the API endpoint URL
    url = os.getenv('OST_PRICE_LISTENER')
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make the GET request to the API endpoint
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        print(f"Retrieved latest prices data")
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

def latest_prices() -> pd.DataFrame:
    # Load data
    data = latest_prices_endpoint()
    # Clean
    df = pd.DataFrame(data)
    df['pair'] = df['from'] + df['to']

    df_prices = df[['pair', 'mid']].copy()
    df_prices.rename(columns={'mid': 'lastPrice'}, inplace=True)
    df_prices['lastPrice'] = df_prices['lastPrice'].astype(float)

    return df_prices

def compute_uPnl(openPrice, lastPrice, isBuy, notional):
    abs_uPnl = (lastPrice - openPrice) / openPrice * notional
    direction_factor = 1 if isBuy else -1
    return direction_factor * abs_uPnl

def get_open_trades_uPnl(df_trades) -> pd.DataFrame:
    # Load latest prices
    df_prices = latest_prices()
    # JOIN LEFT prices on open_trades df
    df_trades_prices =  df_trades.merge(df_prices, how='left', on='pair')
    df_trades_prices['uPnl'] = df_trades_prices.apply(
        lambda row: compute_uPnl(openPrice=row['openPrice'], lastPrice=row['lastPrice'], isBuy=row['isBuy'], notional=row['notional']),
        axis=1
    )

    return df_trades_prices

if __name__ == '__main__':
    #print(open_trades_endpoint())
    print(latest_prices())