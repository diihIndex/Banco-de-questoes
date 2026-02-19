import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurações da página
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

# --- CONEXÃO E DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
# Padronização de nomes de colunas
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

st.title("📚 Sistema de Gestão de Itens - IFCE")

# --- ABAS ---
# Usamos o 'key' para tentar manter a aba ativa durante interações
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
            st.success("Salvo com sucesso! Atualize a página para ver no banco.")

with tab3:
    st.header("Gerador de Documento")
    
    if not df.empty:
        # Criar uma coluna de exibição amigável para o seletor
        df['display_name'] = df['id'].astype(str) + " - " + df['conteudo'] + " (" + df['fonte'] + ")"
        
        st.subheader("1. Selecione as questões na ordem desejada:")
        # O Multiselect funciona como sua fila de reordenação
        selecao = st.multiselect(
            "Clique ou digite para adicionar questões à prova:",
            options=df['display_name'].tolist(),
            default=st.session_state.get('last_selection', []),
            help="A ordem em que você clica é a ordem que aparecerá na prova."
        )
        st.session_state['last_selection'] = selecao

        if selecao:
            # Filtrar e manter a ordem exata da seleção
            ids_selecionados = [int(item.split(" - ")[0]) for item in selecao]
            df_prova = df.set_index('id').loc[ids_selecionados].reset_index()

            st.divider()
            st.subheader("2. Visualização da Prova")
            
            # --- CABEÇALHO DA PROVA NA TELA ---
            container_prova = st.container()
            with container_prova:
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
                        if idx < 5: st.write(f"{letras[idx]}) {alt.strip()}")
                    st.write("")
                
                st.divider()
                with st.expander("Gabarito"):
                    for i, row in df_prova.iterrows():
                        st.write(f"Q{i+1}: {row['gabarito']}")

            # --- BOTÃO DE IMPRESSÃO ---
            st.info("💡 Para imprimir: Pressione **Ctrl + P** no seu teclado. O menu lateral e botões sumirão automaticamente no papel.")
            
            # CSS para esconder o que não é a prova na hora do Ctrl+P
            st.markdown("""
                <style>
                @media print {
                    div[data-testid="stSidebar"], 
                    div.stButton, 
                    header, 
                    .stTabs, 
                    .no-print {
                        display: none !important;
                    }
                    .main .block-container {
                        padding: 0 !important;
                    }
                }
                </style>
            """, unsafe_allow_html=True)
            
        else:
            st.info("Selecione pelo menos uma questão para visualizar a prova.")
    else:
        st.warning("Banco de dados vazio.")
