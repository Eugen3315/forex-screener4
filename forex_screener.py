import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🧭 Скринер Forex и Металлов")

# Символы: валюты и металлы (Yahoo Finance формат)
symbols = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "XAU/USD (Gold)": "XAUUSD=X",
    "XAG/USD (Silver)": "XAGUSD=X"
}

# Пользовательский выбор символов
selected = st.multiselect("Выбери активы для анализа:", list(symbols.keys()), default=list(symbols.keys())[:3])
selected_symbols = [symbols[s] for s in selected]

# Загрузка данных
@st.cache_data
def load_data(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['sma200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
    df['sma50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
    return df.dropna()

# Анализ и отображение сигналов
st.subheader("📊 Результаты анализа")

for name, symbol in symbols.items():
    if symbol not in selected_symbols:
        continue

    df = load_data(symbol)
    last = df.iloc[-1]
    signal = ""

    if last['rsi'] < 30 and last['Close'] > last['sma200']:
        signal = "🟢 Возможная покупка (RSI < 30 и выше SMA200)"
    elif last['rsi'] > 70 and last['Close'] < last['sma200']:
        signal = "🔴 Возможная продажа (RSI > 70 и ниже SMA200)"

    with st.expander(f"{name} - Цена: {round(last['Close'], 4)} - {signal if signal else 'Нет сигнала'}"):
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='Цены'))

        fig.add_trace(go.Scatter(
            x=df.index, y=df['sma200'], line=dict(color='blue', width=1), name='SMA 200'))

        fig.add_trace(go.Scatter(
            x=df.index, y=df['sma50'], line=dict(color='orange', width=1), name='SMA 50'))

        fig.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

        st.write("🔍 RSI:", round(last['rsi'], 2))
