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
        "Jogadores e Mestres (INTERSECT)",
        "Composição Racial por Classe",
        "Personagens por Jogador",       # Query 1
        "Missões em Progresso",          # Query 2
        "Valor do Inventário",           # Query 3
        "Habilidades por Classe",        # Query 4
        "NPCs por Mestre",               # Query 5
        "Ranking de XP",                 # Query 6
        "Sessões e Missões",             # Query 7
        "Personagens Mais Fortes",       # Query 8
        "Missões Mais Lucrativas",       # Query 9
        "Itens Mais Valiosos",           # Query 10
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

# --- QUERY 1: PERSONAGENS POR JOGADOR (Com Input Dinâmico) ---
elif opcao == "Personagens por Jogador":
    st.subheader("Consultar Personagens de um Jogador")
    
    # Input para substituir o valor fixo 'Travis Willingham'
    nome_jogador = st.text_input("Nome do Jogador:", value="Travis Willingham")
    
    sql_query = """
    SELECT p.nome_personagem, p.nivel, r.nome_raca, c.nome_classe, pc.experiencia
    FROM PERSONAGEM p
    JOIN PC ON pc.pc_id = p.personagem_id
    JOIN JOGADOR j ON j.jogadorUser_id = pc.pc_jogador_id
    JOIN USUARIO u ON u.user_id = j.jogadorUser_id
    JOIN RACA r ON r.raca_id = p.personagemRaca_id
    JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
    WHERE u.nome_usuario = %s;
    """
    
    st.code(sql_query.replace("%s", f"'{nome_jogador}'"), language="sql")
    
    try:
        # O uso de params previne SQL Injection
        df = pd.read_sql(sql_query, conn, params=(nome_jogador,))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nenhum personagem encontrado para este jogador.")
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 2: MISSÕES EM PROGRESSO ---
elif opcao == "Missões em Progresso":
    st.subheader("Monitoramento de Missões Ativas")
    
    sql_query = """
    SELECT m.nome_missao, m.status, p.nome_personagem, u.nome_usuario
    FROM MISSAO m
    JOIN EM_MISSAO em ON em.mMissao_id = m.missao_id
    JOIN PERSONAGEM p ON p.personagem_id = em.mPersonagem_id
    LEFT JOIN PC ON PC.pc_id = p.personagem_id
    LEFT JOIN JOGADOR j ON j.jogadorUser_id = PC.pc_jogador_id
    LEFT JOIN USUARIO u ON u.user_id = j.jogadorUser_id
    WHERE m.status = 'Em Progresso'
    ORDER BY m.missao_id;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 3: VALOR TOTAL DO INVENTÁRIO ---
elif opcao == "Valor do Inventário":
    st.subheader("Auditoria de Riqueza dos Personagens")
    
    sql_query = """
    SELECT p.nome_personagem, SUM(i.valor) as valor_total_inventario, COUNT(i.item_id) as qtd_itens
    FROM PERSONAGEM p
    JOIN INVENTARIO inv ON inv.iPersonagem_id = p.personagem_id
    JOIN ITEM i ON i.proprietario_id = inv.inventario_id
    GROUP BY p.personagem_id, p.nome_personagem
    ORDER BY valor_total_inventario DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
        # Gráfico extra
        st.bar_chart(df.set_index("nome_personagem")["valor_total_inventario"])
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 4: HABILIDADES POR CLASSE ---
elif opcao == "Habilidades por Classe":
    st.subheader("Catálogo de Habilidades")
    
    sql_query = """
    SELECT c.nome_classe, h.nome as habilidade, h.tipo, h.custo, h.descricao
    FROM CLASSE c
    LEFT JOIN HABILIDADE h ON h.classeHabilidade_id = c.classe_id
    ORDER BY c.nome_classe, h.custo;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 5: NPCS POR MESTRE ---
elif opcao == "NPCs por Mestre":
    st.subheader("Criações dos Mestres")
    
    sql_query = """
    SELECT u.nome_usuario as mestre, p.nome_personagem as npc, npc.tipo_NPC, p.nivel
    FROM NPC npc
    JOIN MESTRE m ON m.mestreUser_id = npc.mestreNpc_id
    JOIN USUARIO u ON u.user_id = m.mestreUser_id
    JOIN PERSONAGEM p ON p.personagem_id = npc.npc_id
    ORDER BY u.nome_usuario, p.nivel DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 6: RANKING DE XP ---
elif opcao == "Ranking de XP":
    st.subheader("Leaderboard de Experiência")
    
    sql_query = """
    SELECT u.nome_usuario, p.nome_personagem, pc.experiencia, p.nivel
    FROM PC pc
    JOIN PERSONAGEM p ON p.personagem_id = pc.pc_id
    JOIN JOGADOR j ON j.jogadorUser_id = pc.pc_jogador_id
    JOIN USUARIO u ON u.user_id = j.jogadorUser_id
    ORDER BY pc.experiencia DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 7: SESSÕES E MISSÕES ---
elif opcao == "Sessões e Missões":
    st.subheader("Atividade dos Mestres")
    
    sql_query = """
    SELECT u.nome_usuario as mestre, s.titulo, s.data_criacao, 
           COUNT(m.missao_id) as total_missoes
    FROM SESSAO s
    JOIN MESTRE me ON me.mestreUser_id = s.mUser_id
    JOIN USUARIO u ON u.user_id = me.mestreUser_id
    LEFT JOIN MISSAO m ON m.s_id = s.sessao_id
    GROUP BY u.nome_usuario, s.sessao_id, s.titulo, s.data_criacao
    ORDER BY s.data_criacao;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 8: PERSONAGENS MAIS FORTES ---
elif opcao == "Personagens Mais Fortes":
    st.subheader("Top 10: Soma de Atributos")
    
    sql_query = """
    SELECT nome_personagem, forca, destreza, carisma, sabedoria, inteligencia, 
           (forca + destreza + carisma + sabedoria + inteligencia) as total_atributos
    FROM PERSONAGEM
    ORDER BY total_atributos DESC
    LIMIT 10;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 9: MISSÕES MAIS LUCRATIVAS ---
elif opcao == "Missões Mais Lucrativas":
    st.subheader("Recompensas de Ouro por Missão")
    
    sql_query = """
    SELECT m.nome_missao, m.status, r.qtd_ouro, r.qtd_xp, r.titulo, s.titulo as sessao
    FROM MISSAO m
    JOIN RECOMPENSA r ON r.recompensa_id = m.mRecompensa_id
    JOIN SESSAO s ON s.sessao_id = m.s_id
    ORDER BY r.qtd_ouro DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 10: ITENS MAIS VALIOSOS ---
elif opcao == "Itens Mais Valiosos":
    st.subheader("Top 15 Itens de Maior Valor")
    
    sql_query = """
    SELECT i.nome_item, i.valor, i.tipo_item, p.nome_personagem
    FROM ITEM i
    JOIN INVENTARIO inv ON inv.inventario_id = i.proprietario_id
    JOIN PERSONAGEM p ON p.personagem_id = inv.iPersonagem_id
    ORDER BY i.valor DESC
    LIMIT 15;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na query: {e}")

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