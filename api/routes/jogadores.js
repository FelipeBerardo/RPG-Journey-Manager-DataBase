// routes/jogadores.js - CRUD de Jogadores
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar todos os jogadores
router.get("/", async (req, res) => {
  try {
    const query = `
      SELECT u.user_id, u.nome_usuario, u.email, u.data_nascimento,
             COUNT(pc.pc_id) as total_personagens,
             COALESCE(SUM(pc.experiencia), 0) as experiencia_total
      FROM USUARIO u
      JOIN JOGADOR j ON j.jogadorUser_id = u.user_id
      LEFT JOIN PC pc ON pc.pc_jogador_id = j.jogadorUser_id
      GROUP BY u.user_id
      ORDER BY experiencia_total DESC
    `;
    const result = await client.query(query);
    console.log(`✅ ${result.rows.length} jogadores enviados!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar jogadores:", err.message);
    res.status(500).json({ error: "Erro ao listar jogadores" });
  }
});

// Buscar jogador por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT u.*, 
             COUNT(pc.pc_id) as total_personagens,
             COALESCE(SUM(pc.experiencia), 0) as experiencia_total
      FROM USUARIO u
      JOIN JOGADOR j ON j.jogadorUser_id = u.user_id
      LEFT JOIN PC pc ON pc.pc_jogador_id = j.jogadorUser_id
      WHERE u.user_id = $1
      GROUP BY u.user_id
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Jogador não encontrado" });
    }
    
    console.log(`✅ Jogador ${result.rows[0].nome_usuario} encontrado!`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erro ao buscar jogador:", err.message);
    res.status(500).json({ error: "Erro ao buscar jogador" });
  }
});

// Listar personagens de um jogador
router.get("/:id/personagens", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT p.personagem_id, p.nome_personagem, p.nivel, pc.experiencia,
             r.nome_raca, c.nome_classe, p.pontos_vida
      FROM PC pc
      JOIN PERSONAGEM p ON p.personagem_id = pc.pc_id
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
      WHERE pc.pc_jogador_id = $1
      ORDER BY pc.experiencia DESC
    `;
    const result = await client.query(query, [id]);
    console.log(`✅ ${result.rows.length} personagens do jogador ${id} enviados!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao buscar personagens:", err.message);
    res.status(500).json({ error: "Erro ao buscar personagens do jogador" });
  }
});

// Criar novo jogador
router.post("/", async (req, res) => {
  try {
    const { nome_usuario, data_nascimento, email } = req.body;
    
    // Primeiro inserir na tabela USUARIO
    const userQuery = `
      INSERT INTO USUARIO (user_id, nome_usuario, data_nascimento, email)
      VALUES ((SELECT COALESCE(MAX(user_id), 0) + 1 FROM USUARIO), $1, $2, $3)
      RETURNING *
    `;
    const userResult = await client.query(userQuery, [nome_usuario, data_nascimento, email]);
    const newUserId = userResult.rows[0].user_id;
    
    // Depois inserir na tabela JOGADOR
    const jogadorQuery = "INSERT INTO JOGADOR (jogadorUser_id) VALUES ($1)";
    await client.query(jogadorQuery, [newUserId]);
    
    console.log(`✅ Jogador ${nome_usuario} criado com sucesso!`);
    res.status(201).json({ jogador: userResult.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao criar jogador:", err.message);
    res.status(500).json({ error: "Erro ao criar jogador", details: err.message });
  }
});

// Atualizar jogador
router.put("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { nome_usuario, email, data_nascimento } = req.body;
    
    const query = `
      UPDATE USUARIO
      SET nome_usuario = COALESCE($1, nome_usuario),
          email = COALESCE($2, email),
          data_nascimento = COALESCE($3, data_nascimento)
      WHERE user_id = $4
      RETURNING *
    `;
    const result = await client.query(query, [nome_usuario, email, data_nascimento, id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Jogador não encontrado" });
    }
    
    console.log(`✅ Jogador ${id} atualizado com sucesso!`);
    res.json({ jogador: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao atualizar jogador:", err.message);
    res.status(500).json({ error: "Erro ao atualizar jogador" });
  }
});

// Deletar jogador
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    
    // Primeiro remove da tabela JOGADOR
    await client.query("DELETE FROM JOGADOR WHERE jogadorUser_id = $1", [id]);
    
    // Depois remove da tabela USUARIO
    const query = "DELETE FROM USUARIO WHERE user_id = $1 RETURNING *";
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Jogador não encontrado" });
    }
    
    console.log(`✅ Jogador ${id} removido com sucesso!`);
    res.json({ message: "Jogador removido", jogador: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao deletar jogador:", err.message);
    res.status(500).json({ error: "Erro ao deletar jogador" });
  }
});

module.exports = router;