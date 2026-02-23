import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import io

# --- 1. FUNÇÕES AUXILIARES ---

def converter_link_drive(url):
    """Converte links do Google Drive para links de imagem direta."""
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
    """Converte arquivos de imagem carregados em Base64 para exibição no HTML."""
    if image_file:
        try:
            return base64.b64encode(image_file.getvalue()).decode()
        except: return None
    return None

def limpar_coluna(nome):
    """Padroniza nomes das colunas para evitar erros de acentuação."""
    n = str(nome).lower().strip()
    subs = {'á': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'ú': 'u', 'ç': 'c'}
    for k, v in subs.items(): n = n.replace(k, v)
    return n

# --- 2. CONFIGURAÇÕES VISUAIS (CSS) ---
CSS_ESTILOS = r"""
<style>
    body { font-family: 'Arial', sans-serif; font-size: 11pt; color: black; margin: 0; }
    .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 15px; }
    .header-table td { border: 1px solid black; padding: 8px; vertical-align: middle; }
    .quest-box { margin-bottom: 20px; page-break-inside: avoid; line-height: 1.4; }
    .texto-base { font-style: italic; display: block; margin-bottom: 8px; }
    .quest-img { display: block; margin: 10px auto; max-width: 70%; max-height: 280px; border: 1px solid #ddd; }
    
    /* Grid de Identificação */
    .grid-container { display: flex; margin-top: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .grid-box { width: 18px; height: 24px; border: 1.2px solid black; margin-right: -1.2px; display: inline-block; }
    
    /* Cartão Resposta */
    .cartao-page { page-break-before: always; border: 2px solid black; padding: 30px; margin-top: 20px; }
    .instrucoes-cartao { border: 1.5px solid black; padding: 15px; margin-bottom: 25px; font-size: 9pt; background-color: #fcfcfc; }
    .instrucoes-cartao p { margin: 3px 0; line-height: 1.2; }
    
    .columns-container { display: flex; flex-direction: row; flex-wrap: wrap; gap: 25px; justify-content: flex-start; }
    .column { display: flex; flex-direction: column; border: 1.5px solid #000; min-width: 220px; }
    .cartao-row { display: flex; align-items: center; height: 32px; border-bottom: 0.5px solid #ccc; }
    .q-num-col { width: 50px; font-weight: bold; text-align: center; border-right: 2.5px solid black; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 10pt; }
    .bubbles-col { display: flex; gap: 8px; padding: 0 10px; align-items: center; }
    .bubble-circle { width: 22px; height: 22px; border: 1.5px solid black; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 8pt; font-weight: bold; }
    
    .gabarito-section { page-break-before: always; border-top: 2px dashed black; padding-top: 20px; }
    .gabarito-grid { display: flex; flex-wrap: wrap; gap: 10px; }
    .gabarito-item { width: 100px; border: 1px solid #ccc; padding: 5px; text-align: center; }
    
    ul { list-style-type: none; padding-left: 0; }
    li { margin-bottom: 5px; }
    @media print { .no-print { display: none; } }
</style>
"""

MATHJAX_AND_PRINT = r"""
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$']] } };
</script>
"""

# --- 3. INÍCIO DO APP ---
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
    st.info("Para cadastrar, utilize a planilha diretamente no Google Drive por enquanto.")
    st.markdown("[Acesse a Planilha Aqui](https://docs.google.com/spreadsheets/d/1ndLQTjM2RQZliaiDs8zFU7r0_8tG2VJmYDXRyZ0Pe88/edit)")

