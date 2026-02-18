import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Banco de Questões Permanente", layout="wide")

st.title("🗄️ Banco de Questões via Google Sheets")

# Criar a conexão explicitando onde buscar o segredo
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Tentamos ler usando a configuração do Secrets
        return conn.read()
    except Exception as e:
        # Se der erro, tentamos passar o link diretamente para testar
        # Substitua pelo seu link real abaixo se o erro persistir
        url = st.secrets.get("public_gsheets_url") or st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet")
        if url:
            return conn.read(spreadsheet=url)
        else:
            st.error("Erro: Link da planilha não encontrado nos Secrets!")
            return pd.DataFrame()

df = load_data()
