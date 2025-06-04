import yfinance as yf

def analizar_fundamental(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        per = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        deuda_patrimonio = info.get("debtToEquity", None)
        margen = info.get("profitMargins", None)

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

        # Margen
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
            razones.append("Margen no disponible")

        return score, razones

    except Exception as e:
        return 0, [f"Error en análisis fundamental: {e}"]
