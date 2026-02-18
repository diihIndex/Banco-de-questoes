import streamlit as st

# Page configuration
st.set_page_config(page_title='Banco de Questões', layout='wide')

# Initialize session state with sample questions
if 'questions' not in st.session_state:
    st.session_state.questions = [
        {'ano': 2020, 'conteudo': 'Razão', 'dificuldade': 'Fácil', 'texto_base': 'Texto exemplo da questão sobre razão.', 'enunciado': 'Qual é a razão entre A e B?', 'alternativas': {'A': 'Alternativa 1', 'B': 'Alternativa 2', 'C': 'Alternativa 3', 'D': 'Alternativa 4', 'E': 'Alternativa 5'}},
        {'ano': 2021, 'conteudo': 'Regra de Três', 'dificuldade': 'Médio', 'texto_base': 'Texto exemplo da questão sobre regra de três.', 'enunciado': 'Como utilizar a regra de três neste caso?', 'alternativas': {'A': 'Alternativa 1', 'B': 'Alternativa 2', 'C': 'Alternativa 3', 'D': 'Alternativa 4', 'E': 'Alternativa 5'}},
        {'ano': 2026, 'conteudo': 'Escala', 'dificuldade': 'Difícil', 'texto_base': 'Texto exemplo da questão sobre escala.', 'enunciado': 'Qual é a escala correta a ser usada?', 'alternativas': {'A': 'Alternativa 1', 'B': 'Alternativa 2', 'C': 'Alternativa 3', 'D': 'Alternativa 4', 'E': 'Alternativa 5'}},
    ]

# Menu options
menu = st.sidebar.selectbox('Menu', ['Ver Banco de Questões', 'Cadastrar Nova Questão', 'Gerar Atividade', 'Sobre'])

if menu == 'Ver Banco de Questões':
    st.title('Banco de Questões')
    # Filters
    filter_content = st.selectbox('Filtrar por Conteúdo', ['Todos', 'Razão', 'Regra de Três', 'Escala'])
    filter_difficulty = st.selectbox('Filtrar por Dificuldade', ['Todos', 'Fácil', 'Médio', 'Difícil'])
    filter_year = st.selectbox('Filtrar por Ano', ['Todos', 2020, 2021, 2026])
 
    # Display questions
    for question in st.session_state.questions:
        if (filter_content == 'Todos' or question['conteudo'] == filter_content) and 
           (filter_difficulty == 'Todos' or question['dificuldade'] == filter_difficulty) and 
           (filter_year == 'Todos' or question['ano'] == filter_year):
            st.write(question['texto_base'])
            st.write(question['enunciado'])
            for k, v in question['alternativas'].items():
                st.write(f'{k}: {v}')

elif menu == 'Cadastrar Nova Questão':
    st.title('Cadastrar Nova Questão')
    # Form for new question
    with st.form(key='new_question_form'):
        fonte = st.text_input('Fonte')
        ano = st.number_input('Ano', min_value=2000, max_value=2026)
        conteudo = st.selectbox('Conteúdo', ['Razão', 'Regra de Três', 'Escala'])
        dificuldade = st.selectbox('Dificuldade', ['Fácil', 'Médio', 'Difícil'])
        texto_base = st.text_area('Texto Base')
        enunciado = st.text_area('Enunciado')
        alternativas = {k: st.text_input(f'Alternativa {k}') for k in ['A', 'B', 'C', 'D', 'E']}
        submit_button = st.form_submit_button(label='Cadastrar')
        if submit_button:
            st.session_state.questions.append({
                'fonte': fonte,
                'ano': ano,
                'conteudo': conteudo,
                'dificuldade': dificuldade,
                'texto_base': texto_base,
                'enunciado': enunciado,
                'alternativas': alternativas,
            })
            st.success('Questão cadastrada com sucesso!')

elif menu == 'Gerar Atividade':
    st.title('Gerar Atividade')
    # Functionality to generate exams
    st.write('Função de geração de atividades não implementada.')

elif menu == 'Sobre':
    st.title('Sobre')
    st.write('Esta aplicação permite gerenciar questões de provas do IFCE.')
    st.write('Versão: 1.0')