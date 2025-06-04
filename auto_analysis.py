import os
import datetime
import pandas as pd

from utils.data_fetcher import descargar_datos
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias

def clasificar_recomendacion(score):
    if score >= 75:
        return "Alta"
    elif score >= 50:
        return "Media"
    else:
        return "Baja"

def ejecutar_analisis_programado(ticker="AAPL"):
    fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
    df = descargar_datos(ticker)
    if df.empty:
        print(f"{fecha_actual} - No se pudieron obtener datos para {ticker}")
        return None

    cierre = df["Close"].iloc[-1]

    # Análisis técnico
    score_t, _, df, _, _ = analizar_tecnico(df)

    # Análisis fundamental (omitido si es índice)
    if ticker.startswith("^"):
        score_f = 50
    else:
        score_f, _ = analizar_fundamental(ticker)

    # Análisis de sentimiento
    score_s, _ = analizar_sentimiento_noticias(ticker)

    # Score global
    score_final = int((score_t + score_f + score_s) / 3)
    recomendacion = clasificar_recomendacion(score_final)

    registro = {
        "fecha_analisis": fecha_actual,
        "ticker": ticker,
        "cierre": round(cierre, 2),
        "score_tecnico": score_t,
        "score_fundamental": score_f,
        "score_sentimiento": score_s,
        "score_final": score_final,
        "recomendacion": recomendacion
    }

    output_file = f"historico_{ticker.replace('^', '')}.csv"
    if os.path.exists(output_file):
        df_historico = pd.read_csv(output_file)
        df_historico = pd.concat([df_historico, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_historico = pd.DataFrame([registro])

    df_historico.to_csv(output_file, index=False)
    print(f"✅ Análisis guardado en {output_file}")
    return registro
