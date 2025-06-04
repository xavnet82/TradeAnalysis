
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analizar_sentimiento_noticias(ticker):
    url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&token=YOUR_GNEWS_API_KEY"
    try:
        resp = requests.get(url, timeout=10)
        noticias = resp.json().get("articles", [])
        if not noticias:
            return 50, ["❌ No se encontraron noticias."]

        sia = SentimentIntensityAnalyzer()
        pos, neg, neu = 0, 0, 0
        for n in noticias:
            score = sia.polarity_scores(n['title'])["compound"]
            if score > 0.05:
                pos += 1
            elif score < -0.05:
                neg += 1
            else:
                neu += 1

        total = pos + neg + neu
        if total == 0:
            return 50, ["❌ No se puede evaluar sentimiento."]
        pct_pos = pos / total * 100
        if pct_pos > 60:
            return 85, ["✔️ Sentimiento positivo predominante"]
        elif pct_pos < 40:
            return 30, ["❌ Sentimiento negativo dominante"]
        else:
            return 55, ["⚖️ Sentimiento mixto"]

    except Exception as e:
        return 50, [f"❌ Error en análisis de noticias: {e}"]
