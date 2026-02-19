import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor IFCE", layout="wide", page_icon="📝")

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
        # --- FILTROS ---
        with st.expander("🎯 Filtros de Seleção", expanded=True):
            cf1, cf2, cf3 = st.columns(3)
            f_fontes = cf1.multiselect("Fonte", sorted(df['fonte'].unique()))
            f_temas = cf2.multiselect("Conteúdo", sorted(df['conteudo'].unique()))
            f_niveis = cf3.multiselect("Dificuldade", sorted(df['dificuldade'].unique()))

            df_f = df.copy()
            if f_fontes: df_f = df_f[df_f['fonte'].isin(f_fontes)]
            if f_temas: df_f = df_f[df_f['conteudo'].isin(f_temas)]
            if f_niveis: df_f = df_f[df_f['dificuldade'].isin(f_niveis)]

        # --- SELEÇÃO ---
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'] + " | " + df_f['enunciado'].str[:70] + "..."
        selecionadas = st.multiselect("Escolha as questões na ordem desejada:", options=df_f['label'].tolist())

        if selecionadas:
            ids = [int(s.split(" | ")[0]) for s in selecionadas]
            df_prova = df.set_index('id').loc[ids].reset_index()

            # --- BOTÃO DE DOWNLOAD ---
            # Geramos o HTML antecipadamente para o botão de download
            html_final = f"""
            <!DOCTYPE html>
            <html lang="pt-br"><head><meta charset="UTF-8">
            <style>
                @page {{ size: A4; margin: 1.5cm; }}
                body {{ font-family: Arial; padding: 20px; line-height: 1.5; color: #000; font-size: 12pt; }}
                .header-box {{ border: 1px solid #000; padding: 15px; text-align: center; margin-bottom: 30px; }}
                .q-box {{ margin-bottom: 25px; page-break-inside: avoid; border-bottom: 0.5px solid #eee; padding-bottom: 15px; }}
                .enunciado {{ font-weight: bold; margin-top: 10px; display: block; }}
                .alts {{ list-style-type: none; padding-left: 0; }}
            </style></head><body>
            <div class="header-box">
                <h2 style="margin:0;">LISTA DE EXERCÍCIOS - MATEMÁTICA</h2>
                <div style="text-align: left; margin-top: 15px;">
                    <p>ALUNO: _________________________________________________ DATA: ____/____/____</p>
                    <p>PROFESSOR: ____________________________________________ TURMA: _________</p>
                </div>
            </div>
            """
            for i, row in df_prova.iterrows():
                t_base = f"<p style='font-style: italic;'>{row['texto_base']}</p>" if row['texto_base'] else ""
                html_final += f"<div class='q-box'><b>QUESTÃO {i+1}</b> ({row['fonte']})<br>{t_base}<span class='enunciado'>{row['enunciado']}</span><ul style='list-style:none; padding-left:0;'>"
                alts = str(row['alternativas']).split(';')
                letras = ["a", "b", "c", "d", "e"]
                for idx, a in enumerate(alts):
                    if idx < 5: html_final += f"<li>{letras[idx]}) {a.strip()}</li>"
                html_final += "</ul></div>"
            html_final += "</body></html>"

            st.download_button(label="📥 Baixar Arquivo de Impressão", data=html_final, file_name="prova_ifce.html", mime="text/html")

            # --- PREVISÃO VISUAL (SIMULADOR A4) ---
            st.markdown("### 👁️ Pré-visualização do Documento")
            
            # CSS para o simulador de folha no Streamlit
            st.markdown("""
                <style>
                .a4-page {
                    background: white;
                    width: 100%;
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 40px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    border: 1px solid #ddd;
                    color: black;
                    font-family: Arial, sans-serif;
                }
                .preview-header {
                    border: 1px solid black;
                    padding: 15px;
                    text-align: center;
                    margin-bottom: 20px;
                }
                .preview-q { margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
                </style>
            """, unsafe_allow_html=True)

            # Renderizando a "Folha"
            with st.container():
                st.markdown('<div class="a4-page">', unsafe_allow_html=True)
                
                # Cabeçalho no Preview
                st.markdown(f"""
                    <div class="preview-header">
                        <h3 style="margin:0;">LISTA DE EXERCÍCIOS - MATEMÁTICA</h3>
                        <div style="text-align: left; font-size: 12px; margin-top: 10px;">
                            <p>ALUNO: ________________________________________ DATA: ____/____/____</p>
                            <p>PROFESSOR: ____________________________________ TURMA: _________</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Questões no Preview
                for i, row in df_prova.iterrows():
                    st.markdown(f'<div class="preview-q">', unsafe_allow_html=True)
                    st.markdown(f"**QUESTÃO {i+1}** ({row['fonte']})")
                    if row['texto_base']:
                        st.caption(row['texto_base'])
                    st.markdown(f"**{row['enunciado']}**")
                    
                    alts = str(row['alternativas']).split(';')
                    letras = ["a", "b", "c", "d", "e"]
                    for idx, alt in enumerate(alts):
                        if idx < len(letras):
                            st.write(f"{letras[idx]}) {alt.strip()}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("Banco de questões vazio.")
