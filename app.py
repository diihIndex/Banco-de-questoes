import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. CONFIGURAÇÕES VISUAIS FIXAS (Evita erros de Sintaxe) ---

# CSS para garantir quadrados grandes e alinhamento para máscara de correção
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
    
    /* Quadrados Grandes para o Cartão Resposta */
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 28px; height: 36px; border: 1.5px solid black; margin-right: -1.5px; margin-bottom: 5px; display: inline-block; }
    
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 30px; }
    .cartao-row { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    
    /* Alinhamento para Máscara: Letra em cima do Círculo */
    .bubble-group { display: flex; flex-direction: column; align-items: center; margin: 0 12px; }
    .bubble-letter { font-size: 10pt; font-weight: bold; margin-bottom: 4px; }
    .bubble-circle { width: 22px; height: 22px; border: 2px solid black; border-radius: 50%; }
    
    .nota-cell { background: #eee; text-align: center; font-weight: bold; width: 100px; }
    ul { list-style-type: none; padding-left: 20px; }
    li { margin-bottom: 8px; }
</style>
"""

# Script para renderizar LaTeX (Raiz quadrada, frações, etc)
MATHJAX_SCRIPT = r"""
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] } };
</script>
"""

# --- 2. FUNÇÕES E CONEXÃO ---

def get_image_base64(image_file):
    if image_file is not None:
        try:
            return base64.b64encode(image_file.getvalue()).decode()
        except: return None
    return None

st.set_page_config(page_title="Gerador SME Fortaleza", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro na planilha: {e}")
    st.stop()

# --- 3. INTERFACE ---

st.sidebar.header("🖼️ Logotipos Oficiais")
l_sme = st.sidebar.file_uploader("Logo SME (Esquerda)", type=["png", "jpg"])
l_esc = st.sidebar.file_uploader("Logo Escola (Direita)", type=["png", "jpg"])
sme_b64 = get_image_base64(l_sme)
esc_b64 = get_image_base64(l_esc)

st.header("📄 Gerador de Avaliações Profissionais")

with st.expander("🏫 Cabeçalho e Filtros", expanded=True):
    col1, col2 = st.columns([3, 1])
    nome_inst = col1.text_input("Instituição", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_prova = col
