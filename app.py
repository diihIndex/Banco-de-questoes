import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Avaliações IFCE", layout="wide", page_icon="📝")

# 2. Conexão e Dados com tratamento de erro
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    
    # NORMALIZAÇÃO DE COLUNAS: Remove espaços, acentos e deixa minúsculo
    df.columns = [
        str(c).lower().strip()
        .replace('ú', 'u').replace('ê', 'e').replace('ã', 'a')
        .replace('ç', 'c').replace('í', 'i').replace('é', 'e') 
        for c in df.columns
    ]
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# 3. Navegação Lateral - DEFINIÇÃO ÚNICA DOS NOMES
MENU_BANCO = "🔍 Banco de Questões"
MENU_CADASTRO = "📝 Cadastrar Nova"
MENU_GERADOR = "📄 Gerador de Prova"

opcao = st.sidebar.radio("Navegar para:", [MENU_BANCO, MENU_CADASTRO, MENU_GERADOR])

# --- PÁGINA: BANCO DE QUESTÕES ---
if opcao == MENU_BANCO:
    st.header("📊 Visualização do Banco de Dados")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("A planilha está vazia.")

# --- PÁGINA: CADASTRAR NOVA ---
elif opcao == MENU_CADASTRO:
    st.header("📝 Cadastrar Nova Questão")
    st.info("Funcionalidade de cadastro em desenvolvimento.")

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    # Verifica se as colunas essenciais existem antes de prosseguir
    colunas_obrigatorias = ['id', 'fonte', 'enunciado']
    missing = [c for c in colunas_obrigatorias if c not in df.columns]
    
    if missing:
        st.error(f"A planilha precisa ter as colunas: {', '.join(missing)}")
        st.write("Colunas detectadas:", list(df.columns))
    else:
        # --- SEÇÃO DE CONFIGURAÇÃO ---
        with st.expander("⚙️ Configurações do Documento", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                tipo_doc = st.selectbox("Tipo de Cabeçalho", ["Prova", "Atividade"])
                tipo_questao = st.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
            with col2:
                add_gabarito = st.checkbox("Adicionar Gabarito (Modelo IFCE)")
                disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else ["Não definida"]
                f_disciplina = st.multiselect("Filtrar por Disciplina", disciplinas)

        # Filtros
        df_f = df.copy()
        if f_disciplina:
            df_f = df_f[df_f['disciplina'].isin(f_disciplina)]

        # CRIAÇÃO DA LABEL (com segurança para nulos)
        df_f['enunciado_curto'] = df_f['enunciado'].fillna("").astype(str).str[:70]
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].fillna("IFCE") + " | " + df_f['enunciado_curto'] + "..."
        
        selecionadas = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

        if selecionadas:
            # Extração segura de IDs
            ids = [int(s.split(" | ")[0]) for s in selecionadas if s.split(" | ")[0].isdigit()]
            df_prova = df[df['id'].isin(ids)]

            # Lógica simples de exibição (HTML para baixar)
            st.success(f"{len(df_prova)} questões selecionadas!")
            # (Aqui continuaria a lógica de construção do HTML que enviamos antes)
