import requests
import streamlit as st

res = requests.get('https://cloud.chaoslabs.co/query/api/ostium/unrealized-pnl')

res = res.json()
st.metric('total unrealized PNL', sum([res['unrealizedPnlPairs'][pair] for pair in res['unrealizedPnlPairs']]))
st.bar_chart(res['unrealizedPnlPairs'])
st.write(res)