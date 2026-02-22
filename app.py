import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. CONFIGURAÇÕES VISUAIS (CSS Otimizado para Colunas e Bolinhas) ---
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
    
    /* Quadrados de Identificação */
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 26px; height: 32px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    
    /* Layout do Cartão em Colunas */
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 20px; }
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 30px; justify-content: flex-start; margin-top: 20px; }
    .column { display: flex; flex-direction: column; gap: 8px; }
    
    /* Bolinhas com Letras dentro (Estilo Compacto) */
    .cartao-row { display: flex; align-items: center; gap: 8px; height: 30px; }
    .q-num { width: 25px; font-weight: bold; font-size: 11pt; text-align: right; }
    .bubble-circle { 
        width: 24px; height: 24px; 
        border: 1.5px solid black; 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 9pt; 
        font-weight: bold;
    }
    
    .nota-cell { background: #eee; text-align: center; font-weight: bold; width: 100px; }
    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; margin-top: 40px; }
    ul { list-style-type: none; padding-left: 20px; }
    li { margin-bottom: 6px; }
</style>
"""

MATHJAX_CONFIG = r"""
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] } };
</script>
"""

def get_image_base64(image_file):
    if image_file is not None:
        try:
            return base64.b64encode(image_file.getvalue()).decode()
        except: return None
    return None

# --- 2. CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Gerador SME Fortaleza", layout="wide")

st.sidebar.header("🖼️ Logotipos")
l_sme = st.sidebar.file_uploader("Logo SME (Esquerda)", type=["png", "jpg"])
l_esc = st.sidebar.file_uploader("Logo Escola (Direita)", type=["png", "jpg"])
sme_b64 = get_image_base64(l_sme)
esc_b64 = get_image_base64(l_esc)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

# --- 3. INTERFACE ---
st.header("📄 Gerador de Avaliações Profissionais")

with st.expander("🏫 Dados do Documento", expanded=True):
    c1, c2 = st.columns([3, 1])
    nome_inst = c1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_total = c2.text_input("Valor", "10,0")
    
    f1, f2 = st.columns(2)
    disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
    sel_disc = f1.multiselect("Disciplina(s)", disciplinas)
    tipo_doc = f1.selectbox("Tipo de Material", ["Prova", "Simulado", "Atividade"])
    df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
    temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
    sel_tema = f2.multiselect("Conteúdo/Tema", temas)
    formato = f2.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
    
    check1, check2 = st.columns(2)
    add_cartao = check1.checkbox("Incluir Cartão-Resposta Compacto", value=True)
    add_gab = check2.checkbox("Incluir Gabarito (Professor
