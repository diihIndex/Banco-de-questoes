import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurações iniciais
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide")

st.title("📚 Banco de Questões Permanente (Google Sheets)")

# Conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl=0)

# Carrega os dados
df = load_data()

# CRIAÇÃO DAS ABAS (Menu centralizado e sempre visível)
aba1, aba2 = st.tabs(["🔍 Visualizar Banco", "📝 Cadastrar Nova Questão"])

with aba1:
    st.header("Questões na Nuvem")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("A planilha está vazia ou não foi encontrada.")

with aba2:
    st.header("Inserir Novo Item")
    with st.form("novo_item"):
        col1, col2 = st.columns(2)
        fonte = col1.text_input("Fonte (ex: IFCE)")
        ano = col2.text_input("Ano")
        conteudo = col1.text_input("Conteúdo")
        dificuldade = col2.selectbox("Dificuldade", ["Fácil", "Média", "Difícil"])
        
        txt_base = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        
        st.info("Separe as alternativas com ponto e vírgula (;). Ex: 10; 15; 20; 25; 30")
        alts = st.text_input("Alternativas")
        gab = st.text_input("Gabarito (Letra ou Valor)")
        
        if st.form_submit_button("Salvar na Planilha"):
            nova_q = pd.DataFrame([{
                "id": len(df) + 1,
                "fonte": fonte,
                "ano": ano,
                "conteudo": conteudo,
                "dificuldade": dificuldade,
                "texto_base": txt_base,
                "enunciado": enun,
                "alternativas": alts,
                "gabarito": gab
            }])
            
            df_final = pd.concat([df, nova_q], ignore_index=True)
            conn.update(data=df_final)
            st.success("Dados salvos com sucesso!")
            st.balloons()
