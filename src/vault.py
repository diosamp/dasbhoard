import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def olp_prices_endpoint():
    url = os.getenv('OST_SUBGRAPH_URL')
    
    query = """
    query getPrice {
        shareToAssetsPriceDailies(
            first:100, 
            orderBy:  timestamp, 
            orderDirection: desc){
            sharePrice
            day
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

        data = data['data']['shareToAssetsPriceDailies']
        
        print(f"Retrieved last {len(data)} data")
        
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None
    

def load_clean_olp_prices() -> pd.DataFrame:
    data = olp_prices_endpoint()
    df = pd.DataFrame(data)

    df.rename(columns={'sharePrice': 'price'}, inplace=True)

    df['day'] = pd.to_datetime(df['day'], format='%d-%m-%Y')
    df['price'] = pd.to_numeric(df['price']) / 1e18

    return df[['day', 'price']].copy()

if __name__ == '__main__':
    df = load_clean_olp_prices()
    print(
        list(
            df.sort_values('day', ascending=False)['price']
        )
    )
