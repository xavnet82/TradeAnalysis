import matplotlib.pyplot as plt


def generar_grafico_precio(df, ticker):
    fig, axs = plt.subplots(3, 1, figsize=(10, 4.2), sharex=True, gridspec_kw={'height_ratios': [4, 1, 1]})
    fig.subplots_adjust(hspace=0.15)

    # Calcular líneas necesarias si no existen
    if 'SMA20' not in df.columns:
        df['SMA20'] = df['Close'].rolling(20).mean()
    if 'SMA50' not in df.columns:
        df['SMA50'] = df['Close'].rolling(50).mean()
    if 'EMA12' not in df.columns:
        df['EMA12'] = df['Close'].ewm(span=12).mean()
    if 'EMA26' not in df.columns:
        df['EMA26'] = df['Close'].ewm(span=26).mean()
    if 'MACD' not in df.columns:
        df['MACD'] = df['EMA12'] - df['EMA26']
    if 'Signal' not in df.columns:
        df['Signal'] = df['MACD'].ewm(span=9).mean()
    if 'RSI' not in df.columns:
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

    # Subplot 1: Precio + SMA
    axs[0].plot(df.index, df['Close'], label='Precio Cierre', color='black')
    axs[0].plot(df.index, df['SMA20'], label='SMA20', linestyle='--')
    axs[0].plot(df.index, df['SMA50'], label='SMA50', linestyle=':')
    axs[0].set_ylabel("Precio")
    axs[0].legend(loc='upper left')
    axs[0].set_title(f"{ticker} - Precio y Medias Móviles")

    # Subplot 2: MACD
    axs[1].plot(df.index, df['MACD'], label='MACD', color='blue')
    axs[1].plot(df.index, df['Signal'], label='Señal', color='red')
    axs[1].axhline(0, color='gray', linestyle='--')
    axs[1].set_ylabel("MACD")
    axs[1].legend(loc='upper left')

    # Subplot 3: RSI
    axs[2].plot(df.index, df['RSI'], label='RSI', color='green')
    axs[2].axhline(70, linestyle='--', color='red', alpha=0.5)
    axs[2].axhline(30, linestyle='--', color='blue', alpha=0.5)
    axs[2].set_ylabel("RSI")
    axs[2].set_ylim(0, 100)
    axs[2].legend(loc='upper left')

    return fig
