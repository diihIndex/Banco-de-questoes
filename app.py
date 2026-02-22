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
    
    # Normalização de colunas para garantir que 'comando' e 'disciplina' sejam lidos
    df.columns = [
        str(c).lower().strip()
        .replace('ú', 'u').replace('ê', 'e').replace('ã', 'a')
        .replace('ç', 'c').replace('í', 'i').replace('é', 'e') 
        for c in df.columns
    ]
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# 3. Definição do Menu Lateral
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
            nova_fonte = st.text_input("Fonte (Ex: IFCE Fortaleza)")
        with c2:
            novo_tema = st.text_input("Conteúdo/Tema")
            nova_dif = st.select_slider("Dificuldade", ["Fácil", "Média", "Difícil"])
        
        novo_texto_base = st.text_area("Texto Base (Opcional)")
        novo_comando = st.text_area("Comando da Questão")
        novas_alts = st.text_input("Alternativas (separar por ';')")
        novo_gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Gerar Código para Planilha"):
            st.code(f"{nova_disc}\t{nova_fonte}\t{novo_tema}\t{novo_texto_base}\t{novo_comando}\t{novas_alts}\t{novo_gab}")

# --- PÁGINA: GERADOR DE PROVA ---
elif opcao == MENU_GERADOR:
    st.header("📄 Gerador de Material Didático")
    
    if 'comando' not in df.columns:
        st.error("Coluna 'comando' não encontrada na planilha! Verifique o cabeçalho.")
        st.stop()

    # 1. Filtros e Configurações
    with st.expander("⚙️ 1. Configurações e Filtros", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            disciplinas = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else []
            sel_disc = st.multiselect("Disciplina", disciplinas)
            tipo_doc = st.selectbox("Tipo de Cabeçalho", ["Prova", "Atividade"])
        
        df_f = df[df['disciplina'].isin(sel_disc)] if sel_disc else df
        
        with f2:
            temas = sorted(df_f['conteudo'].unique()) if 'conteudo' in df_f.columns else []
            sel_tema = st.multiselect("Conteúdo/Tema", temas)
            formato = st.radio("Formato das Questões", ["Objetiva", "Subjetiva"], horizontal=True)
        
        if sel_tema:
            df_f = df_f[df_f['conteudo'].isin(sel_tema)]
        
        add_gabarito = st.checkbox("Incluir Folha de Respostas ao final")

    # 2. Seleção de Itens
    df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'].astype(str) + " | " + df_f['comando'].astype(str).str[:70] + "..."
    itens_selecionados = st.multiselect("Selecione as questões para o documento:", options=df_f['label'].tolist())

    if itens_selecionados:
        ids = [int(s.split(" | ")[0]) for s in itens_selecionados]
        df_prova = df[df['id'].isin(ids)].copy()

        # 3. Construção do HTML
        html_cabecalho = f"""
        <div style="border: 2px solid black; padding: 15px; text-align: center; font-family: 'Times New Roman', serif;">
            <h2 style="margin:0;">{tipo_doc.upper()} DE {", ".join(sel_disc).upper() if sel_disc else "CONTEÚDO"}</h2>
            <p style="margin:5px;">INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DO CEARÁ</p>
            <div style="text-align: left; margin-top: 20px; font-size: 12pt;">
                NOME: _________________________________________________ TURMA: ________ DATA: ___/___/___
            </div>
        </div><br>
        """
        
        html_questoes = ""
        # Loop com indentação rigorosamente alinhada (4 espaços)
        for i, row in df_prova.reset_index().iterrows():
            t_base = f"<p><i>{row['texto_base']}</i></p>" if pd.notna(row['texto_base']) and row['texto_base'] != "" else ""
            html_questoes += f"""
            <div style="margin-bottom: 25px; font-family: 'Times New Roman', serif; font-size: 12pt;">
                <b>QUESTÃO {i+1}</b> ({row['fonte']})<br>
                {t_base}
                <div style="margin-top:5px;">{row['comando']}</div>
            """
            
            if formato == "Objetiva":
                alts = str(row['alternativas']).split(';')
                letras = ['a', 'b', 'c', 'd', 'e']
                html_questoes += "<ul style='list-style-type: none; padding-left: 20px; margin-top: 10px;'>"
                for idx, alt in enumerate(alts):
                    if idx < 5:
                        html_questoes += f"<li style='margin-bottom:5px;'>{letras[idx]}) {alt.strip()}</li>"
                html_questoes += "</ul>"
            else:
                html_questoes += "<div style='border: 1px dashed #ccc; height: 180px; margin-top: 15px; border-radius: 5px;'></div>"
            
            html_questoes += "</div>"

        # 4. Folha de Respostas (Opcional)
        if add_gabarito:
            html_questoes += "<div style='page-break-before: always; text-align:center;'><h3>FOLHA DE RESPOSTAS</h3>"
            for i in range(len(df_prova)):
                html_questoes += f"<p><b>{i+1}:</b> ( A ) ( B ) ( C ) ( D ) ( E )</p>"
            html_questoes += "</div>"

        html_final = f"<html><head><meta charset='UTF-8'></head><body>{html_cabecalho}{html_questoes}</body></html>"
        
        # 5. Saída
        st.download_button("📥 Baixar Documento (HTML/PDF)", data=html_final, file_name="material_ifce.html", mime="text/html")
        st.subheader("👁️ Pré-visualização")
        st.components.v1.html(html_final, height=800, scrolling=True)
