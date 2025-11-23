// routes/classes.js - Listar Classes e Habilidades
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar todas as classes com habilidades
router.get("/", async (req, res) => {
  try {
    const query = `
      SELECT c.classe_id, c.nome_classe, c.dado_vida, c.dado_energia, 
             c.descricao_classe,
             json_agg(
               json_build_object(
                 'habilidade_id', h.habilidade_id,
                 'nome', h.nome,
                 'tipo', h.tipo,
                 'custo', h.custo,
                 'descricao', h.descricao
               )
             ) FILTER (WHERE h.habilidade_id IS NOT NULL) as habilidades
      FROM CLASSE c
      LEFT JOIN HABILIDADE h ON h.classeHabilidade_id = c.classe_id
      GROUP BY c.classe_id
      ORDER BY c.nome_classe
    `;
    const result = await client.query(query);
    console.log(`✅ ${result.rows.length} classes enviadas!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar classes:", err.message);
    res.status(500).json({ error: "Erro ao listar classes" });
  }
});

// Buscar classe específica por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT c.classe_id, c.nome_classe, c.dado_vida, c.dado_energia, 
             c.descricao_classe,
             json_agg(
               json_build_object(
                 'habilidade_id', h.habilidade_id,
                 'nome', h.nome,
                 'tipo', h.tipo,
                 'custo', h.custo,
                 'descricao', h.descricao
               )
             ) FILTER (WHERE h.habilidade_id IS NOT NULL) as habilidades
      FROM CLASSE c
      LEFT JOIN HABILIDADE h ON h.classeHabilidade_id = c.classe_id
      WHERE c.classe_id = $1
      GROUP BY c.classe_id
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Classe não encontrada" });
    }
    
    console.log(`✅ Classe ${result.rows[0].nome_classe} encontrada!`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erro ao buscar classe:", err.message);
    res.status(500).json({ error: "Erro ao buscar classe" });
  }
});

module.exports = router;