import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Avaliações SME", layout="wide", page_icon="📝")

# Função para converter imagem em base64
def get_image_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

# 2. Conexão e Dados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# 3. Sidebar: Carregamento de Logos
st.sidebar.header("🖼️ Logotipos Oficiais")
logo_sme = st.sidebar.file_uploader("Logo Secretaria (SME)", type=["png", "jpg", "jpeg"])
logo_escola = st.sidebar.file_uploader("Logo da Escola (Cônego)", type=["png", "jpg", "jpeg"])

sme_b64 = get_image_base64(logo_sme)
escola_b64 = get_image_base64(logo_escola)

MENU_GERADOR = "📄 Gerador de Prova"
# (Outras opções de menu omitidas para brevidade, foquei no Gerador conforme solicitado)
opcao = st.sidebar.radio("Navegar para:", [MENU_GERADOR])

if opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático Profissional")
    
    with st.expander("🏫 Cabeçalho e Identificação", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        nome_inst = col1.text_input("Instituição", "Escola Municipal Cônego Francisco Pereira da Silva")
        valor_prova = col2.text_input("Valor da Prova", "10,0")
        num_quadrados = col3.number_input("Quadrados p/ Nome", 10, 50, 30)

    with st.expander("🎯 Filtros", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            sel_disc = st.multiselect("Disciplina", sorted(df['disciplina'].unique()))
            tipo_doc = st.selectbox("Documento", ["Prova", "Atividade", "Simulado"])
        with f2:
            sel_tema = st.multiselect("Conteúdo", sorted(df[df['disciplina'].isin(sel_disc)]['conteudo'].unique()) if sel_disc else [])
            formato = st.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
        
        c_check1, c_check2 = st.columns(2)
        add_cartao = c_check1.checkbox("Gerar Cartão-Resposta p/ Máscara")
        add_gab = c_check2.checkbox("Gabarito do Professor")

    # Lógica de filtragem e seleção (ID | FONTE | COMANDO)
    df_f = df.copy()
    if sel_disc: df_f = df_f[df_f['disciplina'].isin(sel_disc)]
    if sel_tema: df_f = df_f[df_f['conteudo'].isin(sel_tema)]
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecao = st.multiselect("Questões:", options=df_f['label'].tolist())

    if selecao:
        ids = [int(s.split(" | ")[0]) for s in selecao]
        df_prova = df[df['id'].isin(ids)].copy()

        # HTML Head com CSS para o Grid Quadriculado e Cartão
        html_head = r"""
        <head>
            <meta charset='UTF-8'>
            <script id="MathJax-script" async src="
