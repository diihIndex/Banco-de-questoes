import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- 1. FUNÇÕES AUXILIARES ---

def converter_link_drive(url):
    url = str(url).strip()
    if 'drive.google.com' in url:
        try:
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
                return f'https://lh3.googleusercontent.com/u/0/d/{file_id}'
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
                return f'https://lh3.googleusercontent.com/u/0/d/{file_id}'
        except Exception: return url
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
    body { font-family: 'Arial', sans-serif; font-size: 12pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 15px; }
    .header-table td { border: 1px solid black; padding: 8px; vertical-align: middle; }
    
    .quest-box { margin-bottom: 20px; page-break-inside: avoid; line-height: 1.3; }
    
    /* AJUSTE DE FLUXO CONTÍNUO */
    .texto-base { font-style: italic; display: inline; }
    .comando-questao { display: inline; margin-left: 5px; }
    .container-enunciado { margin-top: 5px; }
    
    .quest-img { display: block; margin: 10px auto; max-width: 70%; max-height: 280px; border: 1px solid #ddd; }
    
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 26px; height: 32px; border: 1.5px solid black; margin-right: -1.5px; display: inline-block; }
    
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 30px; margin-top: 20px; }
    .instrucoes-cartao { border: 1.5px solid black; padding: 15px; margin-bottom: 25px; font-size: 9pt; background-color: #fcfcfc; }
    .instrucoes-cartao p { margin: 3px 0; line-height: 1.2; }
    
    .cartao-identificacao { margin-bottom: 40px; } 
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 25px; justify-content: flex-start; }
    .column { display: flex; flex-direction: column; border: 1.5px solid #000; min-width: 220px; }
    .cartao-header-row { background-color: #eee; display: flex; font-size: 7.5pt; font-weight: bold; border-bottom: 1.5px solid #000; }
    .cartao-row { display: flex; align-items: center; height: 32px; border-bottom: 0.5px solid #ccc; }
    .q-num-col { width: 50px; font-weight: bold; text-align: center; border-right: 2.5px solid black; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 10pt; }
    .bubbles-col { display: flex; gap: 8px; padding: 0 10px; align-items: center; }
    .bubble-circle { width: 22px; height: 22px; border: 1.5px solid black; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 8pt; font-weight: bold; }
    
    .assinatura-container { margin-top: 70px; display: flex; justify-content: flex-end; }
    .assinatura-box { border-top: 1.5px solid #000; width: 380px; text-align: center; padding-top: 5px; font-size: 9pt; font-weight: bold; }

    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; margin-top: 30px; }
    .gabarito-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .gabarito-item { width: 90px; border: 1px solid #ccc; padding: 4px; text-align: center; font-size: 9pt; }

    ul { list-style-type: none; padding-left: 0; margin-top: 5px; }
    li { margin-bottom: 4px; }
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
        url_img_cad = st.text_input("Link da Imagem")
        comando_cad = st.text_area("Comando")
        alts_cad = st.text_input("Alternativas (A;B;C;D;E)")
        gab_cad = st.text_input("Gabarito")
        if st.form_submit_button("Salvar"): st.info("Adicione os dados na planilha!")

with aba_gerar:
    with st.expander("🏫 Configurações da Instituição", expanded=True):
        c_nome, c_valor = st.columns([3, 1])
        nome_inst = c_nome.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
        valor_total = c_valor.text_input("Valor Total", "10,0")
        col_img_1, col_img_2 = st.columns(2)
        l_sme = col_img_1.file_uploader("Logo Esquerda", type=["png", "jpg"])
        l_esc = col_img_2.file_uploader("Logo Direita", type=["png", "jpg"])
        sme_b64, esc_b64 = get_image_base64(l_sme), get_image_base64(l_esc)

    with st.expander("🎯 Filtros e Estilo", expanded=True):
        f1, f2, f3 = st.columns(3)
        sel_disc = f1.multiselect("Disciplina", sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else [])
        df_f1 = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        sel_tema = f2.multiselect("Conteúdo", sorted(df_f1['conteudo'].unique()) if 'conteudo' in df_f1.columns else [])
        sel_dif = f3.multiselect("Dificuldade", ["Fácil", "Médio", "Difícil"])
        df_filter = df_f1[df_f1['conteudo'].isin(sel_tema)] if sel_tema else df_f1
        if sel_dif: df_filter = df_filter[df_filter['dificuldade'].isin(sel_dif)]
        formato = st.radio("Estilo das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
        add_cartao, add_gab = st.checkbox("Incluir Cartão-Resposta", value=True), st.checkbox("Incluir Gabarito", value=True)

    df_filter['label'] = df_filter['id'].astype(str) + " | " + df_filter['comando'].astype(str).str[:70] + "..."
    selecao = st.multiselect("Selecione as questões:", options=df_filter['label'].tolist())

    if selecao:
        ids = [int(s.split(" | ")[0]) for s in selecao]
        df_prova = df[df['id'].isin(ids)].copy()
        img_sme = f'<img src="data:image/png;base64,{sme_b64}" style="max-height: 60px;">' if sme_b64 else ""
        img_esc = f'<img src="data:image/png;base64,{esc_b64}" style="max-height: 60px;">' if esc_b64 else ""

        html_cabecalho = f"""
        <table class="header-table">
            <tr><td style="width:15%; text-align:center;">{img_sme}</td>
            <td style="text-align:center;"><h3>{nome_inst.upper()}</h3><b>PROVA DE {", ".join(sel_disc).upper()}</b></td>
            <td style="width:15%; text-align:center;">{img_esc}</td></tr>
            <br>
            <tr><td colspan="2"> ESTUDANTE: ____________________________________________________<br>
            <br>
            NÚMERO: [____] TURMA: [________] DATA: ___/___/___</td>
            <td class="nota-cell">NOTA: ______/{valor_total}</td></tr>
        </table>"""

        html_corpo = ""
        for i, row in df_prova.reset_index().iterrows():
            ano = f" - {row['ano']}" if pd.notna(row.get('ano')) else ""
            t_base_content = str(row.get('texto_base', '')).strip()
            t_base_html = f'<span class="texto-base">{t_base_content}</span>' if t_base_content else ""
            
            img_tag = ""
            if 'imagem' in row and pd.notna(row['imagem']) and str(row['imagem']).strip() != "":
                link_convertido = converter_link_drive(str(row['imagem']))
                img_tag = f'<img src="{link_convertido}" class="quest-img">'
            
            comando_html = f'<span class="comando-questao">{row["comando"]}</span>'
            
            # Montagem compacta do enunciado
            html_corpo += f"""
            <div class="quest-box">
                <b>QUESTÃO {i+1}</b> ({row["fonte"]}{ano})
                <div class="container-enunciado">
                    {t_base_html}
                    {img_tag if img_tag else ""}
                    {comando_html}
                </div>
            """
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                html_corpo += "<ul>"
                for idx, alt in enumerate(alts):
                    if idx < 5: html_corpo += f"<li>{['A','B','C','D','E'][idx]}) {alt.strip()}</li>"
                html_corpo += "</ul>"
            else: html_corpo += "<div style='border:1px dashed #ccc; height:100px; margin-top:10px;'></div>"
            html_corpo += "</div>"

        if add_cartao and formato == "Objetiva":
            def grid(n): return "".join(['<div class="grid-box"></div>' for _ in range(n)])
            cartao_html = f'<div class="cartao-page"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">{img_sme}<b style="font-size:14pt;">CARTÃO-RESPOSTA OFICIAL</b>{img_esc}</div>'
            cartao_html += """<div class="instrucoes-cartao"><b>NORMAS DE PREENCHIMENTO:</b>
                <p>● Utilize exclusivamente <b>caneta esferográfica azul ou preta</b>.</p>
                <p>● Preencha <b>totalmente</b> o círculo correspondente à alternativa correta.</p>
                <p>● Marque apenas <b>uma alternativa</b> por questão; rasuras invalidam a resposta.</p>
                <p>● Não utilize corretivos e evite dobrar este cartão.</p></div>"""
            cartao_html += f'<div class="cartao-identificacao">NOME COMPLETO DO ESTUDANTE:<br><div class="grid-container">{grid(48)}</div>NÚMERO: {grid(2)} &nbsp;&nbsp;&nbsp;&nbsp; TURMA: {grid(6)} &nbsp;&nbsp;&nbsp;&nbsp; DATA: {grid(2)}/{grid(2)}/{grid(2)}</div>'
            cartao_html += '<div class="columns-container">'
            num_q = len(df_prova)
            for c in range(0, num_q, 12):
                cartao_html += '<div class="column"><div class="cartao-header-row"><div style="width:50px; text-align:center; border-right:1px solid #000;">QUESTÃO</div><div style="flex:1; text-align:center;">RESPOSTA</div></div>'
                for i in range(c, min(c + 12, num_q)):
                    bubbles = "".join([f'<div class="bubble-circle">{l}</div>' for l in ['A','B','C','D','E']])
                    cartao_html += f'<div class="cartao-row"><div class="q-num-col">{i+1:02d}</div><div class="bubbles-col">{bubbles}</div></div>'
                cartao_html += '</div>'
            cartao_html += '</div><div class="assinatura-container"><div class="assinatura-box">ASSINATURA DO ESTUDANTE</div></div></div>'
            html_corpo += cartao_html

        if add_gab:
            html_corpo += '<div class="gabarito-section"><h3>GABARITO</h3><div class="gabarito-grid">'
            for i, row in df_prova.reset_index().iterrows():
                html_corpo += f'<div class="gabarito-item">Q{i+1:02d}: <b>{row.get("gabarito"," ")}</b></div>'
            html_corpo += '</div></div>'

        btn = '<div class="no-print" style="text-align:center; margin:20px;"><button onclick="window.print()" style="padding:10px 20px; background:#4CAF50; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🖨️ Gerar Documento de Impressão</button></div>'
        html_final = f"<!DOCTYPE html><html>{MATHJAX_AND_PRINT}{CSS_ESTILOS}<body>{btn}{html_cabecalho}{html_corpo}</body></html>"
        st.components.v1.html(html_final, height=800, scrolling=True)
