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

# Lista expandida com os conceitos dos PDFs
opcao = st.sidebar.radio(
    "Escolha a Operação:",
    [
        "Listar Personagens (JOIN)", 
        "Estatísticas de Raça (GROUP BY)", 
        "Jogadores e Mestres (INTERSECT)",
        "Composição Racial por Classe",
        "Personagens por Jogador",       
        "Missões em Progresso",           
        "Valor do Inventário",           
        "Habilidades por Classe",        
        "NPCs por Mestre",               
        "Ranking de XP",                 
        "Sessões e Missões",             
        "Personagens Mais Fortes",       
        "Missões Mais Lucrativas",       
        "Itens Mais Valiosos",
        # --- NOVAS OPÇÕES ADICIONADAS ---
        "Busca de Itens (LIKE)",          # Conceito: Padrão de String
        "Classificação de Poder (CASE)",  # Conceito: Condicional
        "Quem nunca jogou? (NOT EXISTS)", # Conceito: Subquery Correlacionada
        "Média de Riqueza (WITH/CTE)",    # Conceito: Tabela Temporária
        "Curar Personagem (UPDATE)",      # Conceito: Modificação de dados
        "Deletar Item (DELETE)",          # Conceito: Remoção de dados
        # -------------------------------
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

# --- QUERY 3: PERSONAGENS POR JOGADOR (Com Input Dinâmico) ---
elif opcao == "Personagens por Jogador":
    st.subheader("Consultar Personagens de um Jogador")
    
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
        df = pd.read_sql(sql_query, conn, params=(nome_jogador,))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nenhum personagem encontrado para este jogador.")
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 4: MISSÕES EM PROGRESSO ---
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

# --- QUERY 5: VALOR TOTAL DO INVENTÁRIO ---
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
        st.bar_chart(df.set_index("nome_personagem")["valor_total_inventario"])
    except Exception as e:
        st.error(f"Erro na query: {e}")

# --- QUERY 6: HABILIDADES POR CLASSE ---
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

# --- QUERY 7: NPCS POR MESTRE ---
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

# --- QUERY 8: RANKING DE XP ---
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

# --- QUERY 9: SESSÕES E MISSÕES ---
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

# --- QUERY 10: PERSONAGENS MAIS FORTES ---
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

# --- QUERY 11: MISSÕES MAIS LUCRATIVAS ---
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

# --- QUERY 12: ITENS MAIS VALIOSOS ---
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

# --- QUERY 13: JOGADORES QUE SÃO MESTRES (INTERSECT) ---
elif opcao == "Jogadores e Mestres (INTERSECT)":
    st.subheader("Usuários Híbridos (Jogadores & Mestres)")
    st.info("Esta query identifica usuários que possuem papéis duplicados no sistema.")

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

# --- QUERY 14: COMPOSIÇÃO RACIAL POR CLASSE ---
elif opcao == "Composição Racial por Classe":
    st.subheader("Análise Demográfica: Raça x Classe")
    st.info("Agrupamento duplo para entender quais raças preferem quais classes.")

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
        st.dataframe(df, use_container_width=True)
        st.caption("Visualização Gráfica")
        st.bar_chart(df, x="nome_classe", y="quantidade", color="nome_raca", stack=False)
    except Exception as e:
        st.error(f"Erro no SQL: {e}")

# --- NOVO: BUSCA DE ITENS (LIKE) ---
elif opcao == "Busca de Itens (LIKE)":
    st.subheader("Busca Textual em Itens")
    st.info("Conceito: Padrão de String com LIKE (Slide 7 - pg 9)")
    
    termo = st.text_input("Digite o nome (ou parte) do item:", value="Espada")
    
    # O uso de % ao redor do termo permite buscar em qualquer parte da string
    sql_query = """
    SELECT i.nome_item, i.tipo_item, i.valor, i.descricao_item 
    FROM ITEM i 
    WHERE i.nome_item ILIKE %s; 
    """
    # ILIKE é específico do Postgres para Case Insensitive. No SQL padrão seria LIKE.
    
    st.code(sql_query.replace("%s", f"'%{termo}%'"), language="sql")
    
    if st.button("Pesquisar Item"):
        try:
            df = pd.read_sql(sql_query, conn, params=(f"%{termo}%",))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum item encontrado com esse nome.")
        except Exception as e:
            st.error(f"Erro: {e}")

# --- NOVO: CLASSIFICAÇÃO DE PODER (CASE) ---
elif opcao == "Classificação de Poder (CASE)":
    st.subheader("Classificação de Jogadores por XP")
    st.info("Conceito: Lógica Condicional com CASE WHEN (Slide 8 - pg 37)")
    
    sql_query = """
    SELECT p.nome_personagem, pc.experiencia,
           CASE 
               WHEN pc.experiencia < 1000 THEN 'Novato'
               WHEN pc.experiencia BETWEEN 1000 AND 10000 THEN 'Aventureiro'
               WHEN pc.experiencia BETWEEN 10001 AND 50000 THEN 'Veterano'
               ELSE 'Lenda Viva'
           END as rank_poder
    FROM PC pc
    JOIN PERSONAGEM p ON p.personagem_id = pc.pc_id
    ORDER BY pc.experiencia DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")

# --- NOVO: QUEM NUNCA JOGOU? (NOT EXISTS) ---
elif opcao == "Quem nunca jogou? (NOT EXISTS)":
    st.subheader("Personagens Ociosos")
    st.info("Conceito: Subquery Correlacionada e NOT EXISTS (Slide 8 - pg 11)")
    
    # Encontra personagens que NÃO estão na tabela EM_MISSAO
    sql_query = """
    SELECT p.nome_personagem, c.nome_classe
    FROM PERSONAGEM p
    JOIN CLASSE c ON p.personagemClasse_id = c.classe_id
    WHERE NOT EXISTS (
        SELECT 1 
        FROM EM_MISSAO em 
        WHERE em.mPersonagem_id = p.personagem_id
    );
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")

# --- NOVO: MÉDIA DE RIQUEZA (WITH/CTE) ---
elif opcao == "Média de Riqueza (WITH/CTE)":
    st.subheader("Personagens Acima da Média de Ouro")
    st.info("Conceito: Common Table Expressions - WITH (Slide 8 - pg 36)")
    
    # 1. CTE calcula o total de ouro de cada um
    # 2. Select principal filtra quem tem mais que a média
    sql_query = """
    WITH RiquezaPersonagem AS (
        SELECT p.nome_personagem, SUM(i.valor) as total_ouro
        FROM PERSONAGEM p
        JOIN INVENTARIO inv ON inv.iPersonagem_id = p.personagem_id
        JOIN ITEM i ON i.proprietario_id = inv.inventario_id
        GROUP BY p.nome_personagem
    )
    SELECT nome_personagem, total_ouro
    FROM RiquezaPersonagem
    WHERE total_ouro > (SELECT AVG(total_ouro) FROM RiquezaPersonagem)
    ORDER BY total_ouro DESC;
    """
    
    st.code(sql_query, language="sql")
    try:
        df = pd.read_sql(sql_query, conn)
        st.metric("Média Geral de Ouro", f"{df['total_ouro'].mean():.2f} PO")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")

# --- NOVO: CURAR PERSONAGEM (UPDATE) ---
elif opcao == "Curar Personagem (UPDATE)":
    st.subheader("Curar Personagem (UPDATE)")
    st.info("Conceito: Atualização de Dados (Slide 7 - pg 18)")
    
    # Selecionar Personagem
    try:
        chars = pd.read_sql("SELECT personagem_id, nome_personagem, pontos_vida FROM PERSONAGEM", conn)
        char_select = st.selectbox("Escolha o Personagem:", chars['nome_personagem'])
        char_data = chars[chars['nome_personagem'] == char_select].iloc[0]
        
        st.write(f"PV Atual: {char_data['pontos_vida']}")
        
        with st.form("cura_form"):
            novo_pv = st.number_input("Novo valor de PV:", min_value=1, value=int(char_data['pontos_vida']))
            submit_cura = st.form_submit_button("Atualizar PV")
            
            if submit_cura:
                cursor = conn.cursor()
                sql_update = """
                UPDATE PERSONAGEM 
                SET pontos_vida = %s 
                WHERE personagem_id = %s;
                """
                try:
                    cursor.execute(sql_update, (novo_pv, int(char_data['personagem_id'])))
                    conn.commit()
                    st.success(f"PV de {char_select} atualizado para {novo_pv}!")
                    cursor.close()
                    st.rerun() # Recarrega a página para mostrar valor novo
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao atualizar: {e}")
                    
    except Exception as e:
        st.error("Erro ao carregar lista de personagens.")

# --- NOVO: DELETAR ITEM (DELETE) ---
elif opcao == "Deletar Item (DELETE)":
    st.subheader("Remover Item do Mundo (DELETE)")
    st.warning("Ação Irreversível! Conceito: Remoção de Dados (Slide 7 - pg 17)")
    
    # Listar itens para deletar
    try:
        items = pd.read_sql("SELECT item_id, nome_item, proprietario_id FROM ITEM ORDER BY item_id DESC LIMIT 50", conn)
        item_id_to_delete = st.selectbox("Escolha o ID do Item para Deletar:", items['item_id'])
        
        # Mostra detalhes do item selecionado
        item_detalhe = items[items['item_id'] == item_id_to_delete].iloc[0]
        st.write(f"Item: **{item_detalhe['nome_item']}** (Proprietário Inv ID: {item_detalhe['proprietario_id']})")
        
        if st.button("Confirmar Deleção"):
            cursor = conn.cursor()
            sql_delete = "DELETE FROM ITEM WHERE item_id = %s;"
            try:
                cursor.execute(sql_delete, (int(item_id_to_delete),))
                conn.commit()
                st.success(f"Item {item_id_to_delete} removido com sucesso.")
                cursor.close()
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Erro ao deletar: {e}")
                
    except Exception as e:
        st.error("Erro ao carregar itens.")


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