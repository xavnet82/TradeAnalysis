import requests
from bs4 import BeautifulSoup
import time

def obtener_metricas_finviz(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    time.sleep(1)  # para evitar bloqueo

    tabla = soup.find("table", class_="snapshot-table2")
    celdas = tabla.find_all("td")
    data = {}
    for i in range(0, len(celdas), 2):
        key = celdas[i].text.strip()
        value = celdas[i+1].text.strip()
        data[key] = value
    return data

def analizar_fundamental(ticker):
    try:
        datos = obtener_metricas_finviz(ticker)
        score = 0
        razones = []

        rev_growth = datos.get("Sales growth", None)
        if rev_growth:
            porcentaje = float(rev_growth.strip("%"))
            if porcentaje > 10:
                score += 40
                razones.append(f"Crecimiento de ventas: {porcentaje:.2f}%")
            elif porcentaje > 0:
                score += 20
                razones.append(f"Crecimiento moderado de ventas: {porcentaje:.2f}%")
            else:
                score += 5
                razones.append(f"Caída en ventas: {porcentaje:.2f}%")
        else:
            razones.append("No disponible crecimiento de ventas")

        margen = datos.get("Gross Margin", None)
        if margen:
            m = float(margen.strip("%"))
            if m > 50:
                score += 30
                razones.append(f"Margen bruto elevado: {m:.2f}%")
            elif m > 30:
                score += 20
                razones.append(f"Margen bruto moderado: {m:.2f}%")
            else:
                score += 10
                razones.append(f"Margen bruto bajo: {m:.2f}%")
        else:
            razones.append("Margen bruto no disponible")

        eps_growth = datos.get("EPS growth this year", None)
        if eps_growth:
            g = float(eps_growth.strip("%"))
            if g > 10:
                score += 30
                razones.append(f"Crecimiento EPS positivo: {g:.2f}%")
            else:
                score += 10
                razones.append(f"Crecimiento EPS moderado: {g:.2f}%")
        else:
            razones.append("Crecimiento EPS no disponible")

        return score, razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental (finviz): {e}"]
