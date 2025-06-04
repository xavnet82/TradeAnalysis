
import streamlit as st
from config import COLORS
from utils.data_fetcher import descargar_datos
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias
from utils.charts import generar_grafico_precio
from components.cards import render_score_card

import nltk
nltk.download("vader_lexicon")

st.set_page_config(layout="wide")
st.title("📊 Análisis Integral de Acciones")

ticker = st.text_input("Introduce un ticker (ej: AAPL, MSFT, ACN)", "AAPL").upper()

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
    else:
        st.warning("⚠️ No se encontraron datos históricos.")
