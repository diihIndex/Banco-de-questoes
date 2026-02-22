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
    c1, c2 = st.columns([3, 1])
    nome_inst = c1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_total = c2.text_input("Valor da Prova", "10,0")
    
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
    
    # Linha 101 Corrigida aqui
    df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
    temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
    sel_tema = f2.multiselect("Selecione o Conteúdo", temas)
    formato = f2.radio("Estilo das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
    
    st.write("---")
    check1, check2 = st.columns(2)
    add_cartao = check1.checkbox("Incluir Cartão-Resposta (Colunas de 12)", value=True)
    add_gab = check2.checkbox("Incluir Gabarito para o Professor", value=True)

# Seleção de Questões
df_f = df_filter[df_filter['conteudo'].isin(sel_tema)] if sel_tema else df_filter
df_f['label'] = df_f['id'].astype(str) + " | " + df_f['comando'].astype(str).str[:80]
selecao = st.multiselect("📋 Selecione as questões na lista abaixo:", options=df_f['label'].tolist())

# --- 4. GERAÇÃO DO HTML ---
if selecao:
    ids = [int(s.split(" | ")[0]) for s in selecao]
    df_prova = df[df['id'].isin(ids)].copy()

    img_sme = f'<img src="data:image/png;base64,{sme_b64}" style="max-height: 65px;">' if sme_b64 else ""
    img_esc = f'<img src="data:image/png;base64,{esc_b64}" style="max-height: 65px;">' if esc_b64 else ""

    html_cabecalho = f"""
    <table class="header-table">
        <tr>
            <td style="width: 15%; text-align: center;">{img_sme}</td>
            <td style="width: 70%; text-align: center;">
                <h3 style="margin:0;">{nome_inst.upper()}</h3>
                <p style="margin:4px;"><b>{tipo_doc.upper()} DE {", ".join(sel_disc).upper()}</b></p>
            </td>
            <td style="width: 15%; text-align: center;">{img_esc}</td>
        </tr>
        <tr>
            <td colspan="2">
                ESTUDANTE: __________________________________________________________________________<br>
                <div style="margin-top:15px; display: flex; justify-content: space-between;">
                    <span>Nº: [_______]</span> <span>TURMA: [___________]</span> <span>DATA: ____/____/____</span>
                </div>
            </td>
            <td class="nota-cell">NOTA<br><br>______ / {valor_total}</td>
        </tr>
    </table>
    """

    html_corpo = ""
    for i, row in df_prova.reset_index().iterrows():
        t_base = f"<i>{row['texto_base']}</i> " if pd.notna(row['texto_base']) and str(row['texto_base']).strip() != "" else ""
        html_corpo += f'<div class="quest-box"><b>QUESTÃO {i+1}</b> ({row["fonte"]})<br>{t_base}{row["comando"]}'
        if formato == "Objetiva":
            alts = str(row['alternativas']).split(';')
            letras = ['A', 'B', 'C', 'D', 'E']
            html_corpo += "<ul>"
            for idx, alt in enumerate(alts):
                if idx < len(letras):
                    html_corpo += f"<li>{letras[idx]}) {alt.strip()}</li>"
            html_corpo += "</ul>"
        else:
            html_corpo += "<div style='border: 1px dashed #ccc; height: 180px; margin-top: 10px;'></div>"
        html_corpo += "</div>"

    if add_cartao and formato == "Objetiva":
        def grid(n): return "".join(['<div class="grid-box"></div>' for _ in range(n)])
        cartao_html = '<div class="cartao-page">'
        cartao_html += f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">{img_sme}<div><b>CARTÃO-RESPOSTA OFICIAL</b><br><small>{nome_inst}</small></div>{img_esc}</div>'
        cartao_html += f'NOME:<br><div class="grid-container">{grid(30)}</div>'
        cartao_html += f'<div style="display: flex; gap: 30px;"><div>Nº:<br><div class="grid-container">{grid(4)}</div></div><div>TURMA:<br><div class="grid-container">{grid(8)}</div></div><div>DATA:<br><div class="grid-container">{grid(2)}/{grid(2)}/{grid(2)}</div></div></div>'
        cartao_html += '<hr style="margin: 20px 0; border: 1px solid black;">'
        cartao_html += '<div class="columns-container">'
        num_questoes = len(df_prova)
        for c in range(0, num_questoes, 12):
            cartao_html += '<div class="column">'
            for i in range(c, min(c + 12, num_questoes)):
                bubbles = "".join([f'<div class="bubble-circle">{l}</div>' for l in ['A', 'B', 'C', 'D', 'E']])
                cartao_html += f'<div class="cartao-row"><span class="q-num">{i+1:02d}</span> {bubbles}</div>'
            cartao_html += '</div>'
        cartao_html += '</div></div>'
        html_corpo += cartao_html

    if add_gab:
        html_corpo += '<div class="gabarito-section"><h3>GABARITO DO PROFESSOR</h3><div style="display:flex; flex-wrap:wrap; gap:10px;">'
        for i, row in df_prova.reset_index().iterrows():
            g = row.get('gabarito', 'N/A')
            html_corpo += f'<div style="width:100px; border:1px solid #ccc; padding:5px;"><b>Q{i+1}:</b> {g}</div>'
        html_corpo += '</div></div>'

    html_final = f"<!DOCTYPE html><html>{MATHJAX_CONFIG}{CSS_ESTILOS}<body>{html_cabecalho}{html_corpo}</body></html>"
    
    st.divider()
    st.download_button("📥 Baixar Avaliação Pronta", html_final, "avaliacao_sme.html", "text/html")
    st.components.v1.html(html_final, height=1000, scrolling=True)
else:
    st.info("💡 Selecione pelo menos uma questão na lista acima para gerar o material.")
