import os
import datetime
import pandas as pd

from utils.data_fetcher import descargar_datos
from utils.technical_analysis import analizar_tecnico
from utils.fundamental_analysis import analizar_fundamental
from utils.sentiment_analysis import analizar_sentimiento_noticias

# Configuración
TICKER = "AAPL"  # Cambiar por cualquier índice o acción
OUTPUT_FILE = "historico_analisis.csv"
HOY = datetime.date.today().strftime("%Y-%m-%d")

def color_por_score(score):
    if score >= 75:
        return "Alta"
    elif score >= 50:
        return "Media"
    else:
        return "Baja"

def ejecutar_analisis():
    df = descargar_datos(TICKER)
    if df.empty:
        print(f"{HOY} - No se pudo descargar datos de {TICKER}")
        return

    cierre = df["Close"].iloc[-1]

    # Análisis técnico
    score_t, _, df, _, _ = analizar_tecnico(df)

    # Análisis fundamental
    if TICKER.startswith("^"):
        score_f = 50
    else:
        score_f, _ = analizar_fundamental(TICKER)

    # Sentimiento
    score_s, _ = analizar_sentimiento_noticias(TICKER)

    # Score final
    final_score = int((score_t + score_f + score_s) / 3)
    recomendacion = color_por_score(final_score)

    # Registro
    datos = {
        "fecha": HOY,
        "ticker": TICKER,
        "cierre": round(cierre, 2),
        "score_tec": score_t,
        "score_fund": score_f,
        "score_sent": score_s,
        "score_final": final_score,
        "recomendacion": recomendacion,
    }

    if os.path.exists(OUTPUT_FILE):
        df_out = pd.read_csv(OUTPUT_FILE)
        df_out = pd.concat([df_out, pd.DataFrame([datos])], ignore_index=True)
    else:
        df_out = pd.DataFrame([datos])

    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"{HOY} - Análisis guardado para {TICKER}")

if __name__ == "__main__":
    ejecutar_analisis()
