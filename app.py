import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import snscrape.modules.twitter as sntwitter
import datetime
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Configuración inicial
st.set_page_config(layout="wide")
st.title("📊 Análisis Integral de un Ticker")
st.markdown("Evaluación desde tres perspectivas: Técnica, Fundamental y Sentimiento en Redes Sociales.")

# Entrada del usuario
ticker = st.text_input("Introduce el símbolo del ticker (ejemplo: AAPL)", "AAPL").upper()

# Descargar datos históricos
@st.cache_data
def descargar_datos(ticker):
    fin = datetime.date.today()
    inicio = fin - datetime.timedelta(days=365)
    datos = yf.download(ticker, start=inicio, end=fin)
    return datos

# Análisis Técnico
def analisis_tecnico(datos):
    puntuacion = 0
    justificacion = []

    # SMA
    datos['SMA20'] = datos['Close'].rolling(window=20).mean()
    datos['SMA50'] = datos['Close'].rolling(window=50).mean()
    if datos['Close'].iloc[-1] > datos['SMA20'].iloc[-1]:
        puntuacion += 20
        justificacion.append("Precio por encima de SMA20.")
    else:
        justificacion.append("Precio por debajo de SMA20.")
    if datos['Close'].iloc[-1] > datos['SMA50'].iloc[-1]:
        puntuacion += 20
        justificacion.append("Precio por encima de SMA50.")
    else:
        justificacion.append("Precio por debajo de SMA50.")

    # RSI
    delta = datos['Close'].diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    media_ganancia = ganancia.rolling(window=14).mean()
    media_perdida = perdida.rolling(window=14).mean()
    rs = media_ganancia / media_perdida
    rsi = 100 - (100 / (1 + rs))
    datos['RSI'] = rsi
    if rsi.iloc[-1] < 30:
        puntuacion += 20
        justificacion.append("RSI indica sobreventa.")
    elif rsi.iloc[-1] > 70:
        puntuacion += 10
        justificacion.append("RSI indica sobrecompra.")
    else:
        puntuacion += 15
        justificacion.append("RSI en zona neutral.")

    # MACD
    ema12 = datos['Close'].ewm(span=12, adjust=False).mean()
    ema26 = datos['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    datos['MACD'] = macd
    if macd.iloc[-1] > 0:
        puntuacion += 20
        justificacion.append("MACD positivo.")
    else:
        justificacion.append("MACD negativo.")

    # Volumen
    volumen_promedio = datos['Volume'].rolling(window=10).mean()
    if datos['Volume'].iloc[-1] > volumen_promedio.iloc[-1]:
        puntuacion += 20
        justificacion.append("Volumen actual por encima del promedio.")
    else:
        justificacion.append("Volumen actual por debajo del promedio.")

    return puntuacion, justificacion, datos

# Análisis Fundamental
def analisis_fundamental(ticker):
    info = yf.Ticker(ticker).info
    puntuacion = 0
    justificacion = []

    # PER
    per = info.get('trailingPE', None)
    if per:
        if 5 < per < 25:
            puntuacion += 25
            justificacion.append("PER en rango saludable.")
        else:
            justificacion.append("PER fuera de rango.")

    # ROE
    roe = info.get('returnOnEquity', None)
    if roe:
        if roe > 0.15:
            puntuacion += 25
            justificacion.append("ROE alto.")
        else:
            justificacion.append("ROE bajo.")

    # Margen de beneficio
    margen = info.get('profitMargins', None)
    if margen:
        if margen > 0.15:
            puntuacion += 20
            justificacion.append("Margen de beneficio alto.")
        else:
            justificacion.append("Margen de beneficio bajo.")

    # Deuda/Patrimonio
    deuda = info.get('debtToEquity', None)
    if deuda:
        if deuda < 100:
            puntuacion += 20
            justificacion.append("Deuda/Patrimonio en buen rango.")
        else:
            justificacion.append("Deuda/Patrimonio elevado.")

    # Dividendos
    dividendo = info.get('dividendYield', None)
    if dividendo:
        puntuacion += 10
        justificacion.append("Ofrece dividendos.")
    else:
        justificacion.append("No ofrece dividendos.")

    return puntuacion, justificacion

# Análisis de Sentimiento
def analisis_sentimiento(ticker):
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'${ticker} lang:en').get_items()):
        if i > 100:
            break
        tweets.append(tweet.content)
    positivos = 0
    negativos = 0
    neutrales = 0
    for tweet in tweets:
        puntaje = sia.polarity_scores(tweet)
        if puntaje['compound'] > 0.05:
            positivos += 1
        elif puntaje['compound'] < -0.05:
            negativos += 1
        else:
            neutrales += 1
    total = positivos + negativos + neutrales
    if total == 0:
        return 50, ["No se encontraron tweets."]
    porcentaje_positivo = (positivos / total) * 100
    if porcentaje_positivo > 60:
        puntuacion = 90
        justificacion = ["Sentimiento positivo predominante en redes sociales."]
    elif porcentaje_positivo < 40:
        puntuacion = 30
        justificacion = ["Sentimiento negativo predominante en redes sociales."]
    else:
        puntuacion = 60
        justificacion = ["Sentimiento mixto en redes sociales."]
    return puntuacion, justificacion

# Ejecución principal
if ticker:
    datos = descargar_datos(ticker)
    if datos.empty:
        st.error("No se pudieron obtener datos para el ticker proporcionado.")
    else:
        st.subheader("📈 Análisis Técnico")
        puntuacion_tecnica, justificacion_tecnica, datos = analisis_tecnico(datos)
        st.slider("Puntuación Técnica", 0, 100, puntuacion_tecnica, disabled=True)
        for j in justificacion_tecnica:
            st.write(f"- {j}")

        st.subheader("💼 Análisis Fundamental")

::contentReference[oaicite:75]{index=75}
 
