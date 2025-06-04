import pandas as pd

def analizar_tecnico(df):
    score = 0
    justificaciones, detalles, tendencias = [], [], []

    # Indicadores básicos
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['UpperBB'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()
    df['LowerBB'] = df['Close'].rolling(20).mean() - 2 * df['Close'].rolling(20).std()
    df['MiddleBB'] = df['Close'].rolling(20).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # ADX
    df['TR'] = df[['High', 'Low', 'Close']].diff().abs().max(axis=1)
    df['+DM'] = df['High'].diff()
    df['-DM'] = -df['Low'].diff()
    df['+DM'] = df['+DM'].where((df['+DM'] > df['-DM']) & (df['+DM'] > 0), 0.0)
    df['-DM'] = df['-DM'].where((df['-DM'] > df['+DM']) & (df['-DM'] > 0), 0.0)
    tr14 = df['TR'].rolling(14).mean()
    plus_di = 100 * df['+DM'].rolling(14).mean() / tr14
    minus_di = 100 * df['-DM'].rolling(14).mean() / tr14
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['ADX'] = dx.rolling(14).mean()

    # Stochastic RSI
    rsi_min = df['RSI'].rolling(14).min()
    rsi_max = df['RSI'].rolling(14).max()
    df['StochRSI'] = (df['RSI'] - rsi_min) / (rsi_max - rsi_min)

    if df[['SMA20','SMA50','MACD','Signal','RSI','ADX','UpperBB']].isnull().iloc[-1].any():
        return 0, ["❌ No hay suficientes datos técnicos."], df, [], []

    last = df.iloc[-1]
    close = float(last['Close'])
    sma20 = float(last['SMA20'])
    sma50 = float(last['SMA50'])
    macd = float(last['MACD'])
    signal = float(last['Signal'])
    rsi = float(last['RSI'])
    adx = float(last['ADX'])
    stoch_rsi = float(last['StochRSI'])
    upper_bb = float(last['UpperBB'])
    lower_bb = float(last['LowerBB'])
    volume = float(last['Volume'])
    avg_volume = float(df['Volume'].rolling(10).mean().iloc[-1])

    # Nuevo resumen de recomendación
    positivos = sum(1 for r in justificaciones if r.startswith("✔️"))
    if score >= 75 and positivos >= 4:
        recomendacion = "📈 Alta señal de compra técnica"
    elif score >= 50 and positivos >= 3:
        recomendacion = "⚖️ Señales mixtas, considerar mantener"
    else:
        recomendacion = "📉 Señales débiles, mejor evitar entrada"
    
    return score, justificaciones, df, detalles, tendencias, recomendacion


    def add_result(cond, pts, justif, detail, trend):
        nonlocal score
        if cond:
            score += pts
            justificaciones.append("✔️ " + justif)
            detalles.append(detail)
            tendencias.append(trend)
        else:
            justificaciones.append("❌ " + justif)
            detalles.append("Condición contraria detectada: " + detail)
            tendencias.append("📉" if "subiendo" in trend.lower() else "📈")

    # Precio vs SMA
    add_result(close > sma20, 10, "Precio > SMA20", "Tendencia positiva corto plazo.", "📈 Subiendo")
    add_result(close > sma50, 10, "Precio > SMA50", "Tendencia positiva medio plazo.", "📈 Subiendo")

    # RSI
    add_result(40 <= rsi <= 60, 10, "RSI neutro", "Sin sobrecompra ni sobreventa.", "➖ Neutro")
    add_result(rsi < 40, 5, "RSI en sobreventa", "Podría haber rebote.", "📉 Bajando")

    # MACD vs Signal
    add_result(macd > signal, 10, "MACD > Señal", "Momentum positivo confirmado.", "📈 Subiendo")

    # Bandas de Bollinger
    add_result(close < lower_bb, 5, "Precio < Banda inferior", "Posible sobreventa.", "📉 Bajando")
    add_result(close > upper_bb, -5, "Precio > Banda superior", "Posible sobrecompra.", "📈 Subiendo")

    # ADX
    add_result(adx > 25, 10, "ADX > 25", "Tendencia fuerte presente.", "📈 Fuerte")

    # Stochastic RSI
    add_result(stoch_rsi < 0.2, 5, "StochRSI en sobreventa", "Posible rebote cercano.", "📉 Bajando")

    # Volumen
    add_result(volume > avg_volume, 10, "Volumen creciente", "Interés creciente del mercado.", "📈 Subiendo")

    score = min(100, score)  # límite superior
    return score, justificaciones, df, detalles, tendencias
