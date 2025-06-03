import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 50 principales acciones del S&P 500
TOP50_SP500 = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "NVDA", "META", "TSLA", "BRK-B", "UNH",
    "JNJ", "V", "PG", "MA", "LLY", "JPM", "HD", "PEP", "KO", "DIS",
    "BAC", "CMCSA", "NFLX", "XOM", "PFE", "WMT", "MCD", "MRK", "ABT", "ADBE",
    "CRM", "COST", "CSCO", "TXN", "INTC", "MDT", "WFC", "QCOM", "CVX", "AMGN",
    "DHR", "LIN", "HON", "UPS", "ACN", "ORCL", "ABBV", "IBM", "NEE", "T"
]

@st.cache_data(show_spinner=False)
def fetch_and_compute_indicators(ticker: str, period: str):
    try:
        data = yf.download(ticker, period=period, progress=False)
    except Exception:
        return None

    if data is None or data.empty:
        return None

    data = data.dropna(how="all")
    if data.empty:
        return None

    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()

    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA_12"] - data["EMA_26"]

    data["Volume_Avg_10"] = data["Volume"].rolling(window=10).mean()

    required_cols = ["SMA_20", "SMA_50", "RSI", "MACD", "Volume_Avg_10"]
    if not set(required_cols).issubset(set(data.columns)):
        return None

    data = data.dropna(subset=required_cols)
    if data.empty:
        return None

    return data

def compute_scores(data: pd.DataFrame, per: float):
    last = data.iloc[-1]
    score = 0
    razones = []

    if 5 < per < 25:
        score += 1
        razones.append("✔️ PER entre 5 y 25")
    else:
        razones.append("❌ PER fuera de [5,25]")

    if last["Close"] > last["SMA_20"]:
        score += 1
        razones.append("✔️ Precio > SMA 20")
    else:
        razones.append("❌ Precio < SMA 20")

    if last["Close"] > last["SMA_50"]:
        score += 1
        razones.append("✔️ Precio > SMA 50")
    else:
        razones.append("❌ Precio < SMA 50")

    if 40 <= last["RSI"] <= 60:
        score += 1
        razones.append("✔️ RSI entre 40 y 60")
    else:
        razones.append(f"❌ RSI fuera de rango: {last['RSI']:.1f}")

    if last["MACD"] > 0:
        score += 1
        razones.append("✔️ MACD positivo")
    else:
        razones.append("❌ MACD negativo")

    if last["Volume"] > last["Volume_Avg_10"]:
        score += 1
        razones.append("✔️ Volumen > promedio")
    else:
        razones.append("❌ Volumen < promedio")

    rec_score = (score / 6) * 60
    justificacion = [f"Base técnica: {(score / 6) * 60:.1f} pts"]

    # Tendencia últimos 5 días
    ult5 = data["Close"].iloc[-5:]
    var_pct = ((ult5[-1] - ult5[0]) / ult5[0]) * 100
    ajuste = min(max(var_pct, -10), 10)
    rec_score += ajuste
    justificacion.append(f"Tendencia 5d: {var_pct:.1f}% → ajuste {ajuste:.1f} pts")

    if pd.notna(per) and (per < 5 or per > 40):
        rec_score -= 10
        justificacion.append("Penalización por PER extremo: -10 pts")

    rec_score = max(0, min(100, rec_score))
    justificacion.append(f"Rec_score final: {rec_score:.1f}")

    return score, round(rec_score, 1), "\n".join(razones), "\n".join(justificacion)

# ---------- UI Streamlit ----------
st.set_page_config(layout="wide")
st.title("📈 Analizador Técnico de Acciones (Top 50 S&P 500)")
st.markdown("Evalúa acciones con indicadores técnicos y un índice de recomendación 0–100.")

period = st.selectbox("Periodo histórico", ["3mo", "6mo", "1y", "2y"], index=2)

if st.button("🔍 Analizar Top 50"):
    with st.spinner("Procesando tickers..."):
        resultados = []
        for tk in TOP50_SP500:
            data = fetch_and_compute_indicators(tk, period)
            if data is None or data.empty:
                continue

            per = yf.Ticker(tk).info.get("trailingPE", np.nan)
            score, rec_score, razones, justificacion = compute_scores(data, per)

            resultados.append({
                "Ticker": tk,
                "PER": round(per, 2) if pd.notna(per) else np.nan,
                "Score Técnico": score,
                "Recomendación": rec_score,
                "Razones": razones,
                "Justificación": justificacion
            })

    if not resultados:
        st.error("No se pudieron procesar tickers válidos.")
    else:
        df = pd.DataFrame(resultados).sort_values(by="Recomendación", ascending=False)
        st.subheader("📊 Tabla resumen")
        st.dataframe(df[["Ticker", "PER", "Score Técnico", "Recomendación"]], use_container_width=True)

        st.markdown("---")
        st.subheader("🔎 Detalle y justificación por acción")
        for _, row in df.iterrows():
            with st.expander(f"{row['Ticker']}  → {row['Recomendación']} pts"):
                st.markdown(f"**PER:** {row['PER']}")
                st.markdown(f"**Score Técnico:** {row['Score Técnico']} / 6")
                st.text(row["Razones"])
                st.markdown("---")
                st.text(row["Justificación"])
