import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. CONFIGURAÇÕES VISUAIS E SCRIPTS (Constantes Globais para evitar erros) ---
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
    .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
    .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
    
    /* Quadrados Grandes para os campos de identificação */
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
    li { margin-bottom: 8px; }
    
    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; margin-top: 50px; }
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

# Sidebar (Menu Lateral) sempre visível
st.sidebar.header("🖼️ Logotipos e Identidade")
l_sme = st.sidebar.file_uploader("Logo SME (Esquerda)", type=["png", "jpg", "jpeg"])
l_esc = st.sidebar.file_uploader("Logo Escola (Direita)", type=["png", "jpg", "jpeg"])
sme_b64 = get_image_base64(l_sme)
esc_b64 = get_image_base64(l_esc)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    # Normalização de colunas
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
st.header("📄 Gerador de Material Didático Profissional")

with st.expander("🏫 Cabeçalho da Instituição", expanded=True):
    col1, col2 = st.columns([3, 1])
    nome_inst = col1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_total = col2.text_input("Valor da Avaliação", "10,0")

with st.expander("🎯 Filtros e Seleção", expanded=True):
    f1, f2 = st.columns(2)
    disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
    sel_disc = f1.multiselect("Disciplina(s)", disciplinas)
    tipo_doc = f1.selectbox("Tipo de Material", ["Prova", "Simulado", "Atividade"])
    
    df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
    temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
    sel_tema = f2.multiselect("Conteúdo/Tema", temas)
    formato = f2.radio("Formato das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
    
    st.write("---")
    c1, c2 = st.columns(2)
    add_cartao = c1.checkbox("Gerar Cartão-Resposta Quadriculado", value=True)
    add_gab = c2.checkbox("Gerar Gabarito (Professor)", value=True)

# Lista de Questões
df_f = df_filter[df_filter['conteudo'].isin(sel_tema)] if sel_tema else df_filter
df_f['label'] = df_f['id'].astype(str) + " | " + df_f['comando'].astype(str).str[:80]
selecao = st.multiselect("Selecione as questões para incluir:", options=df_f['label'].tolist())

# --- 4. CONSTRUÇÃO DO DOCUMENTO ---
if selecao:
    ids = [int(s.split(" | ")[0]) for s in selecao]
    df_prova = df[df['id'].isin(ids)].copy()

    img_sme = f'<img src="data:image/png;base64,{sme_b64}" style="max-height: 70px;">' if sme_b64 else ""
    img_esc = f'<img src="data:image/png;base64,{esc_b64}" style="max-height: 70px;">' if esc_b64 else ""

    # Cabeçalho (Estudante em linha simples)
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

    # Questões
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

    # Cartão Resposta (Quadriculado)
    if add_cartao and formato == "Objetiva":
        def grid(n): return "".join(['<div class="grid-box"></div>' for _ in range(n)])
        
        html_corpo += '<div class="cartao-page">'
        html_corpo += f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">{img_sme}<div style="text-align: center;"><b>CARTÃO-RESPOSTA OFICIAL</b><br><small>{nome_inst}</small></div>{img_esc}</div>'
        html_corpo += f'NOME COMPLETO DO ESTUDANTE:<br><div class="grid-container">{grid(30)}</div>'
        html_corpo += f'<div style="display: flex; gap: 40px; margin-top: 10px;">'
        html_corpo += f'<div>Nº:<br><div class="grid-container">{grid(4)}</div></div>'
        html_corpo += f'<div>TURMA:<br><div class="grid-container">{grid(8)}</div></div>'
        html_corpo += f'<div>DATA:<br><div class="grid-container">{grid(2)} / {grid(2)} / {grid(2)}</div></div>'
        html_corpo += '</div><hr style="margin: 30px 0; border: 1px solid black;">'
        
        for i in range(len(df_prova)):
            bubbles = "".join([f'<div class="bubble-group"><span class="bubble-letter">{l}</span><div class="bubble-circle"></div></div>' for l in ['A', 'B', 'C', 'D', 'E']])
            html_corpo += f'<div class="cartao-row"><b style="width: 55px; font-size: 13pt;">{str(i+1).zfill(2)}</b> {bubbles}</div>'
        html_corpo += '</div>'

    # Gabarito para o Professor
    if add_gab:
        html_corpo += '<div class="gabarito-section"><h2>GABARITO DO PROFESSOR</h2>'
        for i, row in df_prova.reset_index().iterrows():
            g = row.get('gabarito', 'N/A')
            html_corpo += f'<p><b>Questão {i+1}:</b> {g}</p>'
        html_corpo += '</div>'

    # Unificação
    html_final = f"<!DOCTYPE html><html>{MATHJAX_CONFIG}{CSS_ESTILOS}<body>{html_cabecalho}{html_corpo}</body></html>"
    
    # Exibição e Download
    st.success(f"Documento gerado com {len(df_prova)} questões!")
    col_d1, col_d2 = st.columns(2)
    col_d1.download_button("📥 Baixar Arquivo (HTML)", html_final, "avaliacao_sme.html", "text/html")
    
    st.divider()
    st.subheader("👁️ Pré-visualização")
    st.components.v1.html(html_final, height=1000, scrolling=True)

else:
    st.info("💡 Escolha as questões no campo acima para gerar a pré-visualização e o botão de download.")
