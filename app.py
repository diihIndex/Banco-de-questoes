import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor IFCE", layout="wide")

# 2. Conexão e Dados
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
# Padronização de colunas
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# 3. Navegação Lateral
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["🔍 Banco de Questões", "📝 Cadastrar Nova", "📄 Gerador de Prova"])

# --- PÁGINA 1: BANCO ---
if pagina == "🔍 Banco de Questões":
    st.header("Visualização do Banco")
    st.dataframe(df, use_container_width=True)

# --- PÁGINA 2: CADASTRO ---
elif pagina == "📝 Cadastrar Nova":
    st.header("Cadastrar Nova Questão")
    with st.form("cadastro", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        fnt = c1.text_input("Fonte")
        an = c2.text_input("Ano")
        cont = c3.text_input("Conteúdo")
        dif = st.selectbox("Dificuldade", ["Fácil", "Média", "Difícil"])
        txt = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        alts = st.text_input("Alternativas (separadas por ;)")
        gb = st.text_input("Gabarito")
        if st.form_submit_button("Salvar na Planilha"):
            nova = pd.DataFrame([{"id": len(df)+1, "fonte": fnt, "ano": an, "conteudo": cont, "dificuldade": dif, "texto_base": txt, "enunciado": enun, "alternativas": alts, "gabarito": gb}])
            conn.update(data=pd.concat([df, nova], ignore_index=True))
            st.success("Questão salva com sucesso!")

# --- PÁGINA 3: GERADOR ---
elif pagina == "📄 Gerador de Prova":
    st.header("Gerador de Prova")
    
    if not df.empty:
        st.subheader("1. Filtros")
        cf1, cf2, cf3 = st.columns(3)
        f_fontes = cf1.multiselect("Fonte", sorted(df['fonte'].unique()))
        f_temas = cf2.multiselect("Conteúdo", sorted(df['conteudo'].unique()))
        f_niveis = cf3.multiselect("Dificuldade", sorted(df['dificuldade'].unique()))

        df_f = df.copy()
        if f_fontes: df_f = df_f[df_f['fonte'].isin(f_fontes)]
        if f_temas: df_f = df_f[df_f['conteudo'].isin(f_temas)]
        if f_niveis: df_f = df_f[df_f['dificuldade'].isin(f_niveis)]

        st.subheader("2. Seleção e Ordem")
        # Criar label para o seletor
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'] + " | " + df_f['enunciado'].str[:70] + "..."
        selecionadas = st.multiselect("Escolha as questões na ordem desejada:", options=df_f['label'].tolist())

        if selecionadas:
            ids = [int(s.split(" | ")[0]) for s in selecionadas]
            df_prova = df.set_index('id').loc[ids].reset_index()

            # --- CONSTRUÇÃO DO HTML DE IMPRESSÃO ---
            html_prova = f"""
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Arial', sans-serif; padding: 30px; line-height: 1.5; color: #000; }}
                    .header-box {{ border: 2px solid #000; padding: 15px; text-align: center; margin-bottom: 30px; }}
                    .q-box {{ margin-bottom: 25px; page-break-inside: avoid; border-bottom: 1px dashed #ccc; padding-bottom: 15px; }}
                    .enunciado {{ font-weight: bold; margin-top: 10px; display: block; }}
                    .alts {{ list-style-type: none; padding-left: 0; }}
                    .alt-item {{ margin-bottom: 5px; }}
                    @media print {{ .no-print {{ display: none; }} hr {{ display: none; }} }}
                </style>
            </head>
            <body>
                <div class="header-box">
                    <h2 style="margin:0;">LISTA DE EXERCÍCIOS - MATEMÁTICA</h2>
                    <div style="text-align: left; margin-top: 15px;">
                        <p>ALUNO: _________________________________________________ DATA: ____/____/____</p>
                        <p>PROFESSOR: ____________________________________________ TURMA: _________</p>
                    </div>
                </div>
            """
            for i, row in df_prova.iterrows():
                txt_base = f"<p>{row['texto_base']}</p>" if row['texto_base'] else ""
                html_prova += f"""
                <div class="q-box">
                    <b>QUESTÃO {i+1}</b> ({row['fonte']} - {row['ano']})<br>
                    {txt_base}
                    <span class="enunciado">{row['enunciado']}</span>
                    <ul class="alts">
                """
                alts_lista = str(row['alternativas']).split(';')
                letras = ["a", "b", "c", "d", "e"]
                for idx, a in enumerate(alts_lista):
                    if idx < 5: html_prova += f"<li class='alt-item'>{letras[idx]}) {a.strip()}</li>"
                html_prova += "</ul></div>"
            
            html_prova += "</body></html>"

            st.markdown("### 3. Finalizar")
            
            # BOTÃO DE DOWNLOAD (Substitui o botão de abrir nova aba)
            st.download_button(
                label="📥 GERAR ARQUIVO DE IMPRESSÃO",
                data=html_prova,
                file_name="prova_matematica.html",
                mime="text/html",
                help="Clique para baixar o arquivo. Depois, abra-o e use Ctrl+P para imprimir."
            )
            
            st.info("💡 **Instruções:** Clique no botão acima para baixar a prova. Abra o arquivo baixado no seu navegador e aperte **Ctrl + P**.")
            
            # Preview simples na tela
            with st.expander("Prévia das questões selecionadas"):
                for i, row in df_prova.iterrows():
                    st.write(f"**Q{i+1}:** {row['enunciado'][:100]}...")

    else:
        st.warning("Banco de questões vazio.")
