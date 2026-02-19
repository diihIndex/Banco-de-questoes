import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

# 2. CSS Avançado para Impressão
# Este bloco força o navegador a ignorar toda a estrutura do Streamlit no papel
st.markdown("""
    <style>
    @media print {
        /* Esconde elementos do Streamlit */
        div[data-testid="stSidebar"], 
        div[data-testid="stHeader"], 
        div[data-testid="stToolbar"],
        .stTabs, .stButton, footer, header {
            display: none !important;
        }
        
        /* Reseta margens e paddings do app */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Garante que o texto da prova apareça */
        .print-content {
            display: block !important;
            visibility: visible !important;
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
        }
    }
    
    /* Estilo visual para a data não sumir */
    .data-campo {
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Gestor de Itens IFCE")

# 3. Conexão e Dados
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["🔍 Banco", "📝 Cadastro", "📄 Gerador de Prova"])

with tab1:
    st.dataframe(df, use_container_width=True)

with tab2:
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
            st.success("Salvo!")

with tab3:
    if not df.empty:
        st.subheader("1. Filtros de Busca")
        cf1, cf2, cf3 = st.columns(3)
        
        # Filtros Adicionados
        f_fontes = cf1.multiselect("Fonte", sorted(df['fonte'].unique()))
        f_temas = cf2.multiselect("Conteúdo", sorted(df['conteudo'].unique()))
        f_niveis = cf3.multiselect("Dificuldade", sorted(df['dificuldade'].unique()))

        # Lógica de Filtro
        df_f = df.copy()
        if f_fontes: df_f = df_f[df_f['fonte'].isin(f_fontes)]
        if f_temas: df_f = df_f[df_f['conteudo'].isin(f_temas)]
        if f_niveis: df_f = df_f[df_f['dificuldade'].isin(f_niveis)]

        st.divider()
        
        st.subheader("2. Seleção e Ordem")
        df_f['label'] = df_f['id'].astype(str) + " | " + df_f['fonte'] + " | " + df_f['enunciado'].str[:70] + "..."
        
        col_sel, col_btn = st.columns([4, 1])
        selecionadas = col_sel.multiselect("Escolha as questões na ordem desejada:", options=df_f['label'].tolist(), key="prova_multiselect")
        
        if col_btn.button("Limpar Tudo"):
            st.cache_data.clear()
            st.rerun()

        if selecionadas:
            ids = [int(s.split(" | ")[0]) for s in selecionadas]
            df_prova = df.set_index('id').loc[ids].reset_index()

            st.info("💡 Como imprimir: 1. Veja a prova abaixo. 2. Aperte CTRL + P. 3. Em 'Mais Definições', desmarque 'Cabeçalhos e Rodapés'.")

            # --- ÁREA DE IMPRESSÃO ---
            st.markdown('<div class="print-content">', unsafe_allow_html=True)
            
            # Cabeçalho da Prova
            st.markdown("""
                <div style="text-align: center; border: 1px solid black; padding: 10px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">LISTA DE EXERCÍCIOS - MATEMÁTICA</h2>
                    <div style="text-align: left; margin-top: 15px;">
                        <p>NOME: _________________________________________________ DATA: <span class="data-campo">____/____/____</span></p>
                        <p>PROFESSOR: ____________________________________________ TURMA: _________</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for i, row in df_prova.iterrows():
                st.markdown(f"**QUESTÃO {i+1}** ({row['fonte']} - {row['ano']})")
                if row['texto_base']:
                    st.write(row['texto_base'])
                st.markdown(f"**{row['enunciado']}**")
                
                alts = str(row['alternativas']).split(';')
                letras = ["a", "b", "c", "d", "e"]
                for idx, alt in enumerate(alts):
                    if idx < len(letras):
                        st.write(f"{letras[idx]}) {alt.strip()}")
                st.write("")
                st.markdown("---")
            
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("Ver Gabarito"):
                for i, row in df_prova.iterrows():
                    st.write(f"Q{i+1}: {row['gabarito']}")
    else:
        st.warning("Banco vazio.")
