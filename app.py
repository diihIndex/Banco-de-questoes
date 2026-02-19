import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurações da página
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

# --- CONEXÃO E DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# --- ESTILO CSS PARA IMPRESSÃO REAL ---
st.markdown("""
    <style>
    @media print {
        /* Esconde absolutamente tudo que não seja a prova */
        [data-testid="stSidebar"], 
        [data-testid="stHeader"], 
        .stTabs, 
        .no-print,
        button,
        header,
        footer {
            display: none !important;
        }
        
        /* Remove espaços em branco do Streamlit */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Garante que a prova ocupe a página toda */
        .print-area {
            display: block !important;
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Sistema de Gestão de Itens - IFCE")

tab1, tab2, tab3 = st.tabs(["🔍 Visualizar Banco", "📝 Cadastrar Questão", "📄 Gerar Lista/Prova"])

with tab1:
    st.header("Questões na Nuvem")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Inserir Novo Item")
    with st.form("novo_item", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fonte = c1.text_input("Fonte")
        ano = c2.text_input("Ano")
        conteudo = c1.text_input("Conteúdo")
        dificuldade = c2.selectbox("Dificuldade", ["Fácil", "Média", "Difícil"])
        txt_base = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        alts = st.text_input("Alternativas (separadas por ;)")
        gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Salvar na Planilha"):
            nova_q = pd.DataFrame([{"id": len(df) + 1, "fonte": fonte, "ano": ano, "conteudo": conteudo, "dificuldade": dificuldade, "texto_base": txt_base, "enunciado": enun, "alternativas": alts, "gabarito": gab}])
            df_final = pd.concat([df, nova_q], ignore_index=True)
            conn.update(data=df_final)
            st.success("Salvo! Atualize a página para atualizar o banco.")

with tab3:
    st.header("Gerador de Documento")
    
    if not df.empty:
        # --- ETAPA 1: FILTRO PRÉVIO ---
        st.subheader("1. Filtrar Banco")
        col_f1, col_f2 = st.columns(2)
        temas_disp = sorted(df['conteudo'].unique())
        filtro_tema = col_f1.multiselect("Filtrar por Conteúdo", temas_disp)
        
        niveis_disp = sorted(df['dificuldade'].unique())
        filtro_nivel = col_f2.multiselect("Filtrar por Dificuldade", niveis_disp)

        # Aplicar filtros ao banco que será exibido no seletor
        df_filtrado = df.copy()
        if filtro_tema:
            df_filtrado = df_filtrado[df_filtrado['conteudo'].isin(filtro_tema)]
        if filtro_nivel:
            df_filtrado = df_filtrado[df_filtrado['dificuldade'].isin(filtro_nivel)]

        st.divider()

        # --- ETAPA 2: SELEÇÃO E ORDEM ---
        st.subheader("2. Selecionar e Ordenar")
        df_filtrado['display'] = df_filtrado['id'].astype(str) + " | " + df_filtrado['conteudo'] + " | " + df_filtrado['enunciado'].str[:60] + "..."
        
        selecionadas = st.multiselect(
            "Selecione as questões na ordem que deseja (clique para adicionar):",
            options=df_filtrado['display'].tolist(),
            help="A ordem dos itens aqui será a ordem da prova."
        )

        if selecionadas:
            # Pegar os IDs na ordem correta
            ids_finais = [int(s.split(" | ")[0]) for s in selecionadas]
            df_prova = df.set_index('id').loc[ids_finais].reset_index()

            st.success(f"{len(df_prova)} questões selecionadas. Use Ctrl+P para imprimir.")

            # --- ÁREA DA PROVA (DENTRO DE UMA DIV ESPECÍFICA) ---
            st.markdown('<div class="print-area">', unsafe_allow_html=True)
            
            st.markdown("### 📄 LISTA DE EXERCÍCIOS - MATEMÁTICA")
            st.write("NOME: _________________________________________________ DATA: ___/___/___")
            st.write("PROFESSOR: ____________________________________________ TURMA: _________")
            st.markdown("---")
            
            for i, row in df_prova.iterrows():
                st.markdown(f"**Questão {i+1}**")
                st.write(row['texto_base'])
                st.markdown(f"**{row['enunciado']}**")
                
                alts = str(row['alternativas']).split(';')
                letras = ["a", "b", "c", "d", "e"]
                for idx, alt in enumerate(alts):
                    if idx < len(letras):
                        st.write(f"{letras[idx]}) {alt.strip()}")
                st.write("")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            with st.expander("Gabarito (não sai na impressão)"):
                for i, row in df_prova.iterrows():
                    st.write(f"Q{i+1}: {row['gabarito']}")
        else:
            st.info("Filtre o conteúdo acima e selecione as questões para gerar a prova.")
    else:
        st.warning("Banco de dados vazio.")
