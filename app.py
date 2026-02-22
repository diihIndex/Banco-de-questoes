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
        # Filtro rápido na visualização
        if 'disciplina' in df.columns:
            disc_filter = st.multiselect("Filtrar visualização por disciplina:", sorted(df['disciplina'].unique()))
            if disc_filter:
                st.dataframe(df[df['disciplina'].isin(disc_filter)], use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("A planilha está vazia.")

# --- PÁGINA: CADASTRAR NOVA ---
elif opcao == MENU_CADASTRO:
    st.header("📝 Cadastrar Nova Questão")
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            nova_disc = st.selectbox("Disciplina", ["Matemática", "Física", "Química", "Biologia", "Geografia", "História", "Português"])
            nova_fonte = st.text_input("Fonte (Ex: IFCE Fortaleza)")
            novo_ano = st.text_input("Ano (Ex: 2026.1)")
        with col2:
            novo_tema = st.text_input("Conteúdo/Tema")
            nova_dif = st.select_slider("Dificuldade", ["Fácil", "Média", "Difícil"])
        
        novo_texto_base = st.text_area("Texto Base (Opcional)")
        novo_comando = st.text_area("Comando da Questão (Enunciado)")
        novas_alts = st.text_input("Alternativas (separadas por ponto e vírgula ';')")
        novo_gabarito = st.text_input("Gabarito (Letra ou resposta)")
        
        btn_salvar = st.form_submit_button("Salvar na Planilha")
        if btn_salvar:
            st.warning("Para salvar, integre a função de escrita do GSheets ou copie os dados abaixo para sua planilha.")
            st.code(f"{nova_disc} | {nova_fonte} | {novo_ano} | {novo_tema} | {novo_comando}")

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    # Validação da coluna 'comando'
    if 'comando' not in df.columns:
        st.error("Erro: A coluna 'comando' não foi encontrada. Verifique se ela está escrita corretamente na planilha.")
        st.stop()

    # --- CONFIGURAÇÃO E FILTROS ---
    with st.expander("⚙️ 1. Configurações e Filtros", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            tipo_doc = st.selectbox("Cabeçalho", ["Prova", "Atividade"])
            formato = st.radio("Formato", ["Objetiva", "Subjetiva"], horizontal=True)
        with c2:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            f_disc = st.multiselect("Filtrar Disciplina", disciplinas)
            temas = sorted(df[df['disciplina'].isin(f_disc)]['conteudo'].unique()) if f_disc else sorted(df['conteudo'].unique())
            f_tema = st.multiselect("Filtrar Conteúdo", temas)
        with c3:
            add_gabarito = st.checkbox("Incluir Folha de Respostas")

    # Aplicação dos filtros no DF
    df_f = df.copy()
    if f_disc: df_f = df_f[df_f['disciplina'].isin(f_disc)]
    if f_tema: df_f = df_f[df_f['conteudo'].isin(f_tema)]

    # --- SELEÇÃO DE QUESTÕES ---
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    selecionadas = st.multiselect("🔎 Selecione as questões para o documento:", options=df_f['label'].tolist())

    if selecionadas:
        ids = [int(s.split(" | ")[0]) for s in selecionadas]
        df_prova = df[df['id'].isin(ids)].copy()

        # --- GERAÇÃO DO HTML ---
        cabecalho = f"""<div style='text-align:center; border:1px solid #000; padding:10px;'>
                        <h2>{tipo_doc.upper()} DE {", ".join(f_disc).upper()}</h2>
                        <p>IFCE - CAMPUS FORTALEZA / CAUCAIA</p>
                        <p style='text-align:left;'>NOME:_________________________________________________ DATA:___/___/___</p>
                        </div><br>"""
        
        corpo_questoes = ""
       if itens_selecionados:
        ids = [int(s.split(" | ")[0]) for s in itens_selecionados]
        df_prova = df[df['id'].isin(ids)].copy()

        # 3. CONSTRUÇÃO DO HTML
        html_cabecalho = f"""
        <div style="border: 2px solid black; padding: 10px; text-align: center; font-family: 'Times New Roman';">
            <h3>{tipo_doc.upper()} DE {", ".join(sel_disc).upper() if sel_disc else "CONTEÚDO"}</h3>
            <p>INSTITUTO FEDERAL DO CEARÁ</p>
            <div style="text-align: left; margin-top: 20px;">
                NOME: _________________________________________________ TURMA: ________ DATA: ___/___/___
            </div>
        </div><br>
        """
        
        html_questoes = ""
        # AQUI ESTAVA O ERRO DE INDENTAÇÃO:
        for i, row in df_prova.reset_index().iterrows():
            t_base = f"<p><i>{row['texto_base']}</i></p>" if pd.notna(row['texto_base']) and row['texto_base'] != "" else ""
            html_questoes += f"""
            <div style="margin-bottom: 25px; font-family: 'Times New Roman';">
                <b>QUESTÃO {i+1}</b> ({row['fonte']})<br>
                {t_base}
                {row['comando']}<br>
            """
            
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                letras = ['a', 'b', 'c', 'd', 'e']
                html_questoes += "<ul style='list-style-type: none; padding-left: 20px;'>"
                for idx, alt in enumerate(alts):
                    if idx < len(letras):
                        html_questoes += f"<li>{letras[idx]}) {alt.strip()}</li>"
                html_questoes += "</ul>"
            else:
                html_questoes += "<div style='border: 1px dashed #ccc; height: 150px; margin-top: 10px;'></div>"
            
            html_questoes += "</div>"

        # 4. DOWNLOAD E PREVIEW
        html_final = f"<html><body>{html_cabecalho}{html_questoes}</body></html>"
        
        st.download_button("📥 Baixar Material", data=html_final, file_name="material_ifce.html", mime="text/html")
        st.subheader("👁️ Pré-visualização")
        st.components.v1.html(html_final, height=800, scrolling=True)
