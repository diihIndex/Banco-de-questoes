import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Avaliações IFCE", layout="wide", page_icon="📝")

# 2. Conexão e Dados
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
# Normalização das colunas
df.columns = [c.lower().strip().replace('ú', 'u').replace('ê', 'e') for c in df.columns]

# 3. Navegação Lateral
st.sidebar.title("📌 Menu Principal")
pagina = st.sidebar.radio("Navegar para:", ["🔍 Banco de Questões", "📝 Cadastrar Nova", "📄 Gerador de Prova"])

# --- PÁGINA: GERADOR ---
if pagina == "📄 Gerador de Prova":
    st.header("📄 Gerador de Material Didático")
    
    if not df.empty:
        # --- SEÇÃO DE CONFIGURAÇÃO ---
        with st.expander("⚙️ Configurações do Documento", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                tipo_doc = st.selectbox("Tipo de Cabeçalho", ["Prova", "Atividade"])
                tipo_questao = st.radio("Formato das Questões", ["Objetiva (com alternativas)", "Subjetiva (com espaço para resolução)"], horizontal=True)
            
            with col2:
                add_gabarito = st.checkbox("Adicionar Folha de Gabarito (Modelo IFCE)")
                # Busca por Disciplina (Filtro por coluna ou por aba se houver)
                disciplinas_disponiveis = sorted(df['disciplina'].unique()) if 'disciplina' in df.columns else ["Matemática"]
                f_disciplina = st.multiselect("Filtrar por Disciplina", disciplinas_disponiveis)

        # --- FILTROS DE CONTEÚDO ---
        with st.expander("🎯 Filtros de Seleção de Questões"):
            cf1, cf2 = st.columns(2)
            
            df_f = df.copy()
            if f_disciplina:
                df_f = df_f[df_f['disciplina'].isin(f_disciplina)]
            
            f_temas = cf1.multiselect("Conteúdo/Tema", sorted(df_f['conteudo'].unique()))
            if f_temas:
                df_f = df_f[df_f['conteudo'].isin(f_temas)]
                
            f_fontes = cf2.multiselect("Fonte/Ano", sorted(df_f['fonte'].unique()))
            if f_fontes:
                df_f = df_f[df_f['fonte'].isin(f_fontes)]

        # --- SELEÇÃO ---
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'] + " | " + df_f['enunciado'].str[:70] + "..."
        selecionadas = st.multiselect("Selecione as questões:", options=df_f['label'].tolist())

        if selecionadas:
            # Correção do erro de ID (ValueError) comentada anteriormente
            ids = []
            for s in selecionadas:
                try:
                    ids.append(int(s.split(" | ")[0].strip()))
                except: continue
            
            df_prova = df.set_index('id').loc[ids].reset_index()

            # --- CONSTRUÇÃO DO HTML ---
            # Definição do Cabeçalho
            if tipo_doc == "Prova":
                cabecalho_html = f"""
                <div class="header-box">
                    <h2 style="margin:0;">AVALIAÇÃO DE {', '.join(f_disciplina).upper() if f_disciplina else 'CONTEÚDO'}</h2>
                    <p>INSTITUTO FEDERAL DO CEARÁ - CAMPUS FORTALEZA</p>
                    <div style="text-align: left; margin-top: 15px; font-size: 11pt;">
                        <p>ALUNO(A): _________________________________________________ Nº: ____ TURMA: ________</p>
                        <p>PROFESSOR(A): ____________________________________________ DATA: ___/___/___ NOTA: ________</p>
                    </div>
                </div>"""
            else:
                cabecalho_html = f"""
                <div class="header-box" style="border-bottom: 2px solid #000;">
                    <h2 style="margin:0;">LISTA DE EXERCÍCIOS</h2>
                    <p>Disciplina: {', '.join(f_disciplina) if f_disciplina else 'Geral'} | Assunto: Revisão</p>
                    <div style="text-align: left; margin-top: 10px; font-size: 10pt;">
                        <p>NOME: ____________________________________________________ TURMA: _________ DATA: ___/___/___</p>
                    </div>
                </div>"""

            html_final = f"""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8">
            <style>
                @page {{ size: A4; margin: 1.5cm; }}
                body {{ font-family: 'Times New Roman', serif; line-height: 1.5; color: #000; }}
                .header-box {{ text-align: center; margin-bottom: 25px; padding: 10px; border: 1px solid #000; }}
                .q-box {{ margin-bottom: 25px; page-break-inside: avoid; }}
                .espaco-resolucao {{ border: 1px dashed #ccc; height: 150px; margin-top: 10px; border-radius: 5px; }}
                .gabarito-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .gabarito-table td {{ border: 1px solid #000; padding: 10px; text-align: center; width: 50px; }}
                .page-break {{ page-break-before: always; }}
            </style></head><body>
            {cabecalho_html}
            """

            for i, row in df_prova.iterrows():
                espaco = " " if row['texto_base'] and row['enunciado'] else ""
                html_final += f"""
                <div class="q-box">
                    <b>QUESTÃO {i+1}</b> ({row['fonte']})<br>
                    {row['texto_base']}{espaco}{row['enunciado']}
                """
                
                if "Objetiva" in tipo_questao:
                    html_final += "<ul style='list-style-type: none; padding-left: 0;'>"
                    alts = str(row['alternativas']).split(';')
                    letras = ["a", "b", "c", "d", "e"]
                    for idx, a in enumerate(alts):
                        if idx < 5: html_final += f"<li>{letras[idx]}) {a.strip()}</li>"
                    html_final += "</ul>"
                else:
                    html_final += "<div class='espaco-resolucao'><small style='color:#aaa; padding: 5px;'>Resolução:</small></div>"
                
                html_final += "</div>"

            # Cartão Resposta (Modelo IFCE)
            if add_gabarito:
                html_final += f"""
                <div class="page-break"></div>
                <div class="header-box"><h3>CARTÃO RESPOSTA / GABARITO</h3></div>
                <p>Marque apenas uma alternativa por questão.</p>
                <table class="gabarito-table">
                """
                for i in range(len(df_prova)):
                    html_final += f"<tr><td><b>{i+1}</b></td><td>( A )</td><td>( B )</td><td>( C )</td><td>( D )</td><td>( E )</td></tr>"
                html_final += "</table>"

            html_final += "</body></html>"

            # Download
            st.download_button("📥 Baixar PDF/HTML", data=html_final, file_name="material_ifce.html", mime="text/html")
            st.info("💡 Dica: Ao abrir o arquivo baixado no navegador, aperte Ctrl+P e salve como PDF.")

            # --- PREVIEW ---
            st.markdown("---")
            st.subheader("👁️ Pré-visualização")
            st.components.v1.html(html_final, height=800, scrolling=True)

    else:
        st.warning("Banco de dados não encontrado.")
