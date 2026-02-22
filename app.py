import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- CONFIGURAÇÕES VISUAIS E SCRIPTS (Constantes para evitar erros de sintaxe) ---

CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
    
    /* Quadrados Grandes para o Cartão Resposta */
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; align-items: center; }
    .grid-box { width: 28px; height: 35px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 30px; }
    .cartao-row { display: flex; align-items: center; justify-content: center; margin-bottom: 18px; }
    
    /* Letras centralizadas acima dos círculos para máscara de correção */
    .bubble-group { display: flex; flex-direction: column; align-items: center; margin: 0 12px; }
    .bubble-letter { font-size: 9pt; font-weight: bold; margin-bottom: 3px; }
    .bubble-circle { width: 22px; height: 22px; border: 2px solid black; border-radius: 50%; }
    
    .nota-cell { background: #eee; text-align: center; font-weight: bold; width: 100px; }
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

# --- APP PRINCIPAL ---

st.set_page_config(page_title="Gerador SME", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

st.sidebar.header("🖼️ Logotipos")
l_sme = st.sidebar.file_uploader("Logo SME (Esquerda)", type=["png", "jpg"])
l_esc = st.sidebar.file_uploader("Logo Escola (Direita)", type=["png", "jpg"])
sme_b64 = get_image_base64(l_sme)
esc_b64 = get_image_base64(l_esc)

st.header("📄 Gerador de Avaliações Profissionais")

with st.expander("🏫 Cabeçalho e Filtros", expanded=True):
    col1, col2 = st.columns([3, 1])
    nome_inst = col1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_prova = col2.text_input("Valor", "10,0")
    
    f1, f2 = st.columns(2)
    disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
    sel_disc = f1.multiselect("Disciplina", disciplinas)
    tipo_doc = f1.selectbox("Documento", ["Prova", "Atividade", "Simulado"])
    df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
    temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
    sel_tema = f2.multiselect("Conteúdo", temas)
    formato = f2.radio("Tipo", ["Objetiva", "Subjetiva"], horizontal=True)
    add_cartao = st.checkbox("Incluir Cartão-Resposta Quadriculado")

df_f = df_filter[df_filter['conteudo'].isin(sel_tema)] if sel_tema else df_filter
df_f['label'] = df_f['id'].astype(str) + " | " + df_f['comando'].astype(str).str[:80]
selecao = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

if selecao:
    ids = [int(s.split(" | ")[0]) for s in selecao]
    df_prova = df
