import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Título y descripción
st.title("📊 Analizador de Acciones con Recomendación Técnica")
st.markdown("Introduce un **ticker** (por ejemplo: `AAPL`, `MSFT`, `ACN`) para analizar KPIs técnicos y obtener una recomendación.")

# Entrada del usuario
ticker = st.text_input("Ticker de la acción", "ACN")
period = st.selectbox("Periodo de análisis", ["3mo", "6mo", "1y", "2y"], index=2)

if st.button("📈 Analizar"):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)

        if data.empty:
            st.error("No se encontraron datos para ese ticker.")
        else:
            # Indicadores técnicos
            data["SMA_20"] = data["Close"].rolling(window=20).mean()
            data["SMA_50"] = data["Close"].rolling(window=50).mean()
            data["RSI"] = (
                100 - (100 / (1 + data["Close"].diff().apply(lambda x: x if x > 0 else 0).rolling(14).mean() /
                             data["Close"].diff().apply(lambda x: -x if x < 0 else 0).rolling(14).mean()))
            )
            data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
            data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
            data["MACD"] = data["EMA_12"] - data["EMA_26"]
            data["Volume_Avg_10"] = data["Volume"].rolling(window=10).mean()

            last = data.iloc[-1]

            # ---------- SCORING SIMPLE ----------
            score = 0
            reasons = []

            per = stock.info.get("trailingPE", np.nan)

            if 5 < per < 25:
                score += 1
                reasons.append("✔️ PER entre 5 y 25")

            if last["Close"] > last["SMA_20"]:
                score += 1
                reasons.append("✔️ Precio > SMA 20")

            if last["Close"] > last["SMA_50"]:
                score += 1
                reasons.append("✔️ Precio > SMA 50")

            if 40 <= last["RSI"] <= 60:
                score += 1
                reasons.append("✔️ RSI en zona neutral")

            if last["MACD"] > 0:
                score += 1
                reasons.append("✔️ MACD positivo")

            if last["Volume"] > last["Volume_Avg_10"]:
                score += 1
                reasons.append("✔️ Volumen mayor al promedio")

            st.subheader(f"Último precio de cierre: **{last['Close']:.2f} USD**")
            st.metric("Scoring técnico", f"{score} / 6", help="\n".join(reasons))

            # ---------- RECOMENDACIÓN DE INVERSIÓN (0–100) ----------
            rec_score = 0

            # 1. Scoring base (de 6 → escala a 60 pts)
            rec_score += (score / 6) * 60

            # 2. Variación última semana (tendencia reciente)
            last_5 = data["Close"].iloc[-5:]
            var_pct = ((last_5[-1] - last_5[0]) / last_5[0]) * 100
            if var_pct > 0:
                rec_score += min(var_pct, 10)  # máx 10 pts
            else:
                rec_score += max(var_pct, -10)  # penalización si ha caído

            # 3. Ajuste por PER (valoraciones extremas penalizan)
            if pd.notna(per):
                if per < 5 or per > 40:
                    rec_score -= 10

            # Limitar a [0, 100]
            rec_score = max(0, min(100, rec_score))

            st.markdown("### 🧠 Recomendación de inversión (0-100)")
            st.slider("Nivel recomendado", 0, 100, int(rec_score), disabled=True)
            if rec_score > 75:
                st.success("📈 Alta recomendación de compra")
            elif rec_score > 50:
                st.info("⚖️ Recomendación moderada")
            else:
                st.warning("📉 Baja recomendación. Analiza antes de invertir.")

            # Mostrar tabla resumen
            st.write("### Indicadores técnicos (último día)")
            st.dataframe(last[["Close", "SMA_20", "SMA_50", "RSI", "MACD", "Volume", "Volume_Avg_10"]].round(2))

            # Gráfico interactivo
            fig = go.Figure()
            fig.add_trace(go._

