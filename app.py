import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor IFCE", layout="wide")

# 2. Conexão e Dados
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
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
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'] + " | " + df_f['enunciado'].str[:70] + "..."
        selecionadas = st.multiselect("Escolha as questões na ordem desejada:", options=df_f['label'].tolist())

        if selecionadas:
            ids = [int(s.split(" | ")[0]) for s in selecionadas]
            df_prova = df.set_index('id').loc[ids].reset_index()

            # --- CONSTRUÇÃO DO HTML DE IMPRESSÃO OTIMIZADO PARA A4 ---
            html_prova = f"""
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <style>
                    /* Configurações de página A4 */
                    @page {{
                        size: A4;
                        margin: 1.5cm;
                    }}
                    body {{ 
                        font-family: 'Arial', sans-serif; 
                        width: 100%;
                        margin: 0;
                        padding: 0;
                        font-size: 12pt;
                        color: #000;
                    }}
                    .header-box {{ 
                        border: 1px solid #000; 
                        padding: 10px; 
                        text-align: center; 
                        margin-bottom: 20px;
                        box-sizing: border-box; /* Garante que a borda não aumente a largura */
                    }}
                    .q-box {{ 
                        margin-bottom: 20px; 
                        page-break-inside: avoid; 
                        border-bottom: 0.5px solid #eee; 
                        padding-bottom: 10px; 
                    }}
                    .enunciado {{ font-weight: bold; margin-top: 5px; display: block; }}
                    .alts {{ list-style-type: none; padding-left: 0; margin-top: 10px; }}
                    .alt-item {{ margin-bottom: 3px; }}
                    p {{ margin: 5px 0; }}
                    hr {{ border: none; border-top: 1px solid #000; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header-box">
                    <h2 style="margin:0; font-size: 16pt;">LISTA DE EXERCÍCIOS - MATEMÁTICA</h2>
                    <div style="text-align: left; margin-top: 10px; font-size: 11pt;">
                        <p>ALUNO: _________________________________________________ DATA: ____/____/____</p>
                        <p>PROFESSOR: ____________________________________________ TURMA: _________</p>
                    </div>
                </div>
            """
            for i, row in df_prova.iterrows():
                txt_base = f"<p style='font-style: italic;'>{row['texto_base']}</p>" if row['texto_base'] else ""
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
            
            st.download_button(
                label="📥 GERAR ARQUIVO PARA IMPRESSÃO (A4)",
                data=html_prova,
                file_name="prova_ifce_formatada.html",
                mime="text/html"
            )
            
            st.success("✅ Arquivo gerado com sucesso!")
            st.info("Abra o arquivo baixado e use **Ctrl + P**. Certifique-se de que o 'Destino' é sua impressora ou 'Salvar como PDF'.")

    else:
        st.warning("Banco de questões vazio.")
