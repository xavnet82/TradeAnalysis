import yfinance as yf

def analizar_fundamental(ticker):
    score = 0
    justificacion = []

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # PER
        per = info.get("trailingPE")
        if per and 5 < per < 25:
            score += 25
            justificacion.append("✔️ PER en rango saludable (5–25)")
        else:
            justificacion.append("❌ PER extremo o no disponible")

        # ROE
        roe = info.get("returnOnEquity")
        if roe is not None:
            if roe > 0.15:
                score += 25
                justificacion.append("✔️ ROE alto (>15%)")
            else:
                justificacion.append("❌ ROE bajo")
        else:
            justificacion.append("⚠️ ROE no disponible")

        # Margen de beneficio
        margin = info.get("profitMargins")
        if margin is not None:
            if margin > 0.15:
                score += 20
                justificacion.append("✔️ Margen de beneficio >15%")
            else:
                justificacion.append("❌ Margen bajo")
        else:
            justificacion.append("⚠️ Margen no disponible")

        # Deuda sobre equity
        de_ratio = info.get("debtToEquity")
        if de_ratio is not None:
            if de_ratio < 100:
                score += 20
                justificacion.append("✔️ Deuda/Equity < 100%")
            else:
                justificacion.append("❌ Nivel de deuda elevado")
        else:
            justificacion.append("⚠️ Ratio de deuda no disponible")

        # Dividendos
        dividend_yield = info.get("dividendYield")
        if dividend_yield is not None and dividend_yield > 0:
            score += 10
            justificacion.append("✔️ Ofrece dividendos")
        else:
            justificacion.append("❌ No ofrece dividendos")

    except Exception as e:
        return 50, [f"⚠️ Error en análisis fundamental: {e}"]

    return int(score), justificacion
