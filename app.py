import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gerador de Provas IFCE", layout="wide", page_icon="📚")

# Inicialização do Banco de Dados com TODAS as questões encontradas
if 'banco_questoes' not in st.session_state:
    st.session_state.banco_questoes = [
        {"id": 1, "fonte": "IFCE", "ano": "2026.1 - Caucaia", "conteudo": "Razão e Proporção", "dificuldade": "Fácil", "texto_base": "Em um determinado setor do IFCE, trabalham 45 pessoas, entre homens e mulheres.", "enunciado": "Se a razão entre o número de homens e o número de mulheres é de 2 para 3, o número de mulheres que trabalham nesse setor é:", "alternativas": ["18", "27", "30", "15", "20"], "gabarito": "27"},
        {"id": 2, "fonte": "IFCE", "ano": "2026.1 - Caucaia", "conteudo": "Regra de Três Simples", "dificuldade": "Média", "texto_base": "Para realizar a pintura das salas de aula de um campus, 4 pintores, com a mesma capacidade de trabalho, levam 12 dias.", "enunciado": "Se fossem contratados mais 2 pintores, com essa mesma capacidade, o tempo necessário para realizar essa mesma pintura seria de:", "alternativas": ["6 dias", "8 dias", "10 dias", "18 dias", "15 dias"], "gabarito": "8 dias"},
        {"id": 3, "fonte": "IFCE", "ano": "2026.1 - Fortaleza", "conteudo": "Regra de Três Simples", "dificuldade": "Fácil", "texto_base": "Uma impressora consegue imprimir 150 páginas em 10 minutos.", "enunciado": "Mantendo o mesmo ritmo de impressão, quantas páginas essa impressora imprimirá em 25 minutos?", "alternativas": ["300", "325", "350", "375", "400"], "gabarito": "375"},
        {"id": 4, "fonte": "IFCE", "ano": "2026.1 - Fortaleza", "conteudo": "Razão", "dificuldade": "Fácil", "texto_base": "Em uma turma com 40 alunos, 12 foram reprovados em uma disciplina.", "enunciado": "A razão entre o número de alunos aprovados e o número total de alunos dessa turma é:", "alternativas": ["3/10", "7/10", "3/7", "7/3", "2/5"], "gabarito": "7/10"},
        {"id": 5, "fonte": "IFCE", "ano": "2025.1", "conteudo": "Divisão Proporcional", "dificuldade": "Média", "texto_base": "Dois sócios, Antônio e Benedito, decidiram dividir o lucro de R$ 12.000,00 de sua empresa de forma diretamente proporcional ao tempo de trabalho de cada um.", "enunciado": "Se Antônio trabalhou 3 anos e Benedito trabalhou 5 anos, qual a parte do lucro que caberá a Benedito?", "alternativas": ["R$ 4.500,00", "R$ 6.000,00", "R$ 7.500,00", "R$ 8.000,00", "R$ 9.000,00"], "gabarito": "R$ 7.500,00"},
        {"id": 6, "fonte": "IFCE", "ano": "2024.1", "conteudo": "Razão", "dificuldade": "Fácil", "texto_base": "Em uma biblioteca, a razão entre o número de livros de Literatura e o número de livros de Matemática é de 5 para 2.", "enunciado": "Se a biblioteca possui 150 livros de Matemática, o número de livros de Literatura é:", "alternativas": ["300", "325", "350", "375", "400"], "gabarito": "375"},
        {"id": 7, "fonte": "IFCE", "ano": "2024.1", "conteudo": "Regra de Três Simples", "dificuldade": "Fácil", "texto_base": "Para preparar um refresco, utiliza-se 2 copos de suco concentrado para cada 5 copos de água.", "enunciado": "Se forem utilizados 6 copos de suco concentrado, quantos copos de água serão necessários para manter a mesma proporção?", "alternativas": ["10", "12", "15", "18", "20"], "gabarito": "15"},
        {"id": 8, "fonte": "IFCE", "ano": "2023.1", "conteudo": "Regra de Três Simples", "dificuldade": "Fácil", "texto_base": "Um automóvel consome 12 litros de combustível para percorrer uma distância de 150 km.", "enunciado": "Quantos litros serão necessários para percorrer 250 km, mantendo o mesmo consumo médio?", "alternativas": ["18", "20", "22", "24", "25"], "gabarito": "20"},
        {"id": 9, "fonte": "IFCE", "ano": "2020.1", "conteudo": "Escala", "dificuldade": "Média", "texto_base": "A distância entre duas cidades em um mapa, feito na escala 1:500.000, é de 8 cm.", "enunciado": "A distância real entre essas duas cidades, em quilômetros, é:", "alternativas": ["4 km", "40 km", "400 km", "4.000 km", "40.000 km"], "gabarito": "40 km"},
        {"id": 10, "fonte": "IFCE", "ano": "2019.1", "conteudo": "Regra de Três Composta", "dificuldade": "Difícil", "texto_base": "Se 5 máquinas, funcionando 8 horas por dia, produzem 1.200 peças em 4 dias,", "enunciado": "quantas peças serão produzidas por 8 máquinas, funcionando 10 horas por dia, durante 5 dias?", "alternativas": ["2.400", "3.000", "3.200", "3.600", "4.000"], "gabarito": "3.000"}
    ]

st.title("🛠️ Banco de Questões Matemática - IFCE")

menu = st.sidebar.selectbox("Navegação", ["Início/Banco", "Cadastrar Item", "Gerar Lista"])

if menu == "Início/Banco":
    st.header("🔍 Itens Cadastrados")
    df = pd.DataFrame(st.session_state.banco_questoes).drop(columns=['alternativas'])
    st.dataframe(df, use_container_width=True)

elif menu == "Cadastrar Item":
    st.header("📝 Cadastrar Nova Questão")
    with st.form("my_form"):
        f = st.text_input("Fonte")
        a = st.text_input("Ano")
        c = st.selectbox("Conteúdo", ["Razão", "Proporção", "Regra de Três", "Escala", "Outros"])
        d = st.select_slider("Dificuldade", ["Fácil", "Média", "Difícil"])
        txt = st.text_area("Texto Base")
        enun = st.text_area("Enunciado")
        alt1 = st.text_input("Alt A")
        alt2 = st.text_input("Alt B")
        alt3 = st.text_input("Alt C")
        alt4 = st.text_input("Alt D")
        alt5 = st.text_input("Alt E")
        gab = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        if st.form_submit_button("Salvar"):
            # Lógica para salvar aqui
            st.success("Questão salva (simulação)!")

elif menu == "Gerar Lista":
    st.header("📄 Visualização para Impressão")
    filtro = st.multiselect("Filtrar por Conteúdo", list(set(q['conteudo'] for q in st.session_state.banco_questoes)))
    
    for q in st.session_state.banco_questoes:
        if not filtro or q['conteudo'] in filtro:
            st.markdown(f"**({q['fonte']} - {q['ano']})**")
            st.write(q['texto_base'])
            st.write(f"**{q['enunciado']}**")
            letras = ["A", "B", "C", "D", "E"]
            for i, alt in enumerate(q['alternativas']):
                st.write(f"{letras[i]}) {alt}")
            st.write("---")