with aba_gerar:
    with st.expander("🏫 Configurações da Instituição", expanded=True):
        c_tipo, c_nome, c_valor = st.columns([1.2, 3, 0.8])
        tipo_doc = c_tipo.selectbox("Tipo de Documento", ["AVALIAÇÃO", "ATIVIDADE", "SIMULADO", "RECUPERAÇÃO", "TESTE"])
        nome_inst = c_nome.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
        valor_total = c_valor.text_input("Valor Total", "10,0")
        
        col_img_1, col_img_2 = st.columns(2)
        l_sme = col_img_1.file_uploader("Logo Esquerda", type=["png", "jpg"])
        l_esc = col_img_2.file_uploader("Logo Direita", type=["png", "jpg"])
        sme_b64, esc_b64 = get_image_base64(l_sme), get_image_base64(l_esc)

    with st.expander("🎯 Filtros Gerais", expanded=True):
        f1, f2, f3 = st.columns(3)
        sel_disc = f1.multiselect("Disciplina", sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else [])
        df_f1 = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        sel_tema = f2.multiselect("Conteúdo", sorted(df_f1['conteudo'].unique()) if 'conteudo' in df_f1.columns else [])
        sel_dif = f3.multiselect("Dificuldade", ["Fácil", "Médio", "Difícil"])
        df_filter = df_f1[df_f1['conteudo'].isin(sel_tema)] if sel_tema else df_f1
        if sel_dif: df_filter = df_filter[df_filter['dificuldade'].isin(sel_dif)]
        
        c_check1, c_check2 = st.columns(2)
        add_cartao = c_check1.checkbox("Incluir Cartão-Resposta", value=True)
        add_gab = c_check2.checkbox("Incluir Gabarito", value=True)

    df_filter['label'] = df_filter['id'].astype(str) + " | " + df_filter['comando'].astype(str).str[:70] + "..."
    selecao = st.multiselect("Selecione as questões na ordem desejada:", options=df_filter['label'].tolist())

    if selecao:
        ids_selecionados = [int(s.split(" | ")[0]) for s in selecao]
        df_prova = df[df['id'].isin(ids_selecionados)].set_index('id').loc[ids_selecionados].reset_index()

        st.subheader("⚙️ Formato das Questões")
        formatos_escolhidos = []
        cols = st.columns(min(len(df_prova), 6))
        for idx, row in df_prova.iterrows():
            with cols[idx % 6]:
                default_idx = 0 if pd.notna(row.get('alternativas')) and str(row['alternativas']).strip() != "" else 1
                f = st.selectbox(f"Q{idx+1:02d}", ["Objetiva", "Subjetiva"], index=default_idx, key=f"f_{row['id']}")
                formatos_escolhidos.append(f)

        img_sme = f'<img src="data:image/png;base64,{sme_b64}" style="max-height: 60px;">' if sme_b64 else ""
        img_esc = f'<img src="data:image/png;base64,{esc_b64}" style="max-height: 60px;">' if esc_b64 else ""

        html_cabecalho = f"""
        <table class="header-table">
            <tr><td style="width:15%; text-align:center;">{img_sme}</td>
            <td style="text-align:center;"><h3>{nome_inst.upper()}</h3><b style="font-size:14pt;">{tipo_doc} DE {", ".join(sel_disc).upper()}</b></td>
            <td style="width:15%; text-align:center;">{img_esc}</td></tr>
            <tr><td colspan="2" style="padding: 25px 5px;"> ESTUDANTE: ____________________________________________________<br>
            <br> NÚMERO: [____] TURMA: [________] DATA: ___/___/___</td>
            <td style="text-align:center; font-weight:bold;">NOTA <br><br> ______/{valor_total}</td></tr>
        </table>"""

        html_corpo = ""
        for i, row in df_prova.iterrows():
            num = f"{i+1:02d}"
            t_base = f'<span class="texto-base">{row["texto_base"]}</span>' if pd.notna(row.get('texto_base')) else ""
            img_url = converter_link_drive(row['imagem']) if pd.notna(row.get('imagem')) else None
            img_tag = f'<img src="{img_url}" class="quest-img">' if img_url else ""
            
            html_corpo += f"""
            <div class="quest-box">
                <b>QUESTÃO {num}</b> ({row.get('fonte', 'Autor')})
                <div class="container-enunciado">{t_base}{img_tag}<div>{row['comando']}</div></div>"""
            
            if formatos_escolhidos[i] == "Objetiva":
                alts = str(row['alternativas']).split(';')
                html_corpo += "<ul>"
                for idx, alt in enumerate(alts):
                    if idx < 5: html_corpo += f"<li>{['A','B','C','D','E'][idx]}) {alt.strip()}</li>"
                html_corpo += "</ul>"
            else:
                html_corpo += "<div style='border:1px dashed #ccc; height:80px; margin-top:10px;'></div>"
            html_corpo += "</div>"

        if add_cartao:
            def grid(n): return "".join(['<div class="grid-box"></div>' for _ in range(n)])
            cartao_html = f"""
            <div class="cartao-page">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    {img_sme}<b style="font-size:16pt;">{tipo_doc} <br> <br> CARTÃO-RESPOSTA OFICIAL</b>{img_esc}
                </div>
                
                <div class="instrucoes-cartao">
                    <b>NORMAS DE PREENCHIMENTO:</b>
                    <p>● Utilize exclusivamente <b>caneta esferográfica azul ou preta</b>.</p>
                    <p>● Preencha <b>totalmente</b> o círculo correspondente à alternativa correta.</p>
                    <p>● Marque apenas <b>uma alternativa</b> por questão; rasuras invalidam a resposta.</p>
                    <p>● Não utilize corretivos e evite dobrar este cartão.</p>
                </div>

                <div style="margin-bottom: 35px;">
                    NOME COMPLETO DO ESTUDANTE:<br>
                    <div class="grid-container" style="margin-bottom:15px;">{grid(48)}</div>
                    <div style="display:flex; gap:25px;">
                        <div>NÚMERO: <div class="grid-container">{grid(3)}</div></div>
                        <div>TURMA: <div class="grid-container">{grid(8)}</div></div>
                        <div>DATA: <div class="grid-container">{grid(2)}/{grid(2)}/{grid(2)}</div></div>
                    </div>
                </div>
                <div class="columns-container">"""
            
            for c in range(0, len(df_prova), 12):
                cartao_html += '<div class="column"><div style="background:#eee; display:flex; font-weight:bold; border-bottom:1.5px solid #000; font-size: 7.5pt;"><div style="width:50px; text-align:center; border-right:1px solid #000;">QUESTÃO</div><div style="flex:1; text-align:center;">RESPOSTA</div></div>'
                for i in range(c, min(c + 12, len(df_prova))):
                    if formatos_escolhidos[i] == "Subjetiva":
                        bubbles = "<span style='font-size:7pt; color:#999;'>--- SUBJETIVA ---</span>"
                    else:
                        bubbles = "".join([f'<div class="bubble-circle">{l}</div>' for l in ['A','B','C','D','E']])
                    
                    cartao_html += f'<div class="cartao-row"><div class="q-num-col">{i+1:02d}</div><div class="bubbles-col">{bubbles}</div></div>'
                cartao_html += '</div>'
            
            cartao_html += """
                </div>
                <div style="margin-top: 70px; display: flex; justify-content: flex-end;">
                    <div style="border-top: 1.5px solid #000; width: 380px; text-align: center; padding-top: 5px; font-size: 9pt; font-weight: bold;">
                        ASSINATURA DO ESTUDANTE
                    </div>
                </div>
            </div>"""
            html_corpo += cartao_html

        if add_gab:
            html_corpo += '<div class="gabarito-section"><h3>GABARITO OFICIAL</h3><div class="gabarito-grid">'
            for i, row in df_prova.iterrows():
                val = row.get("gabarito", "-") if formatos_escolhidos[i] == "Objetiva" else "SUBJ."
                html_corpo += f'<div class="gabarito-item">Q{i+1:02d}: <b>{val}</b></div>'
            html_corpo += '</div></div>'

        btn_print = '<div class="no-print" style="text-align:center; margin:20px;"><button onclick="window.print()" style="padding:15px 30px; background:#4CAF50; color:white; border:none; border-radius:8px; cursor:pointer; font-size:16px;">🖨️ Imprimir / Salvar PDF</button></div>'
        st.components.v1.html(f"<html>{MATHJAX_AND_PRINT}{CSS_ESTILOS}<body>{btn_print}{html_cabecalho}{html_corpo}</body></html>", height=900, scrolling=True)
