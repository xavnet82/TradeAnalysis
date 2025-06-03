import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Lista estática de los 50 tickers más representativos del S&P 500
# (por capitalización a enero de 2025, orden solo a efectos de top-50)
TOP50_SP500 = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "META", "TSLA", "BRK-B", "UNH",
    "JNJ", "V", "PG", "MA", "LLY", "JPM", "HD", "PEP", "KO", "DIS",
    "BAC", "CMCSA", "NFLX", "XOM", "PFE", "WMT", "MCD", "MRK", "ABT", "ADBE",
    "CRM", "COST", "CSCO", "TXN", "INTC", "MDT", "WFC", "QCOM", "CVX", "AMGN",
    "DHR", "LIN", "HON", "UPS", "ACN", "ORCL", "ABBV", "IBM", "NEE", "T"
]

@st.cache_data(show_spinner=False)
def fetch_and_compute_indicators(ticker: str, period: str):
    """
    Descarga el histórico de `ticker` en el periodo dado y
    calcula:
      - SMA_20, SMA_50,
      - RSI (14),
      - EMA_12, EMA_26, MACD,
      - Volume_Avg_10
    Devuelve el DataFrame con esas columnas, o None si falla.
    """
    try:
        data = yf.download(ticker, period=period, progress=False)
    except Exception:
        return None

    if data is None or data.empty:
        return None

    # Eliminar columnas completamente vacías (por si falla descarga parcial)
    data = data.dropna(how="all")
    if data.empty:
        return None

    # Indicadores técnicos
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()

    # RSI 14 días (calculado manualmente)
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # MACD (EMA 12 - EMA 26) y señal (EMA 9 del MACD)
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA_12"] - data["EMA_26"]

    # Volumen promedio de 10 días
    data["Volume_Avg_10"] = data["Volume"].rolling(window=10).mean()

    # Eliminar filas donde falte alguno de estos indicadores esenciales
    data = data.dropna(subset=["SMA_20", "SMA_50", "RSI", "MACD", "Volume_Avg_10"])
    if data.empty:
        return None

    return data

def compute_scores(data: pd.DataFrame, per: float):
    """
    A partir del DataFrame con indicadores y el PER, calcula:
      - score técnico (0–6) y razones en una lista de strings
      - rec_score (0–100) y justificación en lista de strings
    Devuelve: (score_int, rec_score_float, razones_texto, justificacion_texto)
    """
    last = data.iloc[-1]
    score = 0
    razones = []

    # 1. PER (fundamental)
    if 5 < per < 25:
        score += 1
        razones.append("✔️ PER entre 5 y 25")
    else:
        razones.append("❌ PER fuera de [5,25]")

    # 2. Precio > SMA_20
    if last["Close"] > last["SMA_20"]:
        score += 1
        razones.append("✔️ Precio > SMA 20 (tendencia media alcista)")
    else:
        razones.append("❌ Precio < SMA 20")

    # 3. Precio > SMA_50
    if last["Close"] > last["SMA_50"]:
        score += 1
        razones.append("✔️ Precio > SMA 50 (tendencia larga alcista)")
    else:
        razones.append("❌ Precio < SMA 50")

    # 4. RSI en zona neutral (40–60)
    if 40 <= last["RSI"] <= 60:
        score += 1
        razones.append("✔️ RSI en zona neutral (40–60)")
    else:
        if last["RSI"] < 40:
            razones.append("❌ RSI < 40 (momentum bajista/sobreventa)")
        else:
            razones.append("❌ RSI > 60 (momentum alcista/sobrecompra)")

    # 5. MACD > 0
    if last["MACD"] > 0:
        score += 1
        razones.append("✔️ MACD positivo (tendencia alcista)")
    else:
        razones.append("❌ MACD negativo (tendencia bajista)")

    # 6. Volumen actual > Volumen promedio 10 días
    if last["Volume"] > last["Volume_Avg_10"]:
        score += 1
        razones.append("✔️ Volumen actual > promedio 10 días")
    else:
        razones.append("❌ Volumen actual < promedio 10 días")

    # --- Cálculo de rec_score (0–100) ---
    rec_score = 0.0
    justificacion = []

    # (a) Base de 60 puntos según score técnico (6 puntos → 60 pts)
    rec_score += (score / 6) * 60
    justificacion.append(f"Score técnico base = {(score/6)*60:.1f} pts")

    # (b) Tendencia en últimos 5 cierres (+/- 10 puntos máximo)
    ultimos5 = data["Close"].iloc[-5:]
    var_pct = (ultimos5.iloc[-1] - ultimos5.iloc[0]) / ultimos5.iloc[0] * 100
    if var_pct > 0:
        añadidos = min(var_pct, 10)
        rec_score += añadidos
        justificacion.append(f"Tendencia 5d: +{var_pct:.1f}% → +{añadidos:.1f} pts")
    else:
        añadidos = max(var_pct, -10)
        rec_score += añadidos
        justificacion.append(f"Tendencia 5d: {var_pct:.1f}% → {añadidos:.1f} pts")

    # (c) Ajuste por PER extremo (<5 o >40 penaliza -10)
    if pd.notna(per):
        if per < 5 or per > 40:
            rec_score -= 10
            justificacion.append("PER extremo (<5 o >40) → -10 pts")
        else:
            justificacion.append("PER en rango aceptable")

    # Limitar rec_score al intervalo [0, 100]
    rec_score = max(0, min(100, rec_score))
    justificacion.append(f"Rec_score final ajustado a [0,100]: {rec_score:.1f}")

    return score, rec_score, "\n".join(razones), "\n".join(justificacion)

