import requests
from bs4 import BeautifulSoup
import time

def obtener_metricas_finviz(ticker):
    """
    Extrae todas las métricas financieras del resumen de Finviz para un ticker dado.
    """
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    time.sleep(1)  # Respetar el rate limit

    soup = BeautifulSoup(r.text, "html.parser")
    tabla = soup.find("table", class_="snapshot-table2")
    celdas = tabla.find_all("td")
    data = {}
    for i in range(0, len(celdas), 2):
        key = celdas[i].text.strip()
        value = celdas[i + 1].text.strip()
        data[key] = value
    return data

def convertir_porcentaje(valor_str):
    try:
        return float(valor_str.replace('%', '').replace(',', '').strip())
    except:
        return None

def analizar_fundamental(ticker):
    """
    Evalúa múltiples KPIs fundamentales extraídos de Finviz.
    Calcula un score entre 0 y 100 y genera justificaciones detalladas.
    """
    try:
        datos = obtener_metricas_finviz(ticker)
        score = 0
        razones = []

        # 1. Crecimiento de ventas
        growth = convertir_porcentaje(datos.get("Sales growth", ""))
        if growth is not None:
            if growth > 10:
                score += 15
                razones.append(f"Sales growth sólido: {growth:.2f}%")
            elif growth > 0:
                score += 10
                razones.append(f"Sales growth moderado: {growth:.2f}%")
            else:
                score += 2
                razones.append(f"Sales growth negativo: {growth:.2f}%")

        # 2. Gross Margin
        gross_margin = convertir_porcentaje(datos.get("Gross Margin", ""))
        if gross_margin is not None:
            if gross_margin > 50:
                score += 10
                razones.append(f"Margen bruto excelente: {gross_margin:.2f}%")
            elif gross_margin > 30:
                score += 7
                razones.append(f"Margen bruto sólido: {gross_margin:.2f}%")
            else:
                score += 3
                razones.append(f"Margen bruto bajo: {gross_margin:.2f}%")

        # 3. Operating Margin
        operating_margin = convertir_porcentaje(datos.get("Operating Margin", ""))
        if operating_margin is not None:
            if operating_margin > 20:
                score += 10
                razones.append(f"Margen operativo excelente: {operating_margin:.2f}%")
            elif operating_margin > 10:
                score += 7
                razones.append(f"Margen operativo aceptable: {operating_margin:.2f}%")
            else:
                score += 3
                razones.append(f"Margen operativo bajo: {operating_margin:.2f}%")

        # 4. ROA
        roa = convertir_porcentaje(datos.get("ROA", ""))
        if roa is not None:
            if roa > 10:
                score += 5
                razones.append(f"ROA alto: {roa:.2f}%")
            elif roa > 5:
                score += 3
                razones.append(f"ROA razonable: {roa:.2f}%")
            else:
                score += 1
                razones.append(f"ROA bajo: {roa:.2f}%")

        # 5. ROE
        roe = convertir_porcentaje(datos.get("ROE", ""))
        if roe is not None:
            if roe > 15:
                score += 5
                razones.append(f"ROE elevado: {roe:.2f}%")
            elif roe > 5:
                score += 3
                razones.append(f"ROE razonable: {roe:.2f}%")
            else:
                score += 1
                razones.append(f"ROE bajo: {roe:.2f}%")

        # 6. ROI
        roi = convertir_porcentaje(datos.get("ROI", ""))
        if roi is not None:
            if roi > 15:
                score += 5
                razones.append(f"ROI excelente: {roi:.2f}%")
            elif roi > 5:
                score += 3
                razones.append(f"ROI razonable: {roi:.2f}%")
            else:
                score += 1
                razones.append(f"ROI bajo: {roi:.2f}%")

        # 7. EPS growth
        eps_growth = convertir_porcentaje(datos.get("EPS growth this year", ""))
        if eps_growth is not None:
            if eps_growth > 10:
                score += 10
                razones.append(f"EPS creciendo bien: {eps_growth:.2f}%")
            elif eps_growth > 0:
                score += 5
                razones.append(f"EPS ligeramente creciente: {eps_growth:.2f}%")
            else:
                score += 2
                razones.append(f"EPS decreciente: {eps_growth:.2f}%")

        # 8. Debt/Equity
        debt_eq = datos.get("Debt/Eq", "")
        try:
            d_eq = float(debt_eq)
            if d_eq < 0.5:
                score += 10
                razones.append(f"Baja deuda (Debt/Equity: {d_eq:.2f})")
            elif d_eq < 1.0:
                score += 5
                razones.append(f"Deuda moderada (Debt/Equity: {d_eq:.2f})")
            else:
                score += 2
                razones.append(f"Alta deuda (Debt/Equity: {d_eq:.2f})")
        except:
            razones.append("No disponible ratio Debt/Equity")

        # 9. Current Ratio
        current_ratio = datos.get("Current Ratio", "")
        try:
            cr = float(current_ratio)
            if cr > 2:
                score += 5
                razones.append(f"Buena liquidez (Current Ratio: {cr:.2f})")
            elif cr > 1:
                score += 3
                razones.append(f"Liquidez aceptable (Current Ratio: {cr:.2f})")
            else:
                score += 1
                razones.append(f"Liquidez baja (Current Ratio: {cr:.2f})")
        except:
            razones.append("No disponible Current Ratio")

        return min(score, 100), razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental (Finviz): {e}"]
