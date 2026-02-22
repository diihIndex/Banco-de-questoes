import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Avaliações IFCE", layout="wide", page_icon="📝")

# 2. Conexão e Dados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    
    # Normalização de colunas
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
            disc_filter = st.multiselect("Filtrar por disciplina:", sorted(df['disciplina'].unique()))
            df_view = df[df['disciplina'].isin(disc_filter)] if disc_filter else df
            st.dataframe(df_view, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# --- PÁGINA: CADASTRAR NOVA ---
elif opcao == MENU_CADASTRO:
    st.header("📝 Cadastrar Nova Questão")
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
        
        if st.form_submit_button("Gerar Linha para Planilha"):
            st.code(f"{nova_disc}\t{nova_fonte}\t{novo_tema}\t{novo_texto_base}\t{novo_comando}\t{novas_alts}\t{novo_gab}")

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    if 'comando' not in df.columns:
        st.error("Coluna 'comando' não encontrada!")
        st.stop()

    with st.expander("⚙️ Configurações e Filtros", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina", disciplinas)
            tipo_doc = st.selectbox("Tipo de Cabeçalho", ["Prova", "Atividade"])
        
        df_f = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        
        with f2:
            temas = sorted(df_f['conteudo'].unique()) if 'conteudo' in df_f.columns else []
            sel_tema = st.multiselect("Conteúdo/Tema", temas)
            formato = st.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
        
        add_gabarito = st.checkbox("Incluir Folha de Respostas")

    # Seleção de Itens
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecionadas = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if selecionadas:
        ids = [int(s.split(" | ")[0]) for s in selecionadas]
        df_prova = df[df['id'].isin(ids)].copy()

        # HTML Head com configuração explícita do MathJax
        html_head = """
        <head>
            <meta charset='UTF-8'>
            <script>
            window.MathJax = {
              tex: {
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true
              },
              options: {
                renderAtStart: true
              }
            };
            </script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
            <style>
                body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; color: black; }
                .quest-box { margin-bottom: 25px; page-break-inside: avoid; }
                .header { border: 2px solid black; padding: 15px; text-align: center; margin-bottom: 25px; }
                ul { list-style-type: none; padding-left: 20px; margin-top: 10px; }
                li { margin-bottom: 5px; }
            </style>
        </head>
        """

        cabecalho = f"""
        <div class="header">
            <h2 style="margin:0;">{tipo_doc.upper()} DE {", ".join(sel_disc).upper() if sel_disc else "CONTEÚDO"}</h2>
            <p style="margin:5px;">INSTITUTO FEDERAL DO CEARÁ</p>
            <div style="text-align: left; margin-top: 20px;">
                NOME: _________________________________________________ TURMA: ________ DATA: ___/___/___
            </div>
        </div>
        """
        
        corpo = ""
        for i, row in df_prova.reset_index().iterrows():
            # Texto base e comando sem quebra de linha (na mesma linha)
            t_base = f"<i>{row['texto_base']}</i> " if pd.notna(row['texto_base']) and str(row['texto_base']).strip() != "" else ""
            
            corpo += f"""
            <div class="quest-box">
                <b>QUESTÃO {i+1}</b> ({row['fonte']})<br>
                {t_base}{row['comando']}
            """
            
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                letras = ['A', 'B', 'C', 'D', 'E']
                corpo += "<ul>"
                for idx, alt in enumerate(alts):
                    if idx < 5:
                        corpo += f"<li>{letras[idx]}) {alt.strip()}</li>"
                corpo += "</ul>"
            else:
                corpo += "<div style='border: 1px dashed #ccc; height: 160px; margin-top: 15px;'></div>"
            
            corpo += "</div>"

        if add_gabarito:
            corpo += "<div style='page-break-before: always; border-top: 2px solid black; padding-top: 20px;'>"
            corpo += "<h3 style='text-align:center;'>FOLHA DE RESPOSTAS</h3>"
            for i in range(len(df_prova)):
                corpo += f"<p><b>{i+1}:</b> ( A ) ( B ) ( C ) ( D ) ( E )</p>"
            corpo += "</div>"

        html_final = f"<!DOCTYPE html><html>{html_head}<body>{cabecalho}{corpo}</body></html>"
        
        st.download_button("📥 Baixar Material", data=html_final, file_name="material_ifce.html", mime="text/html")
        st.subheader("👁️ Pré-visualização")
        st.components.v1.html(html_final, height=800, scrolling=True)