# ---------- Interfaz Streamlit ----------

st.set_page_config(layout="wide")
st.title("📈 Analizador Top 50 Acciones S&P 500")
st.markdown(
    """
    Esta app descarga las 50 principales acciones del S&P 500 (por capitalización),
    calcula indicadores técnicos y muestra un **score técnico (0–6)** y un 
    **índice de recomendación (0–100)** con justificación.
    """
)

period = st.selectbox("Periodo de análisis:", ["3mo", "6mo", "1y", "2y"], index=2)

if st.button("🔍 Analizar Top 50"):
    with st.spinner("⏳ Descargando datos y calculando indicadores…"):
        resultados = []

        for tk in TOP50_SP500:
            data = fetch_and_compute_indicators(tk, period)
            if data is None or data.empty:
                continue

            per = yf.Ticker(tk).info.get("trailingPE", np.nan)
            score, rec_score, razones_texto, justificacion_texto = compute_scores(data, per)

            resultados.append({
                "Ticker": tk,
                "PER": round(per, 2) if pd.notna(per) else np.nan,
                "Score_Técnico": score,
                "Rec_Score": round(rec_score, 1),
                "Razones": razones_texto,
                "Justificación": justificacion_texto
            })

        if len(resultados) == 0:
            st.error("No se pudo obtener datos de ningún ticker.")
        else:
            # Crear un DataFrame y ordenarlo por Rec_Score descendente
            df_resumen = pd.DataFrame(resultados).sort_values(by="Rec_Score", ascending=False).reset_index(drop=True)

            # Mostrar tabla resumen
            st.subheader("🏆 Top 50 - Tabla de Resumen")
            st.dataframe(
                df_resumen[["Ticker", "PER", "Score_Técnico", "Rec_Score"]],
                use_container_width=True
            )

            st.markdown("---")
            st.subheader("🔎 Justificación detallada por acción")
            # Para cada fila, mostrar un expander con explicaciones
            for _, row in df_resumen.iterrows():
                ticker_label = row["Ticker"]
                with st.expander(f"{ticker_label}  → Rec_Score: {row['Rec_Score']}"):
                    st.markdown(f"**PER**: {row['PER']}")
                    st.markdown(f"**Score Técnico (0–6)**: {row['Score_Técnico']}")
                    st.markdown("**Razones Scoring Técnico:**")
                    st.text(row["Razones"])
                    st.markdown("---")
                    st.markdown("**Justificación Recomendación (0–100):**")
                    st.text(row["Justificación"])

    st.success("✅ Análisis completado.")

