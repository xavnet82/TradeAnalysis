
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
        body, .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        .css-18e3th9 {
            background-color: #1e1e1e;
        }
        .stSlider > div > div {
            background: #2c2c2c;
        }
        .st-bb {
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Análisis Integral de Acciones")

tickers = get_sp500_tickers()
ticker = st.selectbox("Selecciona una acción del S&P 500", tickers, index=tickers.index("AAPL"))

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
            score_t, razones_t, df = analizar_tecnico(df)
            render_score_card("Análisis Técnico", score_t, razones_t, COLORS["technical"])

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
            prompt = f"""Resume y analiza los siguientes indicadores para la acción {ticker}:
            - Score técnico: {score_t}, razones: {', '.join(razones_t)}
            - Score fundamental: {score_f}, razones: {', '.join(razones_f)}
            - Sentimiento: {score_s}, razones: {', '.join(razones_s)}
            - Score global: {final_score}/100, recomendación: {resumen}"""

            headers = {
                "Authorization": f"Bearer {st.secrets['openai_api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
                result = response.json()["choices"][0]["message"]["content"]
                st.write(result)
            except Exception as e:
                st.error(f"Error al llamar a OpenAI: {e}")
    else:
        st.warning("⚠️ No se encontraron datos históricos.")
