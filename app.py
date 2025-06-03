import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Título y descripción
st.title("📊 Analizador de Acciones con Scoring Técnico")
st.markdown("Introduce un **ticker** (por ejemplo: `AAPL`, `MSFT`, `ACN`) para analizar KPIs técnicos.")

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

            last = data.iloc[-1]

            # Scoring simple
            score = 0
            reasons = []

            if 5 < stock.info.get("trailingPE", np.nan) < 25:
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

            st.subheader(f"Último precio de cierre: **{last['Close']:.2f} USD**")
            st.metric("Scoring técnico", f"{score} / 5", help="\n".join(reasons))

            # Mostrar tabla resumen
            st.write("### Indicadores técnicos (último día)")
            st.dataframe(last[["Close", "SMA_20", "SMA_50", "RSI", "MACD"]].round(2))

            # Gráfico interactivo
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Precio cierre", line=dict(width=2)))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA_20"], name="SMA 20", line=dict(dash="dot")))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA_50"], name="SMA 50", line=dict(dash="dash")))
            fig.update_layout(title=f"Precio de {ticker.upper()} y Medias Móviles", xaxis_title="Fecha", yaxis_title="USD")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {str(e)}")
