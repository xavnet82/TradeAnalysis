import streamlit as st
import nltk
import os
import pandas as pd
from io import StringIO

from config import COLORS
from utils.data_fetcher import (
    descargar_datos,
    get_all_index_tickers,
    get_all_stock_tickers
)
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias
from utils.charts import generar_grafico_precio
from components.cards import render_score_card
from auto_analysis import ejecutar_analisis_programado

nltk.download("vader_lexicon")

st.set_page_config(layout="wide")
st.title("📊 Análisis Integral de Acciones")

st.sidebar.header("🔎 Selección de Activo")
tipo_activo = st.sidebar.selectbox("Tipo de activo", ["Índice", "Acción"])

if tipo_activo == "Índice":
    indices = get_all_index_tickers()
    ticker = st.sidebar.selectbox("Selecciona un índice", list(indices.keys()), format_func=lambda x: f"{x} - {indices[x]}")
elif tipo_activo == "Acción":
    acciones = get_all_stock_tickers()
    ticker = st.sidebar.selectbox("Selecciona una acción", list(acciones.keys()), format_func=lambda x: f"{x} - {acciones[x]}")

def resumen_final(score_t, score_f, score_s):
    media = int((score_t + score_f + score_s) / 3)
    if media >= 75:
        resumen = "📈 Alta recomendación de inversión."
    elif media >= 50:
        resumen = "⚖️ Recomendación moderada."
    else:
        resumen = "📉 Baja recomendación de inversión."
    return media, resumen

def color_por_score(score):
    if score >= 75:
        return "#9BE7A0"
    elif score >= 50:
        return "#FFEB99"
    else:
        return "#FFB3B3"

if ticker:
    df = descargar_datos(ticker)
    if not df.empty:
        es_indice = ticker.startswith("^")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📈 Resultados")

            score_t, razones_t, df, detalles_t, tendencias_t = analizar_tecnico(df)
            render_score_card("Análisis Técnico", score_t, razones_t, color_por_score(score_t))

            with st.expander("🔍 Ver detalle de indicadores técnicos"):
                for i in range(len(razones_t)):
                    cols = st.columns([1.5, 1.5, 4, 1.5])
                    with cols[0]:
                        st.markdown(f"**Indicador {i+1}**")
                    with cols[1]:
                        st.markdown(razones_t[i])
                    with cols[2]:
                        st.markdown(detalles_t[i])
                    with cols[3]:
                        st.markdown(tendencias_t[i])

            if not es_indice:
                score_f, razones_f = analizar_fundamental(ticker)
                render_score_card("Análisis Fundamental", score_f, razones_f, color_por_score(score_f))
                with st.expander("🔍 Ver detalle de indicadores fundamentales"):
                    for razon in razones_f:
                        st.markdown(f"- {razon}")
            else:
                score_f = 50
                razones_f = ["No se realiza análisis fundamental para índices."]

            score_s, razones_s = analizar_sentimiento_noticias(ticker)
            render_score_card("Sentimiento en Noticias", score_s, razones_s, color_por_score(score_s))

            st.markdown("---")
            st.subheader("✅ Recomendación Consolidada")
            final_score, resumen = resumen_final(score_t, score_f, score_s)
            st.metric("Score Global", f"{final_score}/100")
            st.info(resumen)

            st.markdown("---")
            st.subheader("📉 Gráfico del último año (con SMA)")
            fig = generar_grafico_precio(df, ticker)
            st.pyplot(fig)

            st.markdown("---")
            st.subheader("📅 Análisis Automático")

            if st.button("Ejecutar análisis y guardar histórico"):
                resultado = ejecutar_analisis_programado(ticker)
                if resultado:
                    st.success(f"Análisis ejecutado para {ticker} y guardado.")
                else:
                    st.warning(f"No se pudo ejecutar el análisis para {ticker}.")

            csv_file = f"historico_{ticker.replace('^', '')}.csv"
            if os.path.exists(csv_file):
                df_hist = pd.read_csv(csv_file)
                st.subheader(f"📚 Histórico de análisis para {ticker}")
                st.dataframe(df_hist.tail(10))

                with open(csv_file, "r", encoding="utf-8") as f:
                    csv_data = f.read()
                st.download_button(
                    label="⬇️ Descargar histórico CSV",
                    data=csv_data,
                    file_name=csv_file,
                    mime="text/csv"
                )

                if st.button("🗑️ Eliminar histórico del ticker"):
                    try:
                        os.remove(csv_file)
                        st.success(f"Histórico eliminado: {csv_file}")
                    except Exception as e:
                        st.error(f"No se pudo eliminar: {e}")

        with col2:
            st.subheader("🧠 Análisis Generado por IA")
            usar_ia = st.toggle("¿Generar análisis con IA?", value=True)
            if usar_ia:
                from openai import OpenAI

                prompt = f"""Analiza los siguientes indicadores para el activo {ticker}:
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
