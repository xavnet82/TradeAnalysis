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

def get_all_index_tickers():
    # Tickers estándar de Yahoo Finance para índices globales
    return {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^DJI": "Dow Jones Industrial",
        "^STOXX50E": "EuroStoxx 50",
        "^FTSE": "FTSE 100",
        "^N225": "Nikkei 225",
        "^HSI": "Hang Seng",
        "^BVSP": "IBOVESPA Brasil",
        "^IBEX": "IBEX 35"
    }

def get_all_stock_tickers():
    # Subconjunto representativo; puede ampliarse o leerse desde archivo
    return {
        "AAPL": "Apple (NASDAQ)",
        "MSFT": "Microsoft (NASDAQ)",
        "GOOGL": "Alphabet (NASDAQ)",
        "AMZN": "Amazon (NASDAQ)",
        "TSLA": "Tesla (NASDAQ)",
        "NVDA": "NVIDIA (NASDAQ)",
        "BBVA.MC": "BBVA (BME)",
        "SAN.MC": "Banco Santander (BME)",
        "ITX.MC": "Inditex (BME)",
        "SAP.DE": "SAP (XETRA)",
        "OR.PA": "L'Oréal (Euronext)",
        "AIR.PA": "Airbus (Euronext)",
        "BAS.DE": "BASF (XETRA)"
    }

