import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import time
import uuid
from datetime import datetime

TOTAL_BITCOINS = 21_000_000  # Máximo de Bitcoins que podem existir

def get_bitcoin_data():
    url = "https://api.blockchair.com/bitcoin/stats"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("data", {})
        return {
            "blocks": data.get("blocks", 0),
            "transactions": data.get("transactions", 0),
            "transactions_24h": data.get("transactions_24h", 0),
            "average_transaction_fee_24h": data.get("average_transaction_fee_24h", 0),
            "nodes": data.get("nodes", 0),
            "market_price_usd": data.get("market_price_usd", 0),
            "circulating_supply": data.get("circulating_supply", 0) / 100_000_000  # Convertendo satoshis para BTC
        }
    else:
        st.error(f"Erro ao buscar dados da API. Status code: {response.status_code}")
        return None

def get_brazilian_real_rate():
    try:
        url = "https://economia.awesomeapi.com.br/last/USD-BRL"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data["USDBRL"]["bid"])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter taxa de câmbio: {e}")
        return None

def get_historical_price():
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = [item[1] for item in data["prices"]]
        timestamps = [item[0] / 1000 for item in data["prices"]]
        df = pd.DataFrame({"Timestamp": timestamps, "Price": prices})
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter preço histórico: {e}")
        return None

def get_bitcoin_news():
    try:
        url = f"https://newsapi.org/v2/everything?q=bitcoin&apiKey=b883b98d22b24538ad2c7d86fe62648c"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["articles"][:3]
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter notícias: {e}")
        return None


def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([10, 1])  
    with col1:
        st.title("📊 Dashboard de Dados do Bitcoin")
    

    price_placeholder = st.empty()
    chart_placeholder = st.empty()
    network_placeholder = st.empty()
    news_placeholder = st.empty()



    while True:
        data = get_bitcoin_data()
        brl_rate = get_brazilian_real_rate()

        if brl_rate and data:
            with price_placeholder.container():
                st.markdown(
                    f"""
                    <h1 style='text-align: center; color: white;'>
                        💰 Preço do Bitcoin: USD ${data['market_price_usd']:,.2f} / BRL R${(data['market_price_usd'] * brl_rate):,.2f}
                    </h1>
                    """,
                    unsafe_allow_html=True
                )

            historical_price = get_historical_price()
            if historical_price is not None:
                fig = px.line(historical_price, x="Timestamp", y="Price", title="📈 Preço Histórico do Bitcoin (30 dias)")
                chart_placeholder.plotly_chart(fig, use_container_width=True, key=str(uuid.uuid4()))

            with network_placeholder.container():
                st.markdown("## 🌐 Informações da Rede")
                col1, col2, col3 = st.columns(3)
                col1.metric("⛏️ Blocos Minerados", f"{data['blocks']:,}")
                col2.metric("🔄 Transações Totais", f"{data['transactions']:,}")
                col3.metric("⚡ Transações nas Últimas 24h", f"{data['transactions_24h']:,}")

                col4, col5, col6 = st.columns(3)
                col4.metric("💰 Taxa Média (sat/byte)", f"{data['average_transaction_fee_24h']:.2f}")
                col5.metric("🖥️ Nós na Rede", f"{data['nodes']:,}")
                col6.metric("💲 Preço do BTC", f"USD ${data['market_price_usd']:,.2f} / BRL R${(data['market_price_usd'] * brl_rate):,.2f}")

            with news_placeholder.container():
                st.markdown("## 📰 Últimas Notícias sobre Bitcoin")
                news_articles = get_bitcoin_news()
                if news_articles:
                    cols = st.columns(len(news_articles))
                    for i, article in enumerate(news_articles):
                        with cols[i]:
                            st.markdown(
                                f"""
                                <div style='border: 1px solid #e0e0e0; padding: 10px; border-radius: 10px;'>
                                    <strong>{article['title']}</strong><br>
                                    {article['description']}<br>
                                    <a href='{article['url']}' target='_blank'>Leia mais</a>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

        time.sleep(30)

if __name__ == "__main__":
    main()
