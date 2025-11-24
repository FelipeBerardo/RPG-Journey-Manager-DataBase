import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Configuração da Página
st.set_page_config(page_title="RPG Manager", layout="wide")
load_dotenv()

# 2. Conexão com o Banco (Cacheada para não reconectar a cada clique)
@st.cache_resource
def init_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

conn = init_connection()

# --- Título e Sidebar ---
st.title("🐉 Gerenciador de RPG - Banco de Dados")
st.sidebar.header("Menu de Queries")
opcao = st.sidebar.radio(
    "Escolha a Operação:",
    ["Listar Personagens (JOIN)", "Estatísticas de Raça (GROUP BY)", "Buscar por ID (WHERE)", "Inserir Item (INSERT)"]
)

# --- QUERY 1: JOIN (Aquelas complexas que você tem salvas) ---
if opcao == "Listar Personagens (JOIN)":
    st.subheader("Fichas de Personagens Completas")
    
    # Cole aqui a query EXATA que você testou no SQL Editor
    sql_query = """
    SELECT 
        p.personagem_id,
        p.nome_personagem,
        p.nivel,
        p.pontos_vida as PV,
        r.nome_raca as Raca,
        c.nome_classe as Classe
    FROM personagem p
    INNER JOIN raca r ON p.personagemraca_id = r.raca_id
    LEFT JOIN classe c ON p.personagemclasse_id = c.classe_id
    ORDER BY p.nivel DESC;
    """
    
    # st.code mostra o SQL na tela (ótimo para mostrar ao professor)
    st.code(sql_query, language="sql")
    
    # Executa e joga direto num DataFrame (Tabela bonita)
    df = pd.read_sql(sql_query, conn)
    st.dataframe(df, use_container_width=True)

# --- QUERY 2: AGGREGAÇÃO (GROUP BY) ---
elif opcao == "Estatísticas de Raça (GROUP BY)":
    st.subheader("Distribuição de Raças no Mundo")
    
    sql_query = """
    SELECT 
        r.nome_raca, 
        COUNT(p.personagem_id) as total_jogadores,
        ROUND(AVG(p.nivel), 1) as media_nivel
    FROM raca r
    LEFT JOIN personagem p ON r.raca_id = p.personagemraca_id
    GROUP BY r.nome_raca
    HAVING COUNT(p.personagem_id) > 0
    ORDER BY total_jogadores DESC;
    """
    
    st.code(sql_query, language="sql")
    df = pd.read_sql(sql_query, conn)
    
    # Mostra tabela e um gráfico de barras simples
    col1, col2 = st.columns([1, 2])
    col1.dataframe(df)
    col2.bar_chart(df.set_index("nome_raca")["total_jogadores"])

# --- QUERY 3: FILTRO (WHERE) ---
elif opcao == "Buscar por ID (WHERE)":
    st.subheader("Buscar Detalhes do Personagem")
    
    char_id = st.number_input("Digite o ID do Personagem:", min_value=1, step=1)
    
    if st.button("Buscar"):
        cursor = conn.cursor()
        sql = "SELECT * FROM personagem WHERE personagem_id = %s;"
        
        cursor.execute(sql, (char_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            st.success("Personagem encontrado!")
            st.write(resultado)
        else:
            st.error("Personagem não encontrado.")
        cursor.close()

# --- QUERY 4: INSERT (Transação) ---
elif opcao == "Inserir Item (INSERT)":
    st.subheader("Criar Novo Item Lendário")
    
    with st.form("form_item"):
        nome = st.text_input("Nome do Item")
        peso = st.number_input("Peso", min_value=1)
        valor = st.number_input("Valor (PO)", min_value=0)
        tipo = st.selectbox("Tipo", ["Arma", "Armadura", "Poção", "Artefato"])
        # Aqui você teria que listar os IDs de inventário disponíveis ou digitar manual
        proprietario = st.number_input("ID do Inventário do Dono", min_value=1)
        
        submitted = st.form_submit_button("Salvar no Banco")
        
        if submitted:
            try:
                cursor = conn.cursor()
                sql = """
                INSERT INTO item (nome_item, peso, valor, tipo_item, proprietario_id)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(sql, (nome, peso, valor, tipo, proprietario))
                conn.commit() # Confirma a transação
                st.toast("Item inserido com sucesso!", icon="✅")
                cursor.close()
            except Exception as e:
                st.error(f"Erro ao inserir: {e}")
                conn.rollback() # Cancela se der erro