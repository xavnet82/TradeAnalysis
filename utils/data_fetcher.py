
import yfinance as yf
import pandas as pd

def descargar_datos(ticker):
    df = yf.download(ticker, period="1y")
    return df

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)
    df = table[0]
    return df['Symbol'].sort_values().tolist()
