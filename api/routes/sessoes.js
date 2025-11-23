// routes/sessoes.js - Gerenciar Sessões de Jogo
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar todas as sessões
router.get("/", async (req, res) => {
  try {
    const query = `
      SELECT s.sessao_id, s.titulo, s.data_criacao, u.nome_usuario as mestre,
             COUNT(m.missao_id) as total_missoes
      FROM SESSAO s
      JOIN MESTRE me ON me.mestreUser_id = s.mUser_id
      JOIN USUARIO u ON u.user_id = me.mestreUser_id
      LEFT JOIN MISSAO m ON m.s_id = s.sessao_id
      GROUP BY s.sessao_id, u.nome_usuario
      ORDER BY s.data_criacao DESC
    `;
    const result = await client.query(query);
    console.log(`✅ ${result.rows.length} sessões enviadas!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar sessões:", err.message);
    res.status(500).json({ error: "Erro ao listar sessões" });
  }
});

// Buscar sessão por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT s.*, u.nome_usuario as mestre
      FROM SESSAO s
      JOIN MESTRE me ON me.mestreUser_id = s.mUser_id
      JOIN USUARIO u ON u.user_id = me.mestreUser_id
      WHERE s.sessao_id = $1
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Sessão não encontrada" });
    }
    
    console.log(`✅ Sessão ${result.rows[0].titulo} encontrada!`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erro ao buscar sessão:", err.message);
    res.status(500).json({ error: "Erro ao buscar sessão" });
  }
});

// Criar nova sessão
router.post("/", async (req, res) => {
  try {
    const { titulo, mUser_id, data_criacao } = req.body;
    const query = `
      INSERT INTO SESSAO (sessao_id, titulo, data_criacao, mUser_id)
      VALUES ((SELECT COALESCE(MAX(sessao_id), 0) + 1 FROM SESSAO), $1, $2, $3)
      RETURNING *
    `;
    const result = await client.query(query, [titulo, data_criacao || new Date(), mUser_id]);
    console.log(`✅ Sessão ${titulo} criada com sucesso!`);
    res.status(201).json({ sessao: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao criar sessão:", err.message);
    res.status(500).json({ error: "Erro ao criar sessão", details: err.message });
  }
});

module.exports = router;