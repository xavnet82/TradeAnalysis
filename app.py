
import streamlit as st
import nltk
import requests

from config import COLORS
from utils.data_fetcher import descargar_datos, get_sp500_tickers
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias
from utils.charts import generar_grafico_precio
from components.cards import render_score_card

nltk.download("vader_lexicon")

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #ffffff;
            color: #222222;
            font-size: 14px;
        }
        h1, h2, h3, h4 {
            font-size: 15px;
        }
        .stSlider > div > div {
            background: #f0f0f0;
        }
        .css-1d391kg {
            font-size: 13px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Análisis Integral de Acciones")

tickers = get_sp500_tickers()
ticker = st.selectbox("Selecciona una acción del S&P 500", tickers, index=tickers.index("AAPL") if "AAPL" in tickers else 0)

def resumen_final(score_t, score_f, score_s):
    media = int((score_t + score_f + score_s) / 3)
    if media >= 75:
        resumen = "📈 Alta recomendación de inversión."
    elif media >= 50:
        resumen = "⚖️ Recomendación moderada."
    else:
        resumen = "📉 Baja recomendación de inversión."
    return media, resumen

if ticker:
    df = descargar_datos(ticker)
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📈 Resultados")
            score_t, razones_t, df, detalles_t, tendencias_t = analizar_tecnico(df)
            render_score_card("Análisis Técnico", score_t, razones_t, COLORS["technical"])

            with st.expander("🔍 Ver detalle de indicadores técnicos"):
                headers = ["Indicador", "Resultado", "Explicación", "Tendencia"]
                indicadores = ["SMA20", "SMA50", "RSI", "MACD", "Volumen"]
                for i in range(len(indicadores)):
                    cols = st.columns([1.5, 1.5, 4, 1.5])
                    with cols[0]:
                        st.markdown(f"**{indicadores[i]}**")
                    with cols[1]:
                        st.markdown(razones_t[i])
                    with cols[2]:
                        st.markdown(detalles_t[i])
                    with cols[3]:
                        st.markdown(tendencias_t[i])

            score_f, razones_f = analizar_fundamental(ticker)
            render_score_card("Análisis Fundamental", score_f, razones_f, COLORS["fundamental"])

            score_s, razones_s = analizar_sentimiento_noticias(ticker)
            render_score_card("Sentimiento en Noticias", score_s, razones_s, COLORS["sentiment"])

            st.markdown("---")
            st.subheader("✅ Recomendación Consolidada")
            final_score, resumen = resumen_final(score_t, score_f, score_s)
            st.metric("Score Global", f"{final_score}/100")
            st.info(resumen)

            st.markdown("---")
            st.subheader("📉 Gráfico del último año (con SMA)")
            fig = generar_grafico_precio(df, ticker)
            st.pyplot(fig)

        with col2:
            st.subheader("🧠 Análisis Generado por IA")
            usar_ia = st.toggle("¿Generar análisis con IA?", value=True)
            if usar_ia:
                from openai import OpenAI

                prompt = f"""Analiza los siguientes indicadores para la acción {ticker}:
                - Score técnico: {score_t}, razones: {', '.join(razones_t)}
                - Score fundamental: {score_f}, razones: {', '.join(razones_f)}
                - Sentimiento: {score_s}, razones: {', '.join(razones_s)}
                - Score global: {final_score}/100, recomendación: {resumen}, y enriquece la información con un análisis online en profundidad, generando una recomendación resumida con todos los parámetros y overview general"""

                try:
                    client = OpenAI(api_key=st.secrets["openai_api_key"])
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        temperature=0.7,
                    )

                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response:
                        content = chunk.choices[0].delta.content or ""
                        full_response += content
                        placeholder.markdown(full_response)

                except Exception as e:
                    st.error(f"Error al llamar a OpenAI: {e}")
            else:
                st.info("La generación de análisis por IA está desactivada.")
    else:
        st.warning("⚠️ No se encontraron datos históricos.")
