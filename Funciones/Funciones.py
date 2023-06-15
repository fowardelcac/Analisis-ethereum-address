import pandas as pd
import matplotlib.pyplot as plt
from requests import get
from datetime import datetime
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
print(API_KEY)
BASE_URL = "https://api.etherscan.io/api"
ETHER_VALUE = 10**18

def make_api_url(module, action, address, **kwargs):
	url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

	for key, value in kwargs.items():
		url += f"&{key}={value}"

	return url

def get_account_balance(address):
	balance_url = make_api_url("account", "balance", address, tag="latest")
	response = get(balance_url)
	data = response.json()

	value = int(data["result"]) / ETHER_VALUE
	return value

def get_transactions(address):
  transactions_url = make_api_url("account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
  response = get(transactions_url)
  data = response.json()["result"]
  df = pd.DataFrame(data)
  df = df.filter(['blockNumber', 'timeStamp', 'from', 'to', 'value', 'gasPrice', 'gasUsed'], axis=1)
  df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
  columnas_ = ['blockNumber', 'value', 'gasPrice', 'gasUsed']
  for i in columnas_:
    df[i] = pd.to_numeric(df[i], errors='coerce')

  df['value(Eth)'] = df.value / ETHER_VALUE
  df['Gas(Eth)'] = (df.gasPrice * df.gasUsed) / ETHER_VALUE
  return df.set_index('blockNumber').drop(['value'], axis=1)

def get_tokens_tx(address):
  get_tokens_tx_url = make_api_url('account', 'tokentx', address, page=1, offset=150, startblock = 0, endblock = 27025780, sort = 'dsc')

  response = get(get_tokens_tx_url)
  if response.json()['message'] == 'No transactions found':
    st.write("'No existen tx con este tipo de tokens'")
  else:
      data = pd.DataFrame(response.json()["result"])
      df = data.filter(['blockNumber',	'timeStamp','from', 'to', 'contractAddress', 'value', 'tokenName', 'tokenSymbol', 'tokenDecimal'], axis=1)
      df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
      columnas_ = ['blockNumber', 'value', 'tokenDecimal']
      for i in columnas_:
        df[i] = pd.to_numeric(df[i], errors='coerce')
      df.value = df.value  / (10 ** df.tokenDecimal)
      return df.set_index('blockNumber')

def get_nft_response(address):
    get_tokens_tx_url = make_api_url('account', 'tokennfttx', address, page = 1, offset=150, startblock = 0, endblock = 27025780, sort = 'dsc')
    resp = get(get_tokens_tx_url)
    return resp.json()

def edit_nft(response):
    data = pd.DataFrame(response)
    df = data.filter(['blockNumber', 'timeStamp', 'from', 'to', 'contractAddress', 'tokenName', 'tokenSymbol', 'tokenDecimal'], axis=1)
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    columnas_ = ['blockNumber', 'tokenDecimal']
    for i in columnas_:
      df[i] = pd.to_numeric(df[i], errors='coerce')
    df = df.set_index('blockNumber')
    return df

def get_balance_erc20(address, contractaddress, decimales):
    get_erc20_balance = make_api_url('account', 'tokenbalance', address, contractaddress = contractaddress )
    response = get(get_erc20_balance)
    data = response.json()["result"]
    return float(data) / (10**decimales)

def get_eth_px():
  px_url = BASE_URL + f"?module={'stats'}&action={'ethprice'}&apikey={API_KEY}"
  response = get(px_url)
  rdo = response.json()["result"]
  return rdo['ethusd']

def get_balance_usd(address):
    eth_balance = get_account_balance(address)
    ethusd = round(float(get_eth_px()) * eth_balance, 2)
    
    return eth_balance, ethusd 

@st.cache_data 
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


