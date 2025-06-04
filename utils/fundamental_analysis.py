
import yfinance as yf

def analizar_fundamental(ticker):
    score = 0
    justificacion = []
    try:
        stock = yf.Ticker(ticker)
        per = stock.fast_info.get("pe_ratio")

        if per and 5 < per < 25:
            score += 25
            justificacion.append("✔️ PER en rango saludable (5–25)")
        else:
            justificacion.append("❌ PER extremo o no disponible")

        income_stmt = stock.income_stmt
        bs = stock.balance_sheet

        if "Net Income" in income_stmt.index and "Total Stockholder Equity" in bs.index:
            ni = income_stmt.loc["Net Income"].iloc[0]
            equity = bs.loc["Total Stockholder Equity"].iloc[0]
            if equity != 0:
                roe = ni / equity
                if roe > 0.15:
                    score += 25
                    justificacion.append("✔️ ROE alto (>15%)")
                else:
                    justificacion.append("❌ ROE bajo")
            else:
                justificacion.append("⚠️ Equity es cero")
        else:
            justificacion.append("⚠️ No hay datos para ROE")

        if "Net Income" in income_stmt.index and "Total Revenue" in income_stmt.index:
            ni = income_stmt.loc["Net Income"].iloc[0]
            tr = income_stmt.loc["Total Revenue"].iloc[0]
            if tr != 0:
                margin = ni / tr
                if margin > 0.15:
                    score += 20
                    justificacion.append("✔️ Margen >15%")
                else:
                    justificacion.append("❌ Margen bajo")
        else:
            justificacion.append("⚠️ No hay datos de ingresos totales")

        if "Total Debt" in bs.index and "Total Stockholder Equity" in bs.index:
            debt = bs.loc["Total Debt"].iloc[0]
            equity = bs.loc["Total Stockholder Equity"].iloc[0]
            if equity != 0:
                ratio = debt / equity
                if ratio < 1:
                    score += 20
                    justificacion.append("✔️ Deuda/patrimonio <1")
                else:
                    justificacion.append("❌ Deuda elevada")
        else:
            justificacion.append("⚠️ No hay datos de deuda/equity")

        dividend_yield = stock.fast_info.get("dividend_yield")
        if dividend_yield and dividend_yield > 0:
            score += 10
            justificacion.append("✔️ Ofrece dividendos")
        else:
            justificacion.append("❌ No ofrece dividendos")

    except Exception as e:
        return 50, [f"⚠️ Error en análisis fundamental: {e}"]

    return int(score), justificacion
