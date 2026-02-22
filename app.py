import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Avaliações Profissional", layout="wide", page_icon="📝")

# Função para converter imagem de upload em base64 (necessário para exibir no HTML)
def get_image_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
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

# 3. Navegação Lateral e Upload de Logo
st.sidebar.header("⚙️ Configurações Globais")
logo_upload = st.sidebar.file_uploader("Carregar Logo (Secretaria/Escola)", type=["png", "jpg", "jpeg"])
logo_b64 = get_image_base64(logo_upload)

MENU_BANCO = "🔍 Banco de Questões"
MENU_CADASTRO = "📝 Cadastrar Nova"
MENU_GERADOR = "📄 Gerador de Prova"
opcao = st.sidebar.radio("Navegar para:", [MENU_BANCO, MENU_CADASTRO, MENU_GERADOR])

# --- PÁGINA: BANCO DE QUESTÕES ---
if opcao == MENU_BANCO:
    st.header("📊 Visualização do Banco de Dados")
    st.dataframe(df, use_container_width=True)

# --- PÁGINA: CADASTRAR NOVA ---
elif opcao == MENU_CADASTRO:
    st.header("📝 Cadastrar Nova Questão")
    st.info("Formulário de cadastro rápido.")
    # (O código do formulário de cadastro permanece o mesmo dos anteriores)

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    with st.expander("🏫 Configurações da Instituição", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        nome_escola = col1.text_input("Nome da Instituição", "Secretaria Municipal de Educação de Fortaleza")
        valor_prova = col2.text_input("Pontuação Máxima", "10,0")
        num_quadrados = col3.number_input("Quadrados no Nome", 10, 40, 25)

    with st.expander("🎯 Filtros e Documento", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            sel_disc = st.multiselect("Disciplina", sorted(df['disciplina'].unique()))
            tipo_doc = st.selectbox("Tipo de Documento", ["Prova", "Atividade", "Simulado"])
        with f2:
            sel_tema = st.multiselect("Conteúdo", sorted(df[df['disciplina'].isin(sel_disc)]['conteudo'].unique()) if sel_disc else [])
            formato = st.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
        
        c_check1, c_check2 = st.columns(2)
        add_cartao = c_check1.checkbox("Adicionar Cartão-Resposta Profissional")
        add_gab_prof = c_check2.checkbox("Adicionar Gabarito do Professor")

    df_f = df.copy()
    if sel_disc: df_f = df_f[df_f['disciplina'].isin(sel_disc)]
    if sel_tema: df_f = df_f[df_f['conteudo'].isin(sel_tema)]
    
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    itens_selecionados = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if itens_selecionados:
        ids = [int(s.split(" | ")[0]) for s in itens_selecionados]
        df_prova = df[df['id'].isin(ids)].copy()

        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 80px;">' if logo_b64 else ""

        html_head = r"""
        <head>
            <meta charset='UTF-8'>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
            <style>
                body { font-family: 'Times New Roman', serif; font-size: 11pt; color: black; margin: 0; padding: 0; }
                .header-table { width: 100%; border: 2px solid black; border-collapse: collapse; margin-bottom: 20px; }
                .header-table td { border: 1px solid black; padding: 10px; vertical-align: middle; }
                .quest-box { margin-bottom: 20px; page-break-inside: avoid; }
                .name-grid { display: flex; margin-top: 5px; }
                .grid-square { width: 18px; height: 22px; border: 1px solid black; margin-right: -1px; }
                /* Estilo Cartão Resposta */
                .cartao-wrapper { page-break-before: always; border: 2px solid black; padding: 15px; }
                .cartao-row { display: flex; align-items: center; margin-bottom: 12px; }
                .opt-group { display: flex; flex-direction: column; align-items: center; margin-right: 15px; width: 25px; }
                .opt-letter { font-size: 8pt; font-weight: bold; margin-bottom: 2px; }
                .opt-circle { width: 18px; height: 18px; border: 1px solid black; border-radius: 50%; }
            </style>
        </head>
        """

        # Cabeçalho formatado
        cabecalho = f"""
        <table class="header-table">
            <tr>
                <td style="width: 20%; text-align: center;">{logo_html}</td>
                <td style="width: 60%; text-align: center;">
                    <h2 style="margin:0;">{tipo_doc.upper()}</h2>
                    <h3 style="margin:5px;">{nome_escola.upper()}</h3>
                </td>
                <td style="width: 20%; text-align: center;">
                    <b>NOTA</b><br><br>________
                </td>
            </tr>
            <tr>
                <td colspan="3">
                    ALUNO(A): <div class="name-grid">{"".join(['<div class="grid-square"></div>' for _ in range(num_quadrados)])}</div>
                    <div style="margin-top:10px;">DISCIPLINA: {", ".join(sel_disc).upper()} &nbsp;&nbsp;&nbsp; NÚMERO: [___] &nbsp;&nbsp;&nbsp; DATA: ___/___/___</div>
                </td>
            </tr>
        </table>
        """
        
        corpo = ""
        for i, row in df_prova.reset_index().iterrows():
            t_base = f"<i>{row['texto_base']}</i> " if pd.notna(row['texto_base']) and str(row['texto_base']).strip() != "" else ""
            corpo += f'<div class="quest-box"><b>QUESTÃO {i+1}</b> ({row["fonte"]})<br>{t_base}{row["comando"]}'
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                letras = ['A', 'B', 'C', 'D', 'E']
                corpo += "<ul>"
                for idx, alt in enumerate(alts):
                    if idx < 5: corpo += f"<li>{letras[idx]}) {alt.strip()}</li>"
                corpo += "</ul>"
            else:
                corpo += "<div style='border: 1px dashed #ccc; height: 120px; margin-top: 10px;'></div>"
            corpo += "</div>"

        # Cartão Resposta Estilo Máscara
        if add_cartao and formato == "Objetiva":
            corpo += f"""
            <div class="cartao-wrapper">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid black; padding-bottom: 10px; margin-bottom: 15px;">
                    {logo_html}
                    <div style="text-align: center;">
                        <h3 style="margin:0;">CARTÃO-RESPOSTA OFICIAL</h3>
                        <p style="margin:0; font-size: 10pt;">{nome_escola.upper()}</p>
                    </div>
                    <div style="width: 80px;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    NOME: <div class="name-grid">{"".join(['<div class="grid-square"></div>' for _ in range(num_quadrados)])}</div>
                </div>
            """
            for i in range(len(df_prova)):
                opts_html = "".join([f'<div class="opt-group"><span class="opt-letter">{l}</span><div class="opt-circle"></div></div>' for l in ['A', 'B', 'C', 'D', 'E']])
                corpo += f'<div class="cartao-row"><b>{str(i+1).zfill(2)}</b> &nbsp;&nbsp;&nbsp; {opts_html}</div>'
            corpo += "</div>"

        html_final = f"<!DOCTYPE html><html>{html_head}<body>{cabecalho}{corpo}</body></html>"
        
        st.download_button(label="📥 Baixar Documento Completo", data=html_final, file_name="avaliacao_formatada.html", mime="text/html")
        st.subheader("👁️ Pré-visualização")
        st.components.v1.html(html_final, height=800, scrolling=True)
