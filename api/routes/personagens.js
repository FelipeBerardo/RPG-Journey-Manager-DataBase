// routes/personagens.js - CRUD de Personagens
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar todos os personagens
router.get("/", async (req, res) => {
  try {
    const query = `
      SELECT p.personagem_id, p.nome_personagem, p.nivel, p.pontos_vida,
             p.destreza, p.forca, p.carisma, p.sabedoria, p.inteligencia,
             r.nome_raca, c.nome_classe
      FROM PERSONAGEM p
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
      ORDER BY p.nivel DESC
    `;
    const result = await client.query(query);
    console.log(`✅ ${result.rows.length} personagens enviados!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar personagens:", err.message);
    res.status(500).json({ error: "Erro ao listar personagens" });
  }
});

// Buscar personagem por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT p.*, r.nome_raca, r.bonus, r.descricao_raca,
             c.nome_classe, c.dado_vida, c.dado_energia, c.descricao_classe
      FROM PERSONAGEM p
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
      WHERE p.personagem_id = $1
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      console.log(`⚠️  Personagem ${id} não encontrado`);
      return res.status(404).json({ message: "Personagem não encontrado" });
    }
    
    console.log(`✅ Personagem ${result.rows[0].nome_personagem} encontrado!`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erro ao buscar personagem:", err.message);
    res.status(500).json({ error: "Erro ao buscar personagem" });
  }
});

// Criar novo personagem
router.post("/", async (req, res) => {
  try {
    const {
      nome_personagem, pontos_vida, nivel, destreza, forca,
      carisma, sabedoria, inteligencia, personagemRaca_id, personagemClasse_id
    } = req.body;

    const query = `
      INSERT INTO PERSONAGEM 
        (personagem_id, nome_personagem, pontos_vida, nivel, destreza, forca, 
         carisma, sabedoria, inteligencia, personagemRaca_id, personagemClasse_id)
      VALUES 
        ((SELECT COALESCE(MAX(personagem_id), 0) + 1 FROM PERSONAGEM), 
         $1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;
    const values = [
      nome_personagem, pontos_vida || 10, nivel || 1, destreza || 10,
      forca || 10, carisma || 10, sabedoria || 10, inteligencia || 10,
      personagemRaca_id, personagemClasse_id
    ];

    const result = await client.query(query, values);
    console.log(`✅ Personagem ${nome_personagem} criado com sucesso!`);
    res.status(201).json({ personagem: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao criar personagem:", err.message);
    res.status(500).json({ error: "Erro ao criar personagem", details: err.message });
  }
});

// Atualizar personagem
router.put("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const {
      nome_personagem, pontos_vida, nivel, destreza, forca,
      carisma, sabedoria, inteligencia
    } = req.body;

    const query = `
      UPDATE PERSONAGEM
      SET nome_personagem = COALESCE($1, nome_personagem),
          pontos_vida = COALESCE($2, pontos_vida),
          nivel = COALESCE($3, nivel),
          destreza = COALESCE($4, destreza),
          forca = COALESCE($5, forca),
          carisma = COALESCE($6, carisma),
          sabedoria = COALESCE($7, sabedoria),
          inteligencia = COALESCE($8, inteligencia)
      WHERE personagem_id = $9
      RETURNING *
    `;
    const values = [
      nome_personagem, pontos_vida, nivel, destreza,
      forca, carisma, sabedoria, inteligencia, id
    ];

    const result = await client.query(query, values);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Personagem não encontrado" });
    }

    console.log(`✅ Personagem ${id} atualizado com sucesso!`);
    res.json({ personagem: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao atualizar personagem:", err.message);
    res.status(500).json({ error: "Erro ao atualizar personagem" });
  }
});

// Deletar personagem
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = "DELETE FROM PERSONAGEM WHERE personagem_id = $1 RETURNING *";
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Personagem não encontrado" });
    }

    console.log(`✅ Personagem ${id} removido com sucesso!`);
    res.json({ message: "Personagem removido", personagem: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao deletar personagem:", err.message);
    res.status(500).json({ error: "Erro ao deletar personagem" });
  }
});

module.exports = router;