import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import base64

# Configurações da página
st.set_page_config(page_title="Gestor de Provas IFCE", layout="wide", page_icon="📝")

# --- CONEXÃO E DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(ttl=0)
df = df_raw.copy()
df.columns = [c.lower().strip().replace('ú', 'u') for c in df.columns]

# --- ESTILO CSS PARA OCULTAR INTERFACE NA IMPRESSÃO ---
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stHeader"], .stTabs, .no-print {
            display: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Sistema de Gestão de Itens - IFCE")

# Controle de Aba via Session State para evitar redirecionamento
if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = 0

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

# --- ABA 3: GERAR PROVA ---
with abas[2]:
    st.header("Gerador de Documento")
    
    if not df.empty:
        # Filtros de Seleção
        c1, c2 = st.columns(2)
        temas = c1.multiselect("Filtrar Conteúdo", df['conteudo'].unique(), key="m_tema")
        niveis = c2.multiselect("Filtrar Dificuldade", df['dificuldade'].unique(), key="m_nivel")
        
        df_f = df.copy()
        if temas: df_f = df_f[df_f['conteudo'].isin(temas)]
        if niveis: df_f = df_f[df_f['dificuldade'].isin(niveis)]

        st.divider()
        
        # Opções de Organização
        col_ord1, col_ord2 = st.columns([1, 2])
        ordem_manual = col_ord2.text_input("Ordem manual dos IDs (ex: 5, 1, 3):", help="Digite os IDs das questões separados por vírgula para definir a ordem exata.")
        
        if col_ord1.button("🎲 Sortear do Filtro"):
            questoes_sorteadas = df_f.sample(frac=1).head(10) # Sorteia até 10 do filtro
            st.session_state.prova_ids = questoes_sorteadas['id'].tolist()
        
        if ordem_manual:
            try:
                ids_lista = [int(x.strip()) for x in ordem_manual.split(",")]
                st.session_state.prova_ids = ids_lista
            except:
                st.error("Formato de IDs inválido. Use números separados por vírgula.")

        # Construção da Prova Final
        if 'prova_ids' in st.session_state:
            df_prova = df[df['id'].isin(st.session_state.prova_ids)].set_index('id').loc[st.session_state.prova_ids].reset_index()
            
            st.subheader(f"Lista Atual: {len(df_prova)} questões")
            
            # Gerador de HTML para Impressão em Nova Aba
            conteudo_prova_html = f"""
            <html><head><title>Prova de Matemática</title>
            <style>
                body {{ font-family: Arial; padding: 40px; line-height: 1.6; }}
                .header {{ text-align: center; border-bottom: 2px solid black; margin-bottom: 20px; }}
                .question {{ margin-bottom: 30px; page-break-inside: avoid; }}
                .footer {{ margin-top: 50px; font-size: 0.8em; border-top: 1px solid #ccc; }}
            </style></head><body>
            <div class='header'>
                <h2>LISTA DE EXERCÍCIOS - MATEMÁTICA</h2>
                <p style='text-align: left;'>NOME: _________________________________________________ DATA: ___/___/___</p>
                <p style='text-align: left;'>PROFESSOR: ____________________________________________ TURMA: _________</p>
            </div>
            """
            
            for i, row in df_prova.iterrows():
                conteudo_prova_html += f"<div class='question'><b>Questão {i+1} ({row['fonte']} / {row['ano']})</b><br>"
                conteudo_prova_html += f"<p>{row['texto_base']}</p><b>{row['enunciado']}</b><br><ul>"
                alts = row['alternativas'].split(';')
                letras = ["A", "B", "C", "D", "E"]
                for idx, alt in enumerate(alts):
                    if idx < 5: conteudo_prova_html += f"<li>{letras[idx]}) {alt.strip()}</li>"
                conteudo_prova_html += "</ul></div>"
            
            conteudo_prova_html += "</body><script>window.print();</script></html>"
            
            # Botão que abre a nova aba com o HTML
            b64 = base64.b64encode(conteudo_prova_html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;"><button style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">🖨️ ABRIR PROVA PARA IMPRESSÃO</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Visualização na página
            st.info("Abaixo está uma prévia. Use o botão vermelho acima para abrir a versão de impressão.")
            for i, row in df_prova.iterrows():
                st.markdown(f"**Q{i+1} (ID: {row['id']})** - {row['enunciado'][:50]}...")

    else:
        st.warning("Banco de dados vazio.")
