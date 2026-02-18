import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Banco de Questões Permanente", layout="wide")

st.title("🗄️ Banco de Questões via Google Sheets")

# Criar a conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler os dados
def load_data():
    return conn.read(ttl="0") # ttl="0" força a atualização imediata

df = load_data()

menu = st.sidebar.selectbox("Menu", ["Ver Banco", "Cadastrar Questão"])

if menu == "Ver Banco":
    st.header("📋 Questões Salvas na Nuvem")
    st.dataframe(df, use_container_width=True)

elif menu == "Cadastrar Questão":
    st.header("📝 Novo Item")
    
    with st.form("form_novo_item"):
        col1, col2 = st.columns(2)
        fonte = col1.text_input("Fonte")
        ano = col2.text_input("Ano")
        conteudo = col1.text_input("Conteúdo")
        dificuldade = col2.selectbox("Dificuldade", ["Fácil", "Média", "Difícil"])
        txt_base = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        
        # Alternativas simplificadas para a planilha (salvas como string)
        alts = st.text_input("Alternativas (separe por ponto e vírgula ';')")
        gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Salvar na Planilha"):
            # Criar nova linha
            nova_linha = pd.DataFrame([{
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
            
            # Combinar e atualizar a planilha
            df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
            conn.update(data=df_atualizado)
            st.success("✅ Salvo com sucesso no Google Sheets!")
            st.balloons()
