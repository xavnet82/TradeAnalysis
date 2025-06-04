import os
import datetime
import pandas as pd

from utils.data_fetcher import descargar_datos
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias

# === Configuración ===
TICKER = "AAPL"  # Cambia aquí el ticker deseado (índice o acción)
OUTPUT_FILE = "historico_analisis.csv"
FECHA = datetime.date.today().strftime("%Y-%m-%d")

def clasificar_recomendacion(score):
    if score >= 75:
        return "Alta"
    elif score >= 50:
        return "Media"
    else:
        return "Baja"

def ejecutar_analisis():
    df = descargar_datos(TICKER)
    if df.empty:
        print(f"{FECHA} - No se pudieron obtener datos para {TICKER}")
        return

    cierre = df["Close"].iloc[-1]

    # Análisis técnico
    score_t, _, df, _, _ = analizar_tecnico(df)

    # Análisis fundamental (omitido si es índice)
    if TICKER.startswith("^"):
        score_f = 50
    else:
        score_f, _ = analizar_fundamental(TICKER)

    # Análisis de sentimiento
    score_s, _ = analizar_sentimiento_noticias(TICKER)

    # Score global
    score_final = int((score_t + score_f + score_s) / 3)
    recomendacion = clasificar_recomendacion(score_final)

    registro = {
        "fecha_analisis": FECHA,
        "ticker": TICKER,
        "cierre": round(cierre, 2),
        "score_tecnico": score_t,
        "score_fundamental": score_f,
        "score_sentimiento": score_s,
        "score_final": score_final,
        "recomendacion": recomendacion
    }

    if os.path.exists(OUTPUT_FILE):
        df_historico = pd.read_csv(OUTPUT_FILE)
        df_historico = pd.concat([df_historico, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_historico = pd.DataFrame([registro])

    df_historico.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Análisis guardado: {TICKER} ({FECHA})")

if __name__ == "__main__":
    ejecutar_analisis()
