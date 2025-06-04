import requests
from bs4 import BeautifulSoup

def extraer_tabla_macrotrends(ticker, concepto):
    """
    Extrae la tabla financiera histórica para un concepto (revenue, net-income, etc.).
    """
    url = f"https://www.macrotrends.net/stocks/charts/{ticker}/xyz/{concepto}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Encuentra todas las tablas visibles
    tablas = soup.find_all("table", {"class": "historical_data_table table"})

    if not tablas:
        raise ValueError(f"No se encontró tabla para {concepto}")

    datos = []
    filas = tablas[0].find_all("tr")[1:]  # omitir header
    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) >= 2:
            try:
                año = celdas[0].text.strip()
                valor = celdas[1].text.strip().replace("$", "").replace(",", "")
                valor = float(valor)
                datos.append((año, valor))
            except:
                continue
    return datos

def analizar_fundamental(ticker):
    try:
        revenues = extraer_tabla_macrotrends(ticker.lower(), "revenue")
        net_income = extraer_tabla_macrotrends(ticker.lower(), "net-income")
        cogs = extraer_tabla_macrotrends(ticker.lower(), "cost-goods-sold")

        razones = []
        score = 0

        # Orden descendente: año más reciente primero
        if len(revenues) >= 2:
            growth = (revenues[0][1] - revenues[1][1]) / revenues[1][1]
            if growth > 0.1:
                score += 40
                razones.append(f"Crecimiento de ingresos año a año: {growth:.2%}")
            elif growth > 0:
                score += 20
                razones.append(f"Crecimiento moderado de ingresos: {growth:.2%}")
            else:
                score += 5
                razones.append(f"Caída de ingresos: {growth:.2%}")
        else:
            razones.append("Datos insuficientes para analizar ingresos.")

        if len(cogs) >= 2 and len(revenues) >= 2:
            margen_bruto = 1 - (cogs[0][1] / revenues[0][1])
            razones.append(f"Margen bruto último año: {margen_bruto:.2%}")
            if margen_bruto > 0.5:
                score += 30
            elif margen_bruto > 0.3:
                score += 15
            else:
                score += 5

        if len(net_income) >= 2:
            crecimiento_net = (net_income[0][1] - net_income[1][1]) / net_income[1][1]
            razones.append(f"Crecimiento en beneficio neto: {crecimiento_net:.2%}")
            if crecimiento_net > 0.1:
                score += 30
            elif crecimiento_net > 0:
                score += 15
            else:
                score += 0
        else:
            razones.append("Datos de beneficio neto insuficientes.")

        return score, razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental (macrotrends): {e}"]
