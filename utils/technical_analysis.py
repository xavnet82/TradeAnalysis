
import pandas as pd

def analizar_tecnico(df):
    score = 0
    justificaciones = []
    detalles = []
    tendencias = []

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
        return 0, ["❌ No hay suficientes datos técnicos."], df, [], []

    last = df.iloc[-1]

    close = float(last['Close'])
    sma20 = float(last['SMA20'])
    sma50 = float(last['SMA50'])
    macd = float(last['MACD'])
    rsi = float(last['RSI'])
    volume = float(last['Volume'])
    avg_volume = float(df['Volume'].rolling(10).mean().iloc[-1])

    # SMA20
    if close > sma20:
        score += 20
        justificaciones.append("✔️ Precio > SMA20")
        detalles.append("El precio actual está por encima de la media de 20 días, lo que sugiere una tendencia de corto plazo positiva.")
        tendencias.append("📈 Subiendo")
    else:
        justificaciones.append("❌ Precio < SMA20")
        detalles.append("El precio actual está por debajo de la media de 20 días, indicando debilidad reciente.")
        tendencias.append("📉 Bajando")

    # SMA50
    if close > sma50:
        score += 20
        justificaciones.append("✔️ Precio > SMA50")
        detalles.append("La cotización se mantiene por encima de la media de 50 días, consolidando fuerza a medio plazo.")
        tendencias.append("📈 Subiendo")
    else:
        justificaciones.append("❌ Precio < SMA50")
        detalles.append("La cotización se sitúa por debajo de su media de 50 días, lo que podría indicar corrección.")
        tendencias.append("📉 Bajando")

    # RSI
    if 40 <= rsi <= 60:
        score += 20
        justificaciones.append("✔️ RSI en zona neutra")
        detalles.append("El RSI está en equilibrio, sin señales claras de sobrecompra o sobreventa.")
        tendencias.append("➖ Neutro")
    elif rsi < 40:
        score += 10
        justificaciones.append("✔️ RSI en sobreventa")
        detalles.append("El RSI indica que el activo podría estar infravalorado, posible rebote técnico.")
        tendencias.append("📉 Bajando")
    else:
        justificaciones.append("❌ RSI en sobrecompra")
        detalles.append("El RSI señala sobrecompra, lo que podría derivar en corrección a corto plazo.")
        tendencias.append("📈 Subiendo")

    # MACD
    if macd > 0:
        score += 20
        justificaciones.append("✔️ MACD positivo")
        detalles.append("El MACD está por encima de cero, lo cual confirma momentum alcista.")
        tendencias.append("📈 Subiendo")
    else:
        justificaciones.append("❌ MACD negativo")
        detalles.append("El MACD está por debajo de cero, lo que indica presión bajista.")
        tendencias.append("📉 Bajando")

    # Volumen
    if volume > avg_volume:
        score += 20
        justificaciones.append("✔️ Volumen actual > promedio 10 días")
        detalles.append("El volumen reciente supera la media, indicando mayor interés del mercado.")
        tendencias.append("📈 Subiendo")
    else:
        justificaciones.append("❌ Volumen actual < promedio")
        detalles.append("El volumen reciente es bajo, lo que sugiere debilidad en la tendencia.")
        tendencias.append("📉 Bajando")

    return score, justificaciones, df, detalles, tendencias
