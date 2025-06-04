import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")

st.set_page_config(layout="wide")
st.title("📊 Análisis Integral de Acciones")
ticker = st.text_input("Introduce un ticker (ej: AAPL, MSFT, ACN)", "AAPL").upper()

# Descargar datos históricos
@st.cache_data
def descargar_datos(ticker):
    df = yf.download(ticker, period="1y")
    return df

# Análisis técnico
def analizar_tecnico(df):
    score = 0
    justificacion = []

    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    last = df.iloc[-1]

    if last['Close'] > last['SMA20']:
        score += 20
        justificacion.append("✔️ Precio > SMA20")
    else:
        justificacion.append("❌ Precio < SMA20")

    if last['Close'] > last['SMA50']:
        score += 20
        justificacion.append("✔️ Precio > SMA50")
    else:
        justificacion.append("❌ Precio < SMA50")

    if 40 <= last['RSI'] <= 60:
        score += 20
        justificacion.append("✔️ RSI neutro")
    elif last['RSI'] < 40:
        score += 10
        justificacion.append("✔️ RSI en sobreventa")
    else:
        justificacion.append("❌ RSI en sobrecompra")

    if last['MACD'] > 0:
        score += 20
        justificacion.append("✔️ MACD positivo")
    else:
        justificacion.append("❌ MACD negativo")

    avg_vol = df['Volume'].rolling(10).mean().iloc[-1]
    if last['Volume'] > avg_vol:
        score += 20
        justificacion.append("✔️ Volumen alto")
    else:
        justificacion.append("❌ Volumen bajo")

    return score, justificacion, df

# Análisis fundamental
def analizar_fundamental(info):
    score = 0
    justificacion = []

    per = info.get("trailingPE")
    if per and 5 < per < 25:
        score += 25
        justificacion.append("✔️ PER en rango saludable")
    else:
        justificacion.append("❌ PER extremo o nulo")

    roe = info.get("returnOnEquity")
    if roe and roe > 0.15:
        score += 25
        justificacion.append("✔️ ROE alto")
    else:
        justificacion.append("❌ ROE bajo o nulo")

    margin = info.get("profitMargins")
    if margin and margin > 0.15:
        score += 20
        justificacion.append("✔️ Margen de beneficio alto")
    else:
        justificacion.append("❌ Margen bajo")

    debt = info.get("debtToEquity")
    if debt and debt < 100:
        score += 20
        justificacion.append("✔️ Deuda controlada")
    else:
        justificacion.append("❌ Deuda elevada")

    if info.get("dividendYield"):
        score += 10
        justificacion.append("✔️ Ofrece dividendos")
    else:
        justificacion.append("❌ No ofrece dividendos")

    return score, justificacion

# Análisis de sentimiento desde RSS público
def analizar_sentimiento_rss(ticker):
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    try:
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        titles = [item.find("title").text for item in root.findall(".//item")]
    except:
        return 50, ["❌ No se pudieron cargar titulares."]

    if not titles:
        return 50, ["❌ Sin titulares recientes."]

    sia = SentimentIntensityAnalyzer()
    positives = 0
    negatives = 0
    neutrals = 0

    for title in titles:
        score = sia.polarity_scores(title)["compound"]
        if score > 0.05:
            positives += 1
        elif score < -0.05:
            negatives += 1
        else:
            neutrals += 1

    total = positives + negatives + neutrals
    if total == 0:
        return 50, ["❌ Sin resultados útiles para análisis."]

    pct_pos = positives / total * 100
    if pct_pos > 60:
        return 85, ["✔️ Sentimiento claramente positivo"]
    elif pct_pos < 40:
        return 30, ["❌ Sentimiento negativo dominante"]
    else:
        return 55, ["⚖️ Sentimiento mixto o neutro"]

# Consolidar resultado final
def resumen_final(score_t, score_f, score_s):
    media = int((score_t + score_f + score_s) / 3)
    if media >= 75:
        resumen = "📈 Alta recomendación de inversión basada en datos técnicos, fundamentales y sociales."
    elif media >= 50:
        resumen = "⚖️ Recomendación moderada. Existen señales mixtas entre las fuentes analizadas."
    else:
        resumen = "📉 Baja recomendación de inversión. Precaución ante señales negativas o débiles."

    return media, resumen

# Ejecutar análisis
if ticker:
    df = descargar_datos(ticker)
    if not df.empty:
        info = yf.Ticker(ticker).info

        st.subheader("📈 Análisis Técnico")
        score_t, razones_t, df = analizar_tecnico(df)
        st.slider("Score Técnico", 0, 100, score_t, disabled=True)
        for r in razones_t:
            st.caption(r)

        st.subheader("📊 Análisis Fundamental")
        score_f, razones_f = analizar_fundamental(info)
        st.slider("Score Fundamental", 0, 100, score_f, disabled=True)
        for r in razones_f:
            st.caption(r)

        st.subheader("💬 Sentimiento (Noticias Yahoo Finance)")
        score_s, razones_s = analizar_sentimiento_rss(ticker)
        st.slider("Score Sentimiento", 0, 100, score_s, disabled=True)
        for r in razones_s:
            st.caption(r)

        # Justificación global
        st.markdown("---")
        st.subheader("✅ Justificación Consolidada")
        final_score, resumen = resumen_final(score_t, score_f, score_s)
        st.metric("Recomendación Global", f"{final_score}/100")
        st.info(resumen)

        # Gráfico final
        st.markdown("---")
        st.subheader("📉 Evolución de Precio (último año) con SMA y MACD")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.index, df['Close'], label='Precio', linewidth=1.5)
        ax.plot(df.index, df['SMA20'], label='SMA20', linestyle='--')
        ax.plot(df.index, df['SMA50'], label='SMA50', linestyle='--')
        ax.set_title(f'{ticker} - Precio y Medias Móviles')
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("No se encontraron datos históricos.")
