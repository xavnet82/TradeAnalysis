import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import random

# -----------------------------
# CONFIGURACIÓN DE LA APP
# -----------------------------
st.set_page_config(layout="centered")
st.title("📊 Análisis Integral de un Ticker")
st.markdown("Evalúa una acción desde tres enfoques: **Técnico**, **Fundamental** y **Sentimiento Social**.")

# -----------------------------
# INPUT DEL USUARIO
# -----------------------------
ticker = st.text_input("Introduce un ticker (ej: AAPL, MSFT, ACN)", "AAPL").upper()
period = st.selectbox("Periodo histórico", ["6mo", "1y", "2y"], index=1)

# -----------------------------
# FUNCIÓN: ANÁLISIS TÉCNICO
# -----------------------------
def analizar_tecnico(df):
    razones = []
    score = 0

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    ultimo_rsi = rsi.iloc[-1]

    if 40 <= ultimo_rsi <= 60:
        score += 25
        razones.append("RSI en zona neutral.")
    elif ultimo_rsi < 40:
        score += 15
        razones.append("RSI en sobreventa.")
    else:
        score += 10
        razones.append("RSI en sobrecompra.")

    # SMA
    sma_20 = df["Close"].rolling(20).mean()
    sma_50 = df["Close"].rolling(50).mean()
    if df["Close"].iloc[-1] > sma_20.iloc[-1]:
        score += 20
        razones.append("Precio por encima de SMA 20.")
    else:
        razones.append("Precio por debajo de SMA 20.")

    if df["Close"].iloc[-1] > sma_50.iloc[-1]:
        score += 20
        razones.append("Precio por encima de SMA 50.")
    else:
        razones.append("Precio por debajo de SMA 50.")

    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    if macd.iloc[-1] > 0:
        score += 20
        razones.append("MACD positivo.")
    else:
        razones.append("MACD negativo.")

    # Volumen
    avg_vol = df["Volume"].rolling(10).mean()
    if df["Volume"].iloc[-1] > avg_vol.iloc[-1]:
        score += 15
        razones.append("Volumen actual mayor al promedio.")
    else:
        razones.append("Volumen actual menor al promedio.")

    return int(score), " | ".join(razones)

# -----------------------------
# FUNCIÓN: ANÁLISIS FUNDAMENTAL
# -----------------------------
def analizar_fundamental(info):
    razones = []
    score = 0

    try:
        if 5 < info.get("trailingPE", 0) < 25:
            score += 25
            razones.append("PER en rango saludable.")
        else:
            razones.append("PER fuera de rango.")

        roe = info.get("returnOnEquity", 0)
        if roe and roe > 0.15:
            score += 25
            razones.append("ROE alto.")
        else:
            razones.append("ROE bajo o nulo.")

        margin = info.get("profitMargins", 0)
        if margin and margin > 0.15:
            score += 20
            razones.append("Margen de beneficio alto.")
        else:
            razones.append("Margen bajo.")

        debt = info.get("debtToEquity", 100)
        if debt < 100:
            score += 20
            razones.append("Endeudamiento bajo.")
        else:
            razones.append("Endeudamiento elevado.")

        if info.get("dividendYield", 0):
            score += 10
            razones.append("Ofrece dividendos.")
        else:
            razones.append("No ofrece dividendos.")
    except:
        razones.append("No se pudieron obtener todos los datos.")
        return 0, "Datos incompletos."

    return int(score), " | ".join(razones)

# -----------------------------
# FUNCIÓN: ANÁLISIS SOCIAL (SIMULADO)
# -----------------------------
def analizar_sentimiento_social(ticker):
    # Simulación: en una versión real usarías una API de sentimiento o scraping de Twitter/Reddit
    sentimientos = {
        "positivo": ["Muy buenas expectativas en redes.", "Opiniones positivas de analistas."],
        "neutral": ["Opinión estable, sin cambios recientes.", "Sin noticias relevantes en redes."],
        "negativo": ["Alerta de caída: se discuten problemas.", "Malas noticias o resultados negativos."]
    }

    sentimiento = random.choice(["positivo", "neutral", "negativo"])
    frases = sentimientos[sentimiento]

    if sentimiento == "positivo":
        return 85, " | ".join(frases)
    elif sentimiento == "neutral":
        return 55, " | ".join(frases)
    else:
        return 30, " | ".join(frases)

# -----------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------
if ticker:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if not df.empty:
        info = stock.info

        st.markdown("### 📈 Análisis Técnico")
        score_t, razones_t = analizar_tecnico(df)
        st.slider("Resultado Técnico", 0, 100, score_t, disabled=True)
        st.caption(razones_t)

        st.markdown("### 📊 Análisis Fundamental")
        score_f, razones_f = analizar_fundamental(info)
        st.slider("Resultado Fundamental", 0, 100, score_f, disabled=True)
        st.caption(razones_f)

        st.markdown("### 💬 Análisis de Sentimiento (Redes Sociales)")
        score_s, razones_s = analizar_sentimiento_social(ticker)
        st.slider("Sentimiento Social", 0, 100, score_s, disabled=True)
        st.caption(razones_s)
    else:
        st.error("No se pudo obtener el histórico del ticker.")

