import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Avaliações SME", layout="wide", page_icon="📝")

# Função para converter imagem em base64
def get_image_base64(image_file):
    if image_file is not None:
        try:
            return base64.b64encode(image_file.getvalue()).decode()
        except:
            return None
    return None

# 2. Conexão e Dados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    df.columns = [str(c).lower().strip().replace('ú', 'u').replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('é', 'e') for c in df.columns]
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# 3. Sidebar: Configurações e Logos
st.sidebar.header("🖼️ Identificação Visual")
logo_sme_file = st.sidebar.file_uploader("Logo Prefeitura/SME (Esquerda)", type=["png", "jpg", "jpeg"])
logo_esc_file = st.sidebar.file_uploader("Logo da Escola (Direita)", type=["png", "jpg", "jpeg"])

sme_b64 = get_image_base64(logo_sme_file)
esc_b64 = get_image_base64(logo_esc_file)

MENU_GERADOR = "📄 Gerador de Prova"
opcao = st.sidebar.radio("Navegar para:", [MENU_GERADOR])

if opcao == MENU_GERADOR:
    st.header("📄 Gerador de Avaliações Profissionais")
    
    with st.expander("🏫 Dados do Cabeçalho", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        nome_inst = col1.text_input("Nome da Escola", "Escola Municipal Cônego Francisco Pereira da Silva")
        valor_prova = col2.text_input("Valor da Prova", "10,0")
        num_quadrados = col3.number_input("Quadrados p/ Nome", 10, 50, 30)

    with st.expander("🎯 Filtros de Conteúdo", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina(s)", disciplinas)
            tipo_doc = st.selectbox("Tipo de Material", ["Prova", "Atividade", "Simulado"])
        with f2:
            df_filter = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
            temas = sorted(df_filter['conteudo'].unique()) if 'conteudo' in df_filter.columns else []
            sel_tema = st.multiselect("Conteúdo Específico", temas)
            formato = st.radio("Tipo de Questão", ["Objetiva", "Subjetiva"], horizontal=True)
        
        st.write("---")
        c_check1, c_check2 = st.columns(2)
        add_cartao = c_check1.checkbox("Incluir Cartão-Resposta (Máscara)")
        add_gab = c_check2.checkbox("Incluir Gabarito p/ Professor")

    # Filtragem Final e Seleção
    df_f = df_filter[df_filter['conteudo'].isin(sel_tema)] if sel_tema else df_filter
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecao = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if selecao:
        ids = [int(s.split(" | ")[0]) for s in selecao]
        df_prova = df[df['id'].isin(ids)].copy()

        # Definição do Header HTML
        html_head = r"""
        <head>
            <meta charset='UTF-8'>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
            <style>
                body { font-family: 'Arial', sans-serif; font-size: 10pt; color: black; margin: 0; }
                .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
                .header-table td { border: 1px solid black; padding: 8px; vertical-align: middle; }
                .grid-container { display: flex; margin-top: 4px; }
                .grid-box { width: 16px; height: 20px; border: 1px solid black; margin-right: -1px; }
                .quest-box { margin-bottom: 20px; page-break-inside: avoid; }
                .cartao-page { page-break-before: always; border: 2px solid black; padding: 25px; }
                .instrucoes { font-size: 8.5pt; border: 1px solid black; padding: 10px; margin-bottom: 15px; line-height: 1.4; }
                .cartao-row { display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
                .bubble-group { display: flex; flex-direction: column; align-items: center; margin: 0 8px; }
                .bubble-letter { font-size: 8pt; font-weight: bold; margin-bottom: 2px; }
                .bubble-circle { width: 18px; height: 18px; border: 1.5px solid black; border-radius: 50%; }
                .nota-cell { background: #eee; text-align: center; font-weight: bold; width: 90px; }
            </style>
        </head>
        """

        img_sme = f'<img src="data:image/png;base64,{sme_b64}" style="max-height: 70px;">' if sme_b64 else ""
        img_esc = f'<img src="data:image/png;base64,{esc_b64}" style="max-height: 70px;">' if esc_b64 else ""

        # Cabeçalho do Documento
        cabecalho = f"""
        <table class="header-table">
            <tr>
                <td style="width: 15%; text-align: center;">{img_sme}</td>
                <td style="width: 70%; text-align: center;">
                    <h3 style="margin:0;">{nome_inst.upper()}</h3>
                    <p style="margin:4px;"><b>{tipo_doc.upper()} - {", ".join(sel_disc).upper()}</b></p>
                </td>
                <td class="nota-cell">NOTA<br><br>______</td>
            </tr>
            <tr>
                <td colspan="3">
                    NOME COMPLETO:<br>
                    <div class="grid-container">{"".join(['<div class="grid-box"></div>' for _ in range(num_quadrados)])}</div>
                    <div style="margin-top:10px; display: flex; justify-content: space-between;">
                        <span>Nº: [_____]</span> <span>TURMA: [_________]</span> <span>DATA: ____/____/____</span>
                    </div>
                </td>
            </tr>
        </table>
        """

        corpo = ""
        for i, row in df_prova.reset_index().iterrows():
            t_base = f"<i>{row['texto_base']}</i> " if pd.notna(row['texto_base']) and str(row['texto_base']).strip() != "" else ""
            # Correção da string do corpo
            corpo += f"""
            <div class="quest-box">
                <b>QUESTÃO {i+1}</b> ({row['fonte']})<br>
                {t_base}{row['comando']}
            """
            
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                letras = ['A', 'B', 'C', 'D', 'E']
                corpo += "<ul style='list-style-type: none; padding-left: 20px;'>"
                for idx, alt in enumerate(alts):
                    if idx < len(letras):
                        corpo += f"<li style='margin-bottom:4px;'>{letras[idx]}) {alt.strip()}</li>"
                corpo += "</ul>"
            else:
                corpo += "<div style='border: 1px dashed #ccc; height: 140px; margin-top: 10px;'></div>"
            
            corpo += "</div>"

        # Cartão Resposta Formato Máscara
        if add_cartao and formato == "Objetiva":
            corpo += f"""
            <div class="cartao-page">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    {img_sme}
                    <div style="text-align: center;"><b>CARTÃO-RESPOSTA OFICIAL</b><br><small>{nome_inst}</small></div>
                    {img_esc}
                </div>
                <div class="instrucoes">
                    <b>INSTRUÇÕES PARA O PREENCHIMENTO:</b><br>
                    • Use caneta esferográfica preta ou azul (preferencialmente preta).<br>
                    • Preencha o círculo da alternativa escolhida <b>completamente</b> e com nitidez.<br>
                    • Não serão aceitas marcações rasuradas ou com uso de corretivo.
                </div>
                NOME COMPLETO DO ESTUDANTE:<br>
                <div class="grid-container" style="margin-bottom:12px;">{"".join(['<div class="grid-box"></div>' for _ in range(num_quadrados)])}</div>
                Nº: [_____] TURMA: [_________] DATA: ____/____/____
                <hr style="margin: 20px 0; border: 1px solid black;">
            """
            for i in range(len(df_prova)):
                bubbles = "".join([f'<div class="bubble-group"><span class="bubble-letter">{l}</span><div class="bubble-circle"></div></div>' for l in ['A', 'B', 'C', 'D', 'E']])
                corpo += f'<div class="cartao-row"><b style="width: 40px; font-size: 10pt;">{str(i+1).zfill(2)}</b> {bubbles}</div>'
            corpo += "</div>"

        # Gabarito Final
        if add_gab:
            corpo += "<div style='page-break-before: always;'><h3>GABARITO DE RESPOSTAS</h3>"
            for i, row in df_prova.reset_index().iterrows():
                corpo += f"Questão {i+1}: <b>{row.get('gabarito', 'S/G')}</b><br>"
            corpo += "</div>"

        html_final = f"<!DOCTYPE html><html>{html_head}<body>{cabecalho}{corpo}</body></html>"
        
        st.download_button(label="📥 Baixar Material Completo", data=html_final, file_name="avaliacao_sme.html", mime="text/html")
        st.subheader("👁️ Pré-visualização")
        st.components.v1.html(html_final, height=800, scrolling=True)
