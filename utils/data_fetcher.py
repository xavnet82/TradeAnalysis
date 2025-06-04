import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    # Lista simplificada o puedes parsear desde Wikipedia
    return [
        "AAPL", "ACN", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "JPM", "JNJ", "V", "PG"
    ]

def get_nasdaq100_tickers():
    return [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOG", "TSLA", "META", "PEP", "AVGO", "COST"
    ]

def get_eurostoxx50_tickers():
    return [
        "ADS.DE", "AIR.PA", "ALV.DE", "BNP.PA", "DAI.DE", "ENEL.MI", "IBE.MC", "OR.PA", "SAN.MC", "SAP.DE"
    ]

def get_ibex35_tickers():
    return [
        "SAN.MC", "BBVA.MC", "ITX.MC", "TEF.MC", "REP.MC", "AENA.MC", "ACS.MC", "GRF.MC"
    ]

def get_nasdaq_tickers():
    # Lista ejemplo – idealmente sustituible por parsing o fuente externa
    return [
        "AAPL", "ACN", "TSLA", "NVDA", "AMD", "INTC", "PYPL", "ADBE", "NFLX"
    ]

def descargar_datos(ticker, periodo="1y", intervalo="1d"):
    try:
        df = yf.download(ticker, period=periodo, interval=intervalo, progress=False)
        return df
    except Exception as e:
        return pd.DataFrame()
