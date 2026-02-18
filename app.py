import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

st.title("📚 Sistema de Gestão de Itens - IFCE")

# Conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl=0)

df = load_data()

# Criação das Abas
aba1, aba2, aba3 = st.tabs(["🔍 Visualizar Banco", "📝 Cadastrar Questão", "📄 Gerar Lista/Prova"])

with aba1:
    st.header("Questões na Nuvem")
    st.dataframe(df, use_container_width=True)

with aba2:
    st.header("Inserir Novo Item")
    with st.form("novo_item"):
        col1, col2 = st.columns(2)
        fonte = col1.text_input("Fonte (ex: IFCE)")
        ano = col2.text_input("Ano")
        conteudo = col1.selectbox("Conteúdo", ["Razão e Proporção", "Regra de Três", "Escala", "Divisão Proporcional", "Outros"])
        dificuldade = col2.select_slider("Dificuldade", ["Fácil", "Média", "Difícil"])
        
        txt_base = st.text_area("Texto Base (Exatamente como no original)")
        enun = st.text_area("Enunciado (Exatamente como no original)")
        
        st.info("Separe as alternativas com ponto e vírgula (;)")
        alts = st.text_input("Alternativas")
        gab = st.text_input("Gabarito")
        
        if st.form_submit_button("Salvar na Planilha"):
            nova_q = pd.DataFrame([{
                "id": len(df) + 1,
                "fonte": fonte,
                "ano": ano,
                "conteudo": conteudo,
                "dificuldade": dificuldade,
                "texto_base": txt_base,
                "enunciado": enun,
                "alternativas": alts,
                "gabarito": gab
            }])
            df_final = pd.concat([df, nova_q], ignore_index=True)
            conn.update(data=df_final)
            st.success("Salvo com sucesso!")
            st.balloons()

with aba3:
    st.header("Gerador de Documento")
    
    # Padronização das colunas para evitar o KeyError
    # Isso transforma 'Conteúdo' em 'conteudo' automaticamente no código
    df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

    if not df.empty:
        col_a, col_b = st.columns(2)
        
        # Agora usamos 'conteudo' sem medo do acento na planilha
        opcoes_tema = df['conteudo'].unique()
        temas = col_a.multiselect("Filtrar por Conteúdo", opcoes_tema)
        
        opcoes_nivel = df['dificuldade'].unique()
        niveis = col_b.multiselect("Filtrar por Dificuldade", opcoes_nivel)
        
        # ... (resto do código de filtragem)
    else:
        st.warning("O banco de dados está vazio. Cadastre questões primeiro.")
    
    # Filtragem lógica
    questoes_filtradas = df.copy()
    if temas:
        questoes_filtradas = questoes_filtradas[questoes_filtradas['conteudo'].isin(temas)]
    if niveis:
        questoes_filtradas = questoes_filtradas[questoes_filtradas['dificuldade'].isin(niveis)]
    
    st.write(f"Foram encontradas **{len(questoes_filtradas)}** questões com esses filtros.")
    
    if st.button("Gerar Visualização de Impressão"):
        st.divider()
        st.markdown("### 📄 LISTA DE EXERCÍCIOS - MATEMÁTICA")
        
        for i, row in questoes_filtradas.iterrows():
            # Cabeçalho da questão
            st.markdown(f"**Questão {i+1}** - *({row['fonte']} / {row['ano']})*")
            
            # Texto base e enunciado
            st.write(row['texto_base'])
            st.markdown(f"**{row['enunciado']}**")
            
            # Formatação das alternativas
            if isinstance(row['alternativas'], str):
                lista_alts = row['alternativas'].split(';')
                letras = ["A", "B", "C", "D", "E"]
                for idx, alt in enumerate(lista_alts):
                    if idx < len(letras):
                        st.write(f"{letras[idx]}) {alt.strip()}")
            
            st.write("") # Espaço entre questões
            st.divider()
            
        # Gabarito ao final
        with st.expander("Clique para ver o Gabarito"):
            for i, row in questoes_filtradas.iterrows():
                st.write(f"Questão {i+1}: {row['gabarito']}")
