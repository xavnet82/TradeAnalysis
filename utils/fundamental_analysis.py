import requests
from bs4 import BeautifulSoup

def obtener_per_yahoo(ticker):
    """
    Extrae el PER desde la página principal de Yahoo Finance (quote summary).
    """
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    per = None
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) == 2 and "PE Ratio (TTM)" in cols[0].text:
            try:
                per = float(cols[1].text.replace(",", ""))
            except ValueError:
                per = None
            break

    return per

def analizar_fundamental(ticker):
    """
    Realiza un análisis fundamental simple basado en PER.
    Devuelve un score y explicaciones sin depender de APIs.
    """
    try:
        per = obtener_per_yahoo(ticker)
        score = 0
        razones = []

        if per is not None:
            if per < 15:
                score += 70
                razones.append(f"PER atractivo: {per:.2f}")
            elif per < 25:
                score += 50
                razones.append(f"PER razonable: {per:.2f}")
            else:
                score += 20
                razones.append(f"PER elevado: {per:.2f}")
        else:
            razones.append("PER no disponible")

        razones.append("Análisis basado únicamente en PER por restricciones sin API.")
        return score, razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental (scraping): {e}"]
