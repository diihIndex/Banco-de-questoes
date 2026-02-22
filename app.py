import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. FUNÇÕES AUXILIARES ---

def converter_link_drive(url):
    """Converte links de compartilhamento do Google Drive em links de visualização direta."""
    url = str(url).strip()
    if 'drive.google.com' in url:
        try:
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
                return f'https://lh3.googleusercontent.com/u/0/d/{file_id}'
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
                return f'https://lh3.googleusercontent.com/u/0/d/{file_id}'
        except Exception:
            return url
    return url

def get_image_base64(image_file):
    if image_file:
        try: return base64.b64encode(image_file.getvalue()).decode()
        except: return None
    return None

def limpar_coluna(nome):
    n = str(nome).lower().strip()
    subs = {'á': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'ú': 'u', 'ç': 'c'}
    for k, v in subs.items(): n = n.replace(k, v)
    return n

# --- 2. CONFIGURAÇÕES VISUAIS (CSS) ---
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; line-height: 1.4; }
    .texto-comando-container { margin-top: 5px; white-space: pre-wrap; }
    .quest-img { display: block; margin: 15px auto; max-width: 80%; max-height: 350px; border: 1px solid #ddd; padding: 5px; }
    
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 26px; height: 32px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 30px; margin-top: 20px; }
    .instrucoes-cartao { border: 1.5px solid black; padding: 12px; margin-bottom: 25px; font-size: 8.5pt; background-color: #fcfcfc; line-height: 1.3; }
    .cartao-identificacao { margin-bottom: 45px; } 
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 30px; justify-content: flex-start; }
    .column { display: flex; flex-direction: column; border: 1.5px solid #000; min-width: 230px; }
    .cartao-header-row { background-color: #eee; display: flex; font-size: 7.5pt; font-weight: bold; border-bottom: 1.5px solid #000; }
    .cartao-row { display: flex; align-items: center; height: 35px; border-bottom: 0.5px solid #ccc; }
    .q-num-col { width: 55px; font-weight: bold; text-align: center; border-right: 2.5px solid black; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 11pt; }
    .bubbles-col { display: flex; gap: 8px; padding: 0 12px; align-items: center; }
    .bubble-circle { width: 24px; height: 24px; border: 1.5px solid black; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9pt; font-weight: bold; }
    .assinatura-container { margin-top: 80px; display: flex; justify-content: flex-end; }
    .assinatura-box { border-top: 1.5px solid #000; width: 400px; text-align: center; padding-top: 8px; font-size: 9pt; font-weight: bold; }

    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; margin-top: 40px; }
    .gabarito-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
    .gabarito-item { width: 100px; border: 1px solid #ccc; padding: 5px; text-align: center; font-size: 10pt; }

    ul { list-style-type: none; padding-left: 5px; margin-top: 8px; }
    li { margin-bottom: 6px; }
    @media print { .no-print { display: none; } }
</style>
"""

MATHJAX_AND_PRINT = r"""
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$']] } };
</script>
<script>function printPage(){ window.print(); }</script>
"""

# --- 3. CONEXÃO E INTERFACE ---
st.set_page_config(page_title="Gerador de Avaliações", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [limpar_coluna(c) for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}"); st.stop()

st.title("📄 Gerador de Avaliações")
aba_gerar, aba_cadastrar = st.tabs(["📋 Gerar Avaliação", "📥 Cadastrar Questão"])

with aba_cadastrar:
    st.subheader("Cadastro de Questão")
    with st.form("form_cad"):
        c1, c2, c3, c4 = st.columns(4)
        disc_cad = c1.selectbox("Disciplina", sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else ["Português"])
        tema_cad = c2.text_input("Conteúdo")
        dif_cad = c3.select_slider("Dificuldade", options=["Fácil", "Médio", "Difícil"])
        ano_cad = c4.text_input("Ano")
        fonte_cad = st.text_input("Fonte")
        texto_base_cad = st.text_area("Texto Base")
        url_img_cad = st.text_input("Link da Imagem (Google Drive ou Web)")
        comando_cad = st.text_area("Comando")
        alts_cad = st.text_input("Alternativas (A;B;C;D;E)")
        gab_cad = st.text_input("Gabarito")
        if st.form_submit_button("Salvar"): st.info("Copie os dados para sua planilha!")

with aba_gerar:
    with st.expander("🏫 Configurações da Instituição", expanded=True):
        c_nome, c_
