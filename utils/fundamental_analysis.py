import requests

def get_yf_info(ticker):
    """
    Llama al endpoint interno de Yahoo Finance para obtener datos clave.
    """
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics,financialData"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def analizar_fundamental(ticker):
    """
    Realiza un análisis fundamental sencillo basado en indicadores clave:
    PER, ROE, Deuda/Patrimonio y Margen de beneficios.
    Devuelve un score sobre 100 y una lista de razones justificativas.
    """
    try:
        data = get_yf_info(ticker)

        stats = data["quoteSummary"]["result"][0]

        per = stats["defaultKeyStatistics"].get("trailingPE", {}).get("raw")
        roe = stats["financialData"].get("returnOnEquity", {}).get("raw")
        deuda_patrimonio = stats["financialData"].get("debtToEquity", {}).get("raw")
        margen = stats["financialData"].get("profitMargins", {}).get("raw")

        score = 0
        razones = []

        # PER
        if per is not None:
            if per < 15:
                score += 25
                razones.append(f"PER atractivo: {per:.2f}")
            elif per < 25:
                score += 15
                razones.append(f"PER razonable: {per:.2f}")
            else:
                razones.append(f"PER elevado: {per:.2f}")
        else:
            razones.append("PER no disponible")

        # ROE
        if roe is not None:
            if roe > 0.15:
                score += 25
                razones.append(f"ROE elevado: {roe:.2%}")
            elif roe > 0.05:
                score += 15
                razones.append(f"ROE aceptable: {roe:.2%}")
            else:
                razones.append(f"ROE bajo: {roe:.2%}")
        else:
            razones.append("ROE no disponible")

        # Deuda/Patrimonio
        if deuda_patrimonio is not None:
            if deuda_patrimonio < 100:
                score += 25
                razones.append(f"Buena gestión de deuda (D/E): {deuda_patrimonio:.2f}")
            elif deuda_patrimonio < 200:
                score += 15
                razones.append(f"Nivel de deuda razonable (D/E): {deuda_patrimonio:.2f}")
            else:
                razones.append(f"Deuda elevada (D/E): {deuda_patrimonio:.2f}")
        else:
            razones.append("Relación deuda/patrimonio no disponible")

        # Margen de beneficios
        if margen is not None:
            if margen > 0.15:
                score += 25
                razones.append(f"Margen alto: {margen:.2%}")
            elif margen > 0.05:
                score += 15
                razones.append(f"Margen aceptable: {margen:.2%}")
            else:
                razones.append(f"Margen bajo: {margen:.2%}")
        else:
            razones.append("Margen de beneficios no disponible")

        return score, razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental: {e}"]
