import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data(show_spinner=False)
def get_sp500_tickers():
    """
    Descarga y parsea la tabla de Wikipedia para obtener los tickers del S&P 500.
    Devuelve la lista completa.  
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url, header=0)[0]
    # En los tickers con '.', se reemplaza por '-' para yfinance
    tickers = [t.replace(".", "-") for t in df["Symbol"].tolist()]
    return tickers

@st.cache_data(show_spinner=False)
def fetch_and_compute_indicators(ticker: str, period: str):
    """
    Descarga el histórico de `ticker` en el periodo dado (e.g. "6mo", "1y") y
    calcula:
      - SMA_20, SMA_50,
      - RSI (14),
      - EMA_12, EMA_26, MACD,
      - Volume_Avg_10
    Devuelve el DataFrame con esas columnas añadidas.
    """
    data = yf.download(ticker, period=period, progress=False)
    if data.empty:
        return None

    # Asegurarse de que no queden NaN por completo
    data = data.dropna(how="all")
    # Indicadores técnicos
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()

    # RSI manual (14)
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA_12"] - data["EMA_26"]

    # Volumen promedio 10 días
    data["Volume_Avg_10"] = data["Volume"].rolling(window=10).mean()

    # Limpiar filas con NaN en indicadores esenciales
    data = data.dropna(subset=["SMA_20", "SMA_50", "RSI", "MACD", "Volume_Avg_10"])
    return data

def compute_scores(data: pd.DataFrame, per: float):
    """
    Dado un DataFrame ya con indicadores, extrae la última fila y genera:
      - score técnico (0-6) con razones en lista de strings
      - rec_score (0-100) con lógica ponderada y pequeñas explicaciones
    Devuelve: (score_int, rec_score_float, razones_texto, justificación_texto)
    """
    last = data.iloc[-1]
    score = 0
    razones = []

    # 1. PER
    if 5 < per < 25:
        score += 1
        razones.append("✔️ PER entre 5 y 25")
    else:
        razones.append("❌ PER fuera de rango (valores <5 o >25 penalizan)")

    # 2. Precio > SMA_20
    if last["Close"] > last["SMA_20"]:
        score += 1
        razones.append("✔️ Precio > SMA 20 (tendencia alcista media)")
    else:
        razones.append("❌ Precio < SMA 20 (tendencia débil)")

    # 3. Precio > SMA_50
    if last["Close"] > last["SMA_50"]:
        score += 1
        razones.append("✔️ Precio > SMA 50 (tendencia alcista a largo plazo)")
    else:
        razones.append("❌ Precio < SMA 50 (tendencia bajista a largo plazo)")

    # 4. RSI en zona neutral (40-60)
    if 40 <= last["RSI"] <= 60:
        score += 1
        razones.append("✔️ RSI en zona neutral (40–60), listo para moverse")
    else:
        if last["RSI"] < 40:
            razones.append("❌ RSI < 40 (sobreventa o momentum bajista)")
        else:
            razones.append("❌ RSI > 60 (sobrecompra o momentum alcista)")

    # 5. MACD positivo
    if last["MACD"] > 0:
        score += 1
        razones.append("✔️ MACD positivo (tendencia alcista)")
    else:
        razones.append("❌ MACD negativo (tendencia bajista)")

    # 6. Volumen actual > Volumen promedio 10
    if last["Volume"] > last["Volume_Avg_10"]:
        score += 1
        razones.append("✔️ Volumen actual superior al promedio 10 días (interés)")
    else:
        razones.append("❌ Volumen actual inferior a promedio 10 días (bajo interés)")

    # --- Ahora el rec_score (0–100) ---
    # a) Base sobre score técnico: (score / 6) * 60
    rec_score = (score / 6) * 60

    # b) Comportamiento últimos 5 cierres (tendencia reciente)
    ultimos5 = data["Close"].iloc[-5:]
    var_pct = (ultimos5.iloc[-1] - ultimos5.iloc[0]) / ultimos5.iloc[0] * 100
    if var_pct > 0:
        rec_score += min(var_pct, 10)  # máximo +10 puntos si ha subido
    else:
        rec_score += max(var_pct, -10)  # penaliza hasta -10 si ha caído

    # c) Ajuste extra por PER fuera de rango estricto (<5 o >40 → -10)
    justificacion = []
    if pd.notna(per):
        if per < 5 or per > 40:
            rec_score -= 10
            justificacion.append("PER muy extremo (fuera de [5,40]): -10 puntos")
        else:
            justificacion.append("PER dentro de rango aceptable")

    # Asegurar que rec_score quede en [0, 100]
    rec_score = max(0, min(100, rec_score))

    # Construir texto de justificación de rec_score
    justificacion.insert(0, f"Score técnico base = {(score/6)*60:.1f}")
    justificacion.append(f"Tendencia 5d: {'+' if var_pct>0 else ''}{var_pct:.1f}% → {'+'+str(min(var_pct,10)) if var_pct>0 else str(max(var_pct,-10))} puntos")
    justificacion.append(f"Valor final ajustado a rango [0,100]")

    razones_texto = "\n".join(razones)
    justificacion_texto = "\n".join(justificacion)

    return score, rec_score, razones_texto, justificacion_texto

# ---------- UI de Streamlit ----------

st.set_page_config(layout="wide")
st.title("📈 Analizador Top 50 Acciones S&P 500")
st.markdown(
    """
    Esta aplicación descarga las 50 primeras acciones del S&P 500, 
    calcula indicadores técnicos y genera un score de recomendación (0–100) para cada una. 
    """
)

period = st.selectbox("Selección de periodo para histórico:", ["3mo", "6mo", "1y", "2y"], index=2)
if st.button("🔍 Analizar Top 50"):
    with st.spinner("Descargando datos y calculando indicadores para 50 tickers…"):
        # 1. Obtener lista de tickers y quedarnos con los primeros 50
        all_tickers = get_sp500_tickers()
        top50 = all_tickers[:50]

        resultados = []

        for tk in top50:
            data = fetch_and_compute_indicators(tk, period)
            if data is None or data.empty:
                continue

            # Extraer PER si existe
            per = yf.Ticker(tk).info.get("trailingPE", np.nan)

            score, rec_score, razones_texto, justificacion_texto = compute_scores(data, per)

            resultados.append({
                "Ticker": tk,
                "Score_Tecnico": score,
                "Rec_Score": round(rec_score, 1),
                "PER": round(per, 2) if pd.notna(per) else np.nan,
                "Razones": razones_texto,
                "Justificación": justificacion_texto
            })

        if len(resultados) == 0:
            st.error("No se pudo obtener datos de ningún ticker.")
        else:
            # 2. Crear DataFrame de resumen ordenado por Rec_Score descendente
            df_resumen = pd.DataFrame(resultados).sort_values(by="Rec_Score", ascending=False).reset_index(drop=True)

            # 3. Mostrar tabla resumen
            st.subheader("🏆 Top 50 - Resumen de Scoring y Recomendación")
            st.dataframe(
                df_resumen[["Ticker", "PER", "Score_Tecnico", "Rec_Score"]],
                use_container_width=True
            )

            st.markdown("---")
            st.subheader("🔎 Justificación detallada por acción")
            # 4. Mostrar un expander por cada ticker con la justificación
            for idx, row in df_resumen.iterrows():
                with st.expander(f"{row['Ticker']}  → Rec_Score: {row['Rec_Score']}"):
                    st.markdown(f"**PER**: {row['PER']}")
                    st.markdown(f"**Score Técnico (0–6)**: {row['Score_Tecnico']}")
                    st.markdown("**Razones Scoring Técnico:**")
                    st.text(row["Razones"])
                    st.markdown("---")
                    st.markdown("**Justificación Recomendación (0–100):**")
                    st.text(row["Justificación"])
                    st.markdown("---")

    st.success("✅ Cálculo completado.")

