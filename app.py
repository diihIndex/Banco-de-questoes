import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. CONFIGURAÇÕES VISUAIS (CSS) ---
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
    
    /* Quadrados de Identificação */
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 26px; height: 32px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    
    /* Layout do Cartão em Colunas (Máx 12) */
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 20px; margin-top: 20px; }
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 40px; justify-content: flex-start; margin-top: 20px; }
    .column { display: flex; flex-direction: column; gap: 10px; }
    
    /* Bolinhas Compactas com Letras Dentro */
    .cartao-row { display: flex; align-items: center; gap: 8px; height: 30px; }
    .q-num { width: 25px; font-weight: bold; font-size: 11pt; text-align: right; margin-right: 5px; }
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

def limpar_coluna(nome):
    n = str(nome).lower().strip()
    subs = {'á': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'ú': 'u', 'ç': 'c'}
    for k, v in subs.items():
        n = n.replace(k, v)
    return n

# --- 2. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="Gerador SME Fortaleza", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [limpar_coluna(c) for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
st.header("📄 Gerador de Avaliações SME")

with st.expander("🏫 1. Configurações da Instituição e Logotipos", expanded=True):
    # Campos de Identificação
    c1, c2 = st.columns([3, 1])
    nome_inst = c1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_total = c2.text_input("Valor da Prova", "10,0")
    
    # Uploads de Logo agora estão aqui
    st.write("**Logotipos do Cabeçalho:**")
    col_img1, col_img2 = st.columns(2)
    l_sme = col_img1.file_uploader("Logo Esquerda (ex: SME)", type=["png", "jpg", "jpeg"])
    l_esc = col_img2.file_uploader("Logo Direita (ex: Escola)", type=["png", "jpg", "jpeg"])
    
    sme_b64 = get_image_base64(l_sme)
    esc_b64 = get_image_base64(l_esc)

with st.expander("🎯 2. Filtros e Tipo de Documento", expanded=True):
    f1, f2 = st.columns(2)
    disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
    sel_disc = f1.multiselect("Selecione a(s) Disciplina(s)", disciplinas)
    tipo_doc = f1.selectbox("Tipo de Material", ["Prova", "Simulado", "Atividade"])
    
    df_filter = df[df['discipl
