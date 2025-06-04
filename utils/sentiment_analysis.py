import feedparser
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analizar_sentimiento_noticias(ticker):
    try:
        sid = SentimentIntensityAnalyzer()

        feed_url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            return 50, ["No se encontraron noticias recientes."]

        scores = []
        razones = []

        for entry in feed.entries[:5]:  # solo las 5 primeras
            titulo = entry.title
            score = sid.polarity_scores(titulo)["compound"]
            scaled = int((score + 1) * 50)  # convierte [-1,1] a [0,100]
            scores.append(score)
            razones.append(f"{titulo} (score: {scaled}/100)")

        media = sum(scores) / len(scores)
        final_score = int((media + 1) * 50)

        return final_score, razones

    except Exception as e:
        return 0, [f"Error al analizar sentimiento: {e}"]
