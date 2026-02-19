import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gestor IFCE", layout="wide")

# 2. Conexão e Dados
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# 3. Navegação Lateral (Evita o reset das abas)
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
        # Filtros (Aqui o filtro NÃO reseta a aba mais!)
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

            # --- CONSTRUÇÃO DO HTML DE IMPRESSÃO ---
            # Isso cria um documento independente que não sofre interferência do site
            html_prova = f"""
            <html><head><style>
                body {{ font-family: 'Arial', sans-serif; padding: 40px; color: #333; }}
                .header-box {{ border: 2px solid #000; padding: 15px; text-align: center; margin-bottom: 30px; }}
                .q-box {{ margin-bottom: 25px; page-break-inside: avoid; }}
                .enunciado {{ font-weight: bold; margin-top: 10px; }}
                .alts {{ list-style-type: none; padding-left: 0; }}
                .alt-item {{ margin-bottom: 5px; }}
                @media print {{ .no-print {{ display: none; }} }}
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
                html_prova += f"""
                <div class="q-box">
                    <b>QUESTÃO {i+1}</b> ({row['fonte']} - {row['ano']})<br>
                    <p>{row['texto_base'] if row['texto_base'] else ''}</p>
                    <div class="enunciado">{row['enunciado']}</div>
                    <ul class="alts">
                """
                alts_lista = str(row['alternativas']).split(';')
                letras = ["a", "b", "c", "d", "e"]
                for idx, a in enumerate(alts_lista):
                    if idx < 5: html_prova += f"<li class='alt-item'>{letras[idx]}) {a.strip()}</li>"
                html_prova += "</ul></div><hr>"
            
            html_prova += "</body><script>window.print();</script></html>"

            # Botão de Impressão (Abre nova aba)
            b64 = base64.b64encode(html_prova.encode('utf-8')).decode()
            href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;"><button style="background-color: #008CBA; color: white; padding: 15px 32px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">🖨️ ABRIR PROVA PARA IMPRESSÃO</button></a>'
            
            st.markdown("### 3. Finalizar")
            st.markdown(href, unsafe_allow_html=True)
            st.info("Clique no botão azul acima. Ele abrirá a prova formatada em uma nova aba já pronta para imprimir ou salvar em PDF.")
            
            # Preview na tela
            with st.expander("Ver Preview da Prova"):
                for i, row in df_prova.iterrows():
                    st.write(f"Q{i+1}: {row['enunciado'][:100]}...")
