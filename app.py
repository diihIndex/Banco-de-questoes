import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Avaliações", layout="wide", page_icon="📝")

# 2. Conexão e Dados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    
    # Normalização de colunas (converte para minúsculo e remove acentos)
    df.columns = [
        str(c).lower().strip()
        .replace('ú', 'u').replace('ê', 'e').replace('ã', 'a')
        .replace('ç', 'c').replace('í', 'i').replace('é', 'e') 
        for c in df.columns
    ]
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# 3. Navegação Lateral
MENU_BANCO = "🔍 Banco de Questões"
MENU_CADASTRO = "📝 Cadastrar Nova"
MENU_GERADOR = "📄 Gerador de Prova"

opcao = st.sidebar.radio("Navegar para:", [MENU_BANCO, MENU_CADASTRO, MENU_GERADOR])

# --- PÁGINA: BANCO DE QUESTÕES ---
if opcao == MENU_BANCO:
    st.header("📊 Visualização do Banco de Dados")
    if not df.empty:
        if 'disciplina' in df.columns:
            disc_filter = st.multiselect("Filtrar visualização por disciplina:", sorted(df['disciplina'].unique()))
            df_view = df[df['disciplina'].isin(disc_filter)] if disc_filter else df
            st.dataframe(df_view, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# --- PÁGINA: CADASTRAR NOVA ---
elif opcao == MENU_CADASTRO:
    st.header("📝 Cadastrar Nova Questão")
    st.info("Preencha os campos abaixo para gerar a linha de dados.")
    with st.form("form_cadastro"):
        c1, c2 = st.columns(2)
        with c1:
            nova_disc = st.selectbox("Disciplina", ["Matemática", "Física", "Química", "Biologia", "Geografia", "História", "Português"])
            nova_fonte = st.text_input("Fonte")
        with c2:
            novo_tema = st.text_input("Conteúdo/Tema")
            nova_dif = st.select_slider("Dificuldade", ["Fácil", "Média", "Difícil"])
        
        novo_texto_base = st.text_area("Texto Base")
        novo_comando = st.text_area("Comando da Questão")
        novas_alts = st.text_input("Alternativas (separar por ';')")
        novo_gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Gerar Código para Planilha"):
            st.code(f"{nova_disc}\t{nova_fonte}\t{novo_tema}\t{novo_texto_base}\t{novo_comando}\t{novas_alts}\t{novo_gab}")

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    if 'comando' not in df.columns:
        st.error("Coluna 'comando' não encontrada na planilha!")
        st.stop()

    with st.expander("🏫 1. Configurações da Instituição", expanded=True):
        col_inst1, col_inst2 = st.columns(2)
        nome_escola = col_inst1.text_input("Nome da Escola/Instituição", "Nome da Sua Escola")
        valor_prova = col_inst2.text_input("Valor total da prova (ex: 10,0)", "10,0")

    with st.expander("⚙️ 2. Filtros e Formatação", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina", disciplinas)
            tipo_doc = st.selectbox("Tipo de Documento", ["Prova", "Atividade", "Simulado"])
        
        df_f = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        
        with f2:
            temas = sorted(df_f['conteudo'].unique()) if 'conteudo' in df_f.columns else []
            sel_tema = st.multiselect("Conteúdo/Tema", temas)
            formato = st.radio("Formato das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
        
        st.write("---")
        c_check1, c_check2 = st.columns(2)
        add_cartao = c_check1.checkbox("Adicionar Cartão-Resposta (Círculos)")
        add_gab_prof = c_check2.checkbox("Adicionar Gabarito do Professor")

    # Seleção de Itens
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    itens_selecionados = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if itens_selecionados:
        ids = [int(s.split(" | ")[0]) for s in itens_selecionados]
        df_prova = df[df['id'].isin(ids)].copy()

        # HTML Head com MathJax para LaTeX
        html_head = r"""
        <head>
            <meta charset='UTF-8'>
            <script>
            window.MathJax = {
              tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], processEscapes: true }
            };
            </script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
            <style>
                body { font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.3; color: black; }
                .header { border: 2px solid black; padding: 10px; text-align: center; margin-bottom: 20px; position: relative; }
                .nota-box { position: absolute; top: 10px; right: 10px; border: 1px solid black; padding: 5px 15px; text-align: center; }
                .quest-box { margin-bottom: 20px; page-break-inside: avoid; }
                .circle { border: 1px solid black; border-radius: 50%; width: 18px; height: 18px; display: inline-block; text-align: center; font-size: 10pt; margin-right: 5px; line-height: 18px; }
                ul { list-style-type: none; padding-left: 20px; margin-top: 5px; }
                li { margin-bottom: 3px; }
                .cartao-container { border: 1px solid black; padding: 15px; margin-top: 30px; page-break-before: always; }
            </style>
        </head>
        """

        nota_html = f"<div class='nota-box'>NOTA<br><br>____ / {valor_prova}</div>" if tipo_doc == "Prova" else ""
        
        cabecalho = f"""
        <div class="header">
            {nota_html}
            <h2 style="margin:0;">{tipo_doc.upper()} DE {", ".join(sel_disc).upper() if sel_disc else "CONTEÚDO
