// routes/npcs.js - NPCs por Mestre
const express = require("express");
const router = express.Router();
const client = require("../database");

// Listar NPCs de um mestre específico
router.get("/mestre/:mestre_id", async (req, res) => {
  try {
    const { mestre_id } = req.params;
    const query = `
      SELECT p.personagem_id, p.nome_personagem, npc.tipo_NPC, 
             p.nivel, p.pontos_vida, r.nome_raca, c.nome_classe,
             p.forca, p.destreza, p.carisma, p.sabedoria, p.inteligencia
      FROM NPC npc
      JOIN PERSONAGEM p ON p.personagem_id = npc.npc_id
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
      WHERE npc.mestreNpc_id = $1
      ORDER BY p.nivel DESC
    `;
    const result = await client.query(query, [mestre_id]);
    console.log(`✅ ${result.rows.length} NPCs do mestre ${mestre_id} enviados!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao buscar NPCs:", err.message);
    res.status(500).json({ error: "Erro ao buscar NPCs" });
  }
});

// Listar todos os NPCs (com filtro opcional por tipo)
router.get("/", async (req, res) => {
  try {
    const { tipo } = req.query;
    
    let query = `
      SELECT p.personagem_id, p.nome_personagem, npc.tipo_NPC,
             p.nivel, u.nome_usuario as criador,
             r.nome_raca, c.nome_classe
      FROM NPC npc
      JOIN PERSONAGEM p ON p.personagem_id = npc.npc_id
      JOIN MESTRE m ON m.mestreUser_id = npc.mestreNpc_id
      JOIN USUARIO u ON u.user_id = m.mestreUser_id
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
    `;
    
    const params = [];
    if (tipo) {
      query += ` WHERE LOWER(npc.tipo_NPC) LIKE LOWER($1)`;
      params.push(`%${tipo}%`);
    }
    
    query += ` ORDER BY p.nivel DESC`;
    
    const result = await client.query(query, params);
    console.log(`✅ ${result.rows.length} NPCs enviados!`);
    res.json(result.rows);
  } catch (err) {
    console.error("❌ Erro ao listar NPCs:", err.message);
    res.status(500).json({ error: "Erro ao listar NPCs" });
  }
});

// Buscar NPC específico por ID
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const query = `
      SELECT p.*, npc.tipo_NPC, u.nome_usuario as criador,
             r.nome_raca, r.bonus, c.nome_classe, c.dado_vida
      FROM NPC npc
      JOIN PERSONAGEM p ON p.personagem_id = npc.npc_id
      JOIN MESTRE m ON m.mestreUser_id = npc.mestreNpc_id
      JOIN USUARIO u ON u.user_id = m.mestreUser_id
      JOIN RACA r ON r.raca_id = p.personagemRaca_id
      LEFT JOIN CLASSE c ON c.classe_id = p.personagemClasse_id
      WHERE npc.npc_id = $1
    `;
    const result = await client.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "NPC não encontrado" });
    }
    
    console.log(`✅ NPC ${result.rows[0].nome_personagem} encontrado!`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erro ao buscar NPC:", err.message);
    res.status(500).json({ error: "Erro ao buscar NPC" });
  }
});

module.exports = router;