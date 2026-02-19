import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

# Configurações da página
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

# --- ESTILO CSS PARA IMPRESSÃO ---
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"], .stTabs, [data-testid="stToolbar"], .no-print {
            display: none !important;
        }
        .main .block-container {
            padding-top: 0rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Sistema de Gestão de Itens - IFCE")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df_original = conn.read(ttl=0)

# Limpeza e padronização das colunas
df = df_original.copy()
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# --- ABAS ---
abas = st.tabs(["🔍 Visualizar Banco", "📝 Cadastrar Questão", "📄 Gerar Lista/Prova"])

# --- ABA 1: VISUALIZAR ---
with abas[0]:
    st.header("Questões na Nuvem")
    st.dataframe(df, use_container_width=True)

# --- ABA 2: CADASTRAR ---
with abas[1]:
    st.header("Inserir Novo Item")
    with st.form("novo_item"):
        col1, col2 = st.columns(2)
        fonte = col1.text_input("Fonte")
        ano = col2.text_input("Ano")
        conteudo = col1.text_input("Conteúdo")
        dificuldade = col2.selectbox("Dificuldade", ["Fácil", "Média", "Difícil"])
        txt_base = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        alts = st.text_input("Alternativas (separadas por ;)")
        gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Salvar na Planilha"):
            nova_q = pd.DataFrame([{"id": len(df) + 1, "fonte": fonte, "ano": ano, "conteudo": conteudo, "dificuldade": dificuldade, "texto_base": txt_base, "enunciado": enun, "alternativas": alts, "gabarito": gab}])
            df_final = pd.concat([df, nova_q], ignore_index=True)
            conn.update(data=df_final)
            st.success("Salvo com sucesso!")
            st.balloons()

# --- ABA 3: GERAR PROVA (COM QUESTÃO ALEATÓRIA) ---
with abas[2]:
    st.header("Gerador de Documento")
    
    if not df.empty:
        # Filtros principais
        c1, c2 = st.columns(2)
        filtro_tema = c1.multiselect("Filtrar por Conteúdo", df['conteudo'].unique(), key="f_tema")
        filtro_nivel = c2.multiselect("Filtrar por Dificuldade", df['dificuldade'].unique(), key="f_nivel")
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if filtro_tema:
            df_filtrado = df_filtrado[df_filtrado['conteudo'].isin(filtro_tema)]
        if filtro_nivel:
            df_filtrado = df_filtrado[df_filtrado['dificuldade'].isin(filtro_nivel)]
        
        st.divider()
        
        # Opções de Sorteio
        st.subheader("Configuração da Lista")
        col_cfg1, col_cfg2 = st.columns(2)
        
        modo_selecao = col_cfg1.radio("Modo de seleção:", ["Todas as filtradas", "Sortear questões aleatórias"], key="modo_sel")
        
        df_prova = df_filtrado.copy()
        
        if modo_selecao == "Sortear questões aleatórias":
            max_questoes = len(df_filtrado)
            qtd = col_cfg2.number_input(f"Quantas questões sortear? (Máx: {max_questoes})", min_value=1, max_value=max_questoes, value=min(5, max_questoes))
            if st.button("🔄 Sortear Novas Questões"):
                # O clique no botão força o reload e sorteia novamente
                st.session_state.sorteio = df_filtrado.sample(n=qtd).index.tolist()
            
            if "sorteio" in st.session_state and len(st.session_state.sorteio) == qtd:
                # Se o número sorteado bater com a quantidade pedida, usa o sorteio da memória
                df_prova = df_filtrado.loc[st.session_state.sorteio]
            else:
                # Sorteio inicial
                df_prova = df_filtrado.sample(n=qtd)
                st.session_state.sorteio = df_prova.index.tolist()

        st.write(f"A lista atual contém **{len(df_prova)}** questões.")
        
        if st.button("🖨️ Visualizar Prova para Impressão"):
            st.markdown("---")
            # Cabeçalho da Prova
            st.markdown("### 📄 LISTA DE EXERCÍCIOS - MATEMÁTICA")
            st.write("NOME: _________________________________________________ DATA: ___/___/___")
            st.write("PROFESSOR: ____________________________________________ TURMA: _________")
            st.markdown("---")
            
            # Loop de renderização
            for i, (idx, row) in enumerate(df_prova.iterrows()):
                st.markdown(f"**Questão {i+1}** - *({row['fonte']} / {row['ano']})*")
                st.write(row['texto_base'])
                st.markdown(f"**{row['enunciado']}**")
                
                if isinstance(row['alternativas'], str):
                    lista_alts = row['alternativas'].split(';')
                    letras = ["A", "B", "C", "D", "E"]
                    for l_idx, alt in enumerate(lista_alts):
                        if l_idx < len(letras):
                            st.write(f"{letras[l_idx]}) {alt.strip()}")
                st.write("")
                st.divider()
                
            # Gabarito escondido na tela, mas aparece no final se quiser imprimir
            with st.expander("Gabarito (não sai na impressão se estiver fechado)"):
                for i, (idx, row) in enumerate(df_prova.iterrows()):
                    st.write(f"Q{i+1}: {row['gabarito']}")
    else:
        st.warning("Banco de dados vazio.")
