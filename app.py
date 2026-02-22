import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Avaliações SME", layout="wide", page_icon="📝")

def get_image_base64(image_file):
    if image_file is not None:
        try:
            return base64.b64encode(image_file.getvalue()).decode()
        except: return None
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

# 3. Sidebar
st.sidebar.header("🖼️ Logotipos Oficiais")
logo_sme_file = st.sidebar.file_uploader("Logo SME (Esquerda)", type=["png", "jpg", "jpeg"])
logo_esc_file = st.sidebar.file_uploader("Logo Escola (Direita)", type=["png", "jpg", "jpeg"])
sme_b64 = get_image_base64(logo_sme_file)
esc_b64 = get_image_base64(logo_esc_file)

MENU_GERADOR = "📄 Gerador de Prova"
opcao = st.sidebar.radio("Navegar para:", [MENU_GERADOR])

if opcao == MENU_GERADOR:
    st.header("📄 Gerador de Avaliações Profissionais")
    
    with st.expander("🏫 Dados do Cabeçalho", expanded=True):
        col1, col2 = st.columns([3, 1])
        nome_inst = col1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
        valor_prova = col2.text_input("Valor da Prova", "10,0")

    with st.expander("🎯 Filtros e Opções", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina(s)", disciplinas)
            tipo_doc = st.selectbox("Tipo de Material", ["Prova", "Atividade", "Simulado"])
        with f2:
            df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
            temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
            sel_tema = st.multiselect("Conteúdo", temas)
            formato = st.radio("Tipo de Questão", ["Objetiva", "Subjetiva"], horizontal=True)
        
        add_cartao = st.checkbox("Incluir Cartão-Resposta Quadriculado")
        add_gab = st.checkbox("Incluir Gabarito p/ Professor")

    df_f = df_filter[df_filter['conteudo'].isin(sel_tema)] if sel_tema else df_filter
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecao = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if selecao:
        ids = [int(s.split(" | ")[0]) for s in selecao]
        df_prova = df[df['id'].isin(ids)].copy()

        # HTML Head - Correção definitiva para LaTeX
        html_head = r"""
        <head>
            <meta charset='UTF-8'>
            <script>
                window.MathJax = {
                    tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], processEscapes: true },
                    options: { renderAtStart: true }
                };
            </script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
            <style>
                body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
                .header-table { width: 100%; border:
