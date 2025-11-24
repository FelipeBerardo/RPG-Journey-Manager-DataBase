import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Configuração da Página
st.set_page_config(page_title="RPG Manager", layout="wide")
load_dotenv()

# 2. Conexão com o Banco
@st.cache_resource
def init_connection():
    # Verifica se a URL existe para evitar erro
    if "DATABASE_URL" not in os.environ:
        st.error("Erro: DATABASE_URL não encontrada no arquivo .env")
        st.stop()
    return psycopg2.connect(os.environ["DATABASE_URL"])

try:
    conn = init_connection()
except Exception as e:
    st.error(f"Erro ao conectar no banco: {e}")
    st.stop()

# --- Título e Sidebar ---
st.title("🐉 Gerenciador de RPG - Banco de Dados")
st.sidebar.header("Menu de Queries")

# Adicionei as novas opções na lista
opcao = st.sidebar.radio(
    "Escolha a Operação:",
    [
        "Listar Personagens (JOIN)", 
        "Estatísticas de Raça (GROUP BY)", 
        "Jogadores e Mestres (INTERSECT)",   # NOVA
        "Composição Racial por Classe",      # NOVA
        "Buscar por ID (WHERE)", 
        "Inserir Item (INSERT)"
    ]
)

# --- QUERY 1: JOIN (Fichas) ---
if opcao == "Listar Personagens (JOIN)":
    st.subheader("Fichas de Personagens Completas")
    
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
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 2: ESTATÍSTICAS (GROUP BY Simples) ---
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
    
    col1, col2 = st.columns([1, 2])
    col1.dataframe(df)
    col2.bar_chart(df.set_index("nome_raca")["total_jogadores"])

# --- NOVA QUERY: JOGADORES QUE SÃO MESTRES ---
elif opcao == "Jogadores e Mestres (INTERSECT)":
    st.subheader("Usuários Híbridos (Jogadores & Mestres)")
    st.info("Esta query identifica usuários que possuem papéis duplicados no sistema.")

    # Convertido para minúsculo para compatibilidade
    sql_query = """
    SELECT u.nome_usuario, 
       CASE WHEN m.mestreuser_id IS NOT NULL THEN 'Sim' ELSE 'Não' END as eh_mestre,
       CASE WHEN j.jogadoruser_id IS NOT NULL THEN 'Sim' ELSE 'Não' END as eh_jogador
    FROM usuario u
    LEFT JOIN mestre m ON m.mestreuser_id = u.user_id
    LEFT JOIN jogador j ON j.jogadoruser_id = u.user_id
    WHERE m.mestreuser_id IS NOT NULL AND j.jogadoruser_id IS NOT NULL;
    """

    st.code(sql_query, language="sql")
    
    try:
        df = pd.read_sql(sql_query, conn)
        if not df.empty:
            st.success(f"Encontrados {len(df)} usuários com função dupla.")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nenhum usuário encontrado com as duas funções.")
    except Exception as e:
        st.error(f"Erro no SQL: {e}")

# --- NOVA QUERY: COMPOSIÇÃO RACIAL POR CLASSE ---
elif opcao == "Composição Racial por Classe":
    st.subheader("Análise Demográfica: Raça x Classe")
    st.info("Agrupamento duplo para entender quais raças preferem quais classes.")

    # Convertido para minúsculo
    sql_query = """
    SELECT c.nome_classe, r.nome_raca, COUNT(*) as quantidade
    FROM personagem p
    JOIN classe c ON c.classe_id = p.personagemclasse_id
    JOIN raca r ON r.raca_id = p.personagemraca_id
    GROUP BY c.nome_classe, r.nome_raca
    ORDER BY c.nome_classe, quantidade DESC;
    """

    st.code(sql_query, language="sql")
    
    try:
        df = pd.read_sql(sql_query, conn)
        
        # Exibição lado a lado (Tabela e Gráfico)
        st.dataframe(df, use_container_width=True)
        
        # Um gráfico de barras empilhadas fica ótimo aqui
        st.caption("Visualização Gráfica")
        st.bar_chart(
            df, 
            x="nome_classe", 
            y="quantidade", 
            color="nome_raca", # Isso cria cores diferentes para cada raça
            stack=False # Mude para True se quiser barras empilhadas
        )
    except Exception as e:
        st.error(f"Erro no SQL: {e}")

# --- QUERY: FILTRO (WHERE) ---
elif opcao == "Buscar por ID (WHERE)":
    st.subheader("Buscar Detalhes do Personagem")
    
    char_id = st.number_input("Digite o ID do Personagem:", min_value=1, step=1)
    
    if st.button("Buscar"):
        cursor = conn.cursor()
        sql = "SELECT * FROM personagem WHERE personagem_id = %s;"
        
        try:
            cursor.execute(sql, (char_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                st.success("Personagem encontrado!")
                # Mostra o resultado formatado
                st.write(resultado)
            else:
                st.error("Personagem não encontrado.")
        except Exception as e:
            st.error(f"Erro: {e}")
        finally:
            cursor.close()

# --- QUERY: INSERT (Transação) ---
elif opcao == "Inserir Item (INSERT)":
    st.subheader("Criar Novo Item Lendário")
    
    with st.form("form_item"):
        nome = st.text_input("Nome do Item")
        peso = st.number_input("Peso", min_value=1)
        valor = st.number_input("Valor (PO)", min_value=0)
        tipo = st.selectbox("Tipo", ["Arma", "Armadura", "Poção", "Artefato"])
        proprietario = st.number_input("ID do Inventário do Dono", min_value=1)
        
        submitted = st.form_submit_button("Salvar no Banco")
        
        if submitted:
            try:
                cursor = conn.cursor()
                # INSERT com RETURNING para confirmar o ID criado (boa prática)
                sql = """
                INSERT INTO item (nome_item, peso, valor, tipo_item, proprietario_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING item_id;
                """
                cursor.execute(sql, (nome, peso, valor, tipo, proprietario))
                new_id = cursor.fetchone()[0]
                conn.commit()
                st.toast(f"Item criado! ID: {new_id}", icon="✅")
                cursor.close()
            except Exception as e:
                st.error(f"Erro ao inserir: {e}")
                conn.rollback()