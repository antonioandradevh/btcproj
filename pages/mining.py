import streamlit as st
import requests

TOTAL_BITCOINS = 21_000_000

def get_bitcoin_data():
    url = "https://api.blockchair.com/bitcoin/stats"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("data", {})
        circulating_supply = data.get("circulation", 0) / 100_000_000
        remaining_supply = TOTAL_BITCOINS - circulating_supply
        return circulating_supply, remaining_supply
    st.error(f"Erro na API Bitcoin: {response.status_code}")
    return None, None

def get_minerstat_data():
    url = "https://api.minerstat.com/v2/coins?list=BTC"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    st.error("Erro na API Minerstat")
    return None

def get_minerstat_hardware():
    url = "https://api.minerstat.com/v2/hardware?type=asic"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    st.error("Erro ao buscar ASICs")
    return None

def main():
    st.set_page_config(layout="wide")
    st.title("⛏️ Mineração de Bitcoin")

    circulating_supply, remaining_supply = get_bitcoin_data()
    if circulating_supply:
        col1, col2 = st.columns(2)
        col1.metric("Minerados", f"{circulating_supply:,.0f} BTC")
        col2.metric("Restantes", f"{remaining_supply:,.0f} BTC")

    st.markdown("## ⚡ Dados")
    mining_data = get_minerstat_data()
    if mining_data:
        col3, col4, col5 = st.columns(3)
        col3.metric("Recompensa", f"{mining_data['reward']} BTC")
        col4.metric("Dificuldade", f"{mining_data['difficulty']:,}")
        col5.metric("Hashrate", f"{mining_data['network_hashrate']} H/s")

    st.markdown("## ️ Especificações dos ASICs")
    hardware_data = get_minerstat_hardware()
    if hardware_data:
        cols = st.columns(3)
        for i, hw in enumerate(hardware_data[:6]):
            with cols[i % 3]:
                with st.expander(hw.get('name', 'ASIC Desconhecido')):
                    specs = hw.get('specs', {})
                    st.write(f"**Fabricante:** {hw.get('brand', 'N/A')}")
                    st.write(f"**Potência:** {hw.get('algorithms', {}).get('SHA-256', {}).get('power', 'N/A')}W")
                    st.write(f"**Peso:** {specs.get('Weight', 'N/A')}")
                    st.write(f"**Ruído:** {specs.get('Noise level', 'N/A')}")
                    st.write(f"**Chip:** {specs.get('Chip type', 'N/A')}")

if __name__ == "__main__":
    main()