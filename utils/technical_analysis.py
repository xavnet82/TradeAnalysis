
import pandas as pd

def analizar_tecnico(df):
    score = 0
    justificacion = []

    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    indicadores = ['SMA20', 'SMA50', 'MACD', 'RSI']
    if df[indicadores].isnull().iloc[-1].any():
        return 0, ["❌ No hay suficientes datos técnicos."], df

    last = df.iloc[-1]

    close = float(last['Close'])
    sma20 = float(last['SMA20'])
    sma50 = float(last['SMA50'])
    macd = float(last['MACD'])
    rsi = float(last['RSI'])
    volume = float(last['Volume'])
    avg_volume = float(df['Volume'].rolling(10).mean().iloc[-1])

    if close > sma20:
        score += 20
        justificacion.append("✔️ Precio > SMA20")
    else:
        justificacion.append("❌ Precio < SMA20")

    if close > sma50:
        score += 20
        justificacion.append("✔️ Precio > SMA50")
    else:
        justificacion.append("❌ Precio < SMA50")

    if 40 <= rsi <= 60:
        score += 20
        justificacion.append("✔️ RSI en zona neutra")
    elif rsi < 40:
        score += 10
        justificacion.append("✔️ RSI en sobreventa")
    else:
        justificacion.append("❌ RSI en sobrecompra")

    if macd > 0:
        score += 20
        justificacion.append("✔️ MACD positivo")
    else:
        justificacion.append("❌ MACD negativo")

    if volume > avg_volume:
        score += 20
        justificacion.append("✔️ Volumen actual > promedio 10 días")
    else:
        justificacion.append("❌ Volumen actual < promedio")

    return score, justificacion, df
