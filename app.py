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

    with st.expander("⚙️ Configurações do Cabeçalho e Instituição", expanded=True):
        col_inst1, col_inst2 = st.columns(2)
        nome_escola = col_inst1.text_input("Nome da Instituição/Escola", "IFCE - Campus Fortaleza")
        valor_prova = col_inst2.text_input("Valor total da prova (ex: 10,0)", "10,0")

    with st.expander("🎯 Filtros e Formatação", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina", disciplinas)
            tipo_doc = st.selectbox("Tipo de Atividade", ["Prova", "Atividade", "Simulado"])
        
        df_f = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        
        with f2:
            temas = sorted(df_f['conteudo'].unique()) if 'conteudo' in df_f.columns else []
            sel_tema = st.multiselect("Conteúdo/Tema", temas)
            formato = st.radio("Formato das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
        
        st.write("---")
        col_check1, col_check2 = st.columns(2)
        add_cartao_resposta = col_check1.checkbox("Adicionar Cartão-Resposta (Círculos)")
        add_gabarito_respostas = col_check2.checkbox("Adicionar Gabarito (Respostas Corretas)")

    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecionadas = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

    if selecionadas:
        ids = [int(s.split(" | ")[0]) for s in selecionadas]
        df_prova = df[df['id'].isin(ids)].copy()

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
                .quest-box { margin-bottom: 20px; page-break-inside: avoid; }
                .header { border: 2px solid black; padding: 10px; text-align: center; margin-bottom: 20px; position: relative; }
                .nota-box { position: absolute; top: 10px; right: 10px; border: 1px solid black; padding: 5px 15px; text-align: center; }
                .circle { border: 1px solid black; border-radius: 50%; width: 18px; height: 18px; display: inline-block; text-align: center; font-size: 10pt; margin-right: 5px; }
                ul { list-style-type: none; padding-left: 20px; margin-top: 5px; }
                li { margin-bottom: 3px; }
            </style>
        </head>
        """

        nota_html = f"<div class='nota-box'>NOTA<br><br>____ / {valor_prova}</div>" if tipo_doc == "Prova" else ""
        
        cabecalho = f"""
        <div class="header">
            {nota_html}
            <h2 style="margin:0;">{tipo_doc.upper()} DE {", ".join(sel_disc).upper() if sel_disc else "CONTEÚDO"}</h2>
            <p style="margin:5px; font-weight: bold;">{nome_escola.upper()}</p>
            <div style="text-align: left; margin-top: 15px;">
                ALUNO(A): _________________________________________________ TURMA: ________ DATA: ___/___/___
            </div>
        </div>
        """
        
        corpo = ""
        for i, row in df_prova.reset_index().iterrows():
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
                    if idx < 5: corpo += f"<li>{letras[idx]}) {alt.strip()}</li>"
                corpo += "</ul>"
            else:
                corpo += "<div style='border: 1px dashed #ccc; height: 160px; margin-top: 10px;'></div>"
            corpo += "</div>"

        # Cartão Resposta (Círculos estilo IFCE)
        if add_cartao_resposta and formato == "Objetiva":
            corpo += "<div style='page-break-before: always; border: 1px solid black; padding: 15px;'>"
            corpo += f"<h3 style='text-align:center; margin-top:0;'>CARTÃO-RESPOSTA: {nome_escola.upper()}</h3>"
            corpo += "<p style='font-size: 9pt; text-align:center;'>Use caneta azul ou preta. Preencha totalmente o círculo da alternativa correta.</p>"
            for i in range(len(df_prova)):
                letras_row = "".join([f"<span class='circle'>{l}</span> " for l in ['A', 'B', 'C', 'D', 'E']])
                corpo += f"<div style='margin-bottom: 8px;'><b>{str(i+1).zfill(2)}</b> &nbsp;&nbsp; {letras_row}</div>"
            corpo += "</div>"

        # Gabarito de Respostas (Para o Professor)
        if add_gabarito_respostas:
            corpo += "<div style='page-break-before: always;'>"
            corpo += "<h3>GABARITO OFICIAL (PROFESSOR)</h3><table border='1' style='width:100%; border-collapse:collapse; text-align:center;'>"
            corpo += "<tr><th>Questão</th><th>Gabarito</th></tr>"
            for i, row in df_prova.reset_index().iterrows():
                corpo += f"<tr><td>{i+1}</td><td>{row.get('gabarito', 'N/A')}</td></tr>"
            corpo += "</table></div>"

        html_final = f"<!DOCTYPE html><html>{html_head}<body>{cabecalho}{corpo}</body></html>"
        
        st.download_button("📥 Baixar Documento", data=html_final, file_
