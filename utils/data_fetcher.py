
import yfinance as yf

def descargar_datos(ticker):
    df = yf.download(ticker, period="1y")
    return df
