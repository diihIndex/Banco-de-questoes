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
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 26px; height: 32px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 20px; margin-top: 20px; }
    .instrucoes-cartao { border: 1px solid black; padding: 8px; margin-bottom: 15px; font-size: 8pt; background-color: #f9f9f9; }
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 40px; justify-content: flex-start; margin-top: 15px; }
    .column { display: flex; flex-direction: column; gap: 10px; }
    .cartao-row { display: flex; align-items: center; gap: 8px; height: 30px; }
    .q-num { width: 25px; font-weight: bold; font-size: 11pt; text-align: right; margin-right: 5px; }
    .bubble-circle { width: 24px; height: 24px; border: 1.5px solid black; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9pt; font-weight: bold; }
    .nota-cell { background: #eee; text-align: center; font-weight: bold; width: 100px; }
    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; margin-top: 40px; }
    ul { list-style-type: none; padding-left: 5px; margin-top: 8px; }
    li { margin-bottom: 6px; }
    @media print { .no-print { display: none; } }
</style>
"""

PRINT_SCRIPT = "<script>function printPage(){ window.print(); }</script>"

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

# --- 2. CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Gerador de Avaliações", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).copy()
    df.columns = [limpar_coluna(c) for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# --- 3. BARRA LATERAL: ADICIONAR QUESTÃO ---
with st.sidebar:
    st.header("📥 Adicionar ao Banco")
    with st.form("form_questao", clear_on_submit=True):
        nova_disc = st.selectbox("Disciplina", sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else [""])
        novo_tema = st.text_input("Conteúdo/Tema")
        nova_dif = st.select_slider("Dificuldade", options=["Fácil", "Médio", "Difícil"])
        novo_comando = st.text_area("Comando da Questão")
        novas_alts = st.text_input("Alternativas (separadas por ;)")
        novo_gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Salvar Questão"):
            # Aqui entraria a lógica de conn.update() se configurado
            st.success("Questão enviada para análise!")

# --- 4. INTERFACE PRINCIPAL ---
st.header("📄 Gerador de Avaliações")

with st.expander("🏫 1. Configurações e Logotipos", expanded=True):
    c1, c2 = st.columns([3, 1])
    nome_inst = c1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
    valor_total = c2.text_input("Valor da Prova", "10,0")
    
    col_img1, col_img2 = st.columns(2)
    l_sme = col_img1.file_uploader("Logo Esquerda", type=["png", "jpg", "jpeg"])
    l_esc = col_img2.file_uploader("Logo Direita", type=["png", "jpg", "jpeg"])
    sme_b64 = get_image_base64(l_sme)
    esc_b64 = get_image_base64(l_esc)

with st.expander("🎯 2. Filtros de Seleção", expanded=True):
    f1, f2, f3 = st.columns([1, 1, 1])
    
    disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
    sel_disc = f1.multiselect("Disciplina(s)", disciplinas)
    
    df_f1 = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
    temas = sorted(df_f1['conteudo'].unique()) if 'conteudo' in df_f1.columns else []
    sel_tema = f2.multiselect("Conteúdo", temas)
    
    # FILTRO DE DIFICULDADE DE VOLTA
    dificuldades = sorted(df['dificuldade'].unique()) if 'dificuldade' in df.columns else ["Fácil", "Médio", "Difícil"]
    sel_dif = f3.multiselect("Dificuldade", dificuldades)
    
    df_filter = df_f1[df_f1['conteudo'].isin(sel_tema)] if sel_tema else df_f1
    if sel_dif:
        df_filter = df_filter[df_filter['dificuldade'].isin(sel_dif)]
        
    tipo_doc = st.selectbox("Tipo de Material", ["Prova", "Simulado", "Atividade"])
    formato = st.radio("Estilo", ["Objetiva", "Subjetiva"], horizontal=True)
    
    st.write("---")
    check1, check2 = st.columns(2)
    add_cartao = check1.checkbox("Incluir Cartão-Resposta", value=True)
    add_gab = check2.checkbox("Incluir Gabarito", value=True)

# Seleção de Questões
df_filter['label'] = df_filter['id'].astype(str) + " | [" + df_filter['dificuldade'].astype(str) + "] " + df_filter['comando'].astype(str).str[:60] + "..."
selecao = st.multiselect("📋 Selecione as questões abaixo:", options=df_filter['label'].tolist())

# --- 5. PROCESSAMENTO E HTML ---
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
                if idx < len(letras): html_corpo += f"<li>{letras[idx]}) {alt.strip()}</li>"
            html_corpo += "</ul>"
        else:
            html_corpo += "<div style='border: 1px dashed #ccc; height: 180px; margin-top: 10px;'></div>"
        html_corpo += "</div>"

    if add_cartao and formato == "Objetiva":
        def grid(n): return "".join(['<div class="grid-box"></div>' for _ in range(n)])
        cartao_html = f'<div class="cartao-page">'
        cartao_html += f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">{img_sme}<b>CARTÃO-RESPOSTA OFICIAL</b>{img_esc}</div>'
        cartao_html += '<div class="instrucoes-cartao"><b>INSTRUÇÕES:</b> Use caneta azul ou preta. Preencha totalmente o círculo da alternativa. Marque apenas uma opção por questão.</div>'
        cartao_html += f'NOME:<br><div class="grid-container">{grid(30)}</div>'
        cartao_html += '<div class="columns-container">'
        num_q = len(df_prova)
        for c in range(0, num_q, 12):
            cartao_html += '<div class="column">'
            for i in range(c, min(c + 12, num_q)):
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

    btn_imprimir = '<div class="no-print" style="text-align:center; margin: 20px;"><button onclick="window.print()" style="padding:10px 20px; font-size:16px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">🖨️ Imprimir / Salvar como PDF</button></div>'
    html_final = f"<!DOCTYPE html><html>{PRINT_SCRIPT}{CSS_ESTILOS}<body>{btn_imprimir}{html_cabecalho}{html_corpo}</body></html>"
    
    st.divider()
    st.download_button("📥 Baixar Avaliação", html_final, "avaliacao.html", "text/html")
    st.components.v1.html(html_final, height=800, scrolling=True)
else:
    st.info("💡 Filtre e selecione as questões para gerar o documento.")
