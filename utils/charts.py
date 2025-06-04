
import matplotlib.pyplot as plt

def generar_grafico_precio(df, ticker):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df['Close'], label='Precio', linewidth=1.5)
    ax.plot(df.index, df['SMA20'], label='SMA20', linestyle='--')
    ax.plot(df.index, df['SMA50'], label='SMA50', linestyle='--')
    ax.set_title(f'{ticker} - Precio y Medias Móviles')
    ax.legend()
    return fig
