// routes/missoes.js - CRUD de Missões
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar todas as missões
router.get("/", async (req, res) => {
  try {
    const query = `
      SELECT m.missao_id, m.nome_missao, m.status, m.descricao_missao,
             s.titulo as sessao, r.qtd_ouro, r.qtd_xp, r.titulo as recompensa_titulo,
             COUNT(em.mPersonagem_id) as total_participantes
      FROM MISSAO m
      JOIN SESSAO s ON s.sessao_id = m.s_id
      JOIN RECOMPENSA r ON r.recompensa_id = m.mRecompensa_id
      LEFT JOIN EM_MISSAO em ON em.mMissao_id = m.missao_id
      GROUP BY m.missao_id, s.titulo, r.qtd_ouro, r.qtd_xp, r.titulo
      ORDER BY m.missao_id
    `;
    const result = await client.query(query);
    console.log(`✅ ${result.rows.length} missões enviadas!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar missões:", err.message);
    res.status(500).json({ error: "Erro ao listar missões" });
  }
});

// Buscar missão por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT m.*, s.titulo as sessao, r.qtd_ouro, r.qtd_xp, 
             r.qtd_reputacao, r.titulo as recompensa_titulo
      FROM MISSAO m
      JOIN SESSAO s ON s.sessao_id = m.s_id
      JOIN RECOMPENSA r ON r.recompensa_id = m.mRecompensa_id
      WHERE m.missao_id = $1
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Missão não encontrada" });
    }
    
    // Buscar participantes da missão
    const participantesQuery = `
      SELECT p.personagem_id, p.nome_personagem, p.nivel
      FROM EM_MISSAO em
      JOIN PERSONAGEM p ON p.personagem_id = em.mPersonagem_id
      WHERE em.mMissao_id = $1
    `;
    const participantes = await client.query(participantesQuery, [id]);
    
    const missao = {
      ...result.rows[0],
      participantes: participantes.rows
    };
    
    console.log(`✅ Missão ${missao.nome_missao} encontrada!`);
    res.json(missao);
  } catch (err) {
    console.error("❌ Erro ao buscar missão:", err.message);
    res.status(500).json({ error: "Erro ao buscar missão" });
  }
});

// Filtrar missões por status
router.get("/status/:status", async (req, res) => {
  try {
    const { status } = req.params;
    const query = `
      SELECT m.missao_id, m.nome_missao, m.descricao_missao, 
             s.titulo as sessao, COUNT(em.mPersonagem_id) as participantes
      FROM MISSAO m
      JOIN SESSAO s ON s.sessao_id = m.s_id
      LEFT JOIN EM_MISSAO em ON em.mMissao_id = m.missao_id
      WHERE LOWER(m.status) = LOWER($1)
      GROUP BY m.missao_id, s.titulo
      ORDER BY m.missao_id
    `;
    const result = await client.query(query, [status]);
    console.log(`✅ ${result.rows.length} missões com status '${status}' enviadas!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao filtrar missões:", err.message);
    res.status(500).json({ error: "Erro ao filtrar missões" });
  }
});

// Criar nova missão
router.post("/", async (req, res) => {
  try {
    const {
      nome_missao, descricao_missao, status, s_id,
      qtd_ouro, qtd_xp, qtd_reputacao, titulo_recompensa
    } = req.body;
    
    // Primeiro criar a recompensa
    const recompensaQuery = `
      INSERT INTO RECOMPENSA 
        (recompensa_id, qtd_ouro, qtd_xp, qtd_reputacao, titulo)
      VALUES 
        ((SELECT COALESCE(MAX(recompensa_id), 0) + 1 FROM RECOMPENSA),
         $1, $2, $3, $4)
      RETURNING recompensa_id
    `;
    const recompensaResult = await client.query(recompensaQuery, [
      qtd_ouro || 0, qtd_xp || 0, qtd_reputacao || 0, titulo_recompensa
    ]);
    const recompensaId = recompensaResult.rows[0].recompensa_id;
    
    // Depois criar a missão
    const missaoQuery = `
      INSERT INTO MISSAO 
        (missao_id, nome_missao, status, descricao_missao, s_id, mRecompensa_id)
      VALUES 
        ((SELECT COALESCE(MAX(missao_id), 0) + 1 FROM MISSAO),
         $1, $2, $3, $4, $5)
      RETURNING *
    `;
    const missaoResult = await client.query(missaoQuery, [
      nome_missao, status || 'Aberta', descricao_missao, s_id, recompensaId
    ]);
    
    console.log(`✅ Missão ${nome_missao} criada com sucesso!`);
    res.status(201).json({ missao: missaoResult.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao criar missão:", err.message);
    res.status(500).json({ error: "Erro ao criar missão", details: err.message });
  }
});

// Atualizar missão
router.put("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { nome_missao, status, descricao_missao } = req.body;
    
    const query = `
      UPDATE MISSAO
      SET nome_missao = COALESCE($1, nome_missao),
          status = COALESCE($2, status),
          descricao_missao = COALESCE($3, descricao_missao)
      WHERE missao_id = $4
      RETURNING *
    `;
    const result = await client.query(query, [nome_missao, status, descricao_missao, id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Missão não encontrada" });
    }
    
    console.log(`✅ Missão ${id} atualizada com sucesso!`);
    res.json({ missao: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao atualizar missão:", err.message);
    res.status(500).json({ error: "Erro ao atualizar missão" });
  }
});

// Deletar missão
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    
    // Primeiro buscar o ID da recompensa
    const getRecompensa = await client.query(
      "SELECT mRecompensa_id FROM MISSAO WHERE missao_id = $1", 
      [id]
    );
    
    if (getRecompensa.rows.length === 0) {
      return res.status(404).json({ message: "Missão não encontrada" });
    }
    
    const recompensaId = getRecompensa.rows[0].mrecompensa_id;
    
    // Remover vínculos em EM_MISSAO
    await client.query("DELETE FROM EM_MISSAO WHERE mMissao_id = $1", [id]);
    
    // Remover a missão
    const result = await client.query(
      "DELETE FROM MISSAO WHERE missao_id = $1 RETURNING *", 
      [id]
    );
    
    // Remover a recompensa
    await client.query("DELETE FROM RECOMPENSA WHERE recompensa_id = $1", [recompensaId]);
    
    console.log(`✅ Missão ${id} removida com sucesso!`);
    res.json({ message: "Missão removida", missao: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao deletar missão:", err.message);
    res.status(500).json({ error: "Erro ao deletar missão" });
  }
});

module.exports = router;