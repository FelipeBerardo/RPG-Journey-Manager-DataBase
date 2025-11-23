// routes/inventarios.js - Gerenciar Inventários
const express = require("express");
const router = express.Router();
const client = require("../database");

// Buscar inventário de um personagem
router.get("/:personagem_id", async (req, res) => {
  try {
    const { personagem_id } = req.params;
    const query = `
      SELECT p.nome_personagem, i.item_id, i.nome_item, i.tipo_item, 
             i.valor, i.peso, i.descricao_item
      FROM PERSONAGEM p
      JOIN INVENTARIO inv ON inv.iPersonagem_id = p.personagem_id
      JOIN ITEM i ON i.proprietario_id = inv.inventario_id
      WHERE p.personagem_id = $1
      ORDER BY i.valor DESC
    `;
    const result = await client.query(query, [personagem_id]);
    
    if (result.rows.length === 0) {
      return res.json({ 
        message: "Inventário vazio ou personagem não encontrado",
        itens: [] 
      });
    }
    
    console.log(`✅ Inventário de ${result.rows[0].nome_personagem} enviado!`);
    res.json({
      personagem: result.rows[0].nome_personagem,
      total_itens: result.rows.length,
      valor_total: result.rows.reduce((sum, item) => sum + item.valor, 0),
      peso_total: result.rows.reduce((sum, item) => sum + item.peso, 0),
      itens: result.rows
    });
  } catch (err) {
    console.error("❌ Erro ao buscar inventário:", err.message);
    res.status(500).json({ error: "Erro ao buscar inventário" });
  }
});

// Adicionar item ao inventário
router.post("/:personagem_id/itens", async (req, res) => {
  try {
    const { personagem_id } = req.params;
    const { nome_item, peso, valor, descricao_item, tipo_item } = req.body;
    
    // Buscar ID do inventário
    const invQuery = `
      SELECT inventario_id FROM INVENTARIO WHERE iPersonagem_id = $1
    `;
    const invResult = await client.query(invQuery, [personagem_id]);
    
    if (invResult.rows.length === 0) {
      return res.status(404).json({ message: "Inventário não encontrado" });
    }
    
    const inventario_id = invResult.rows[0].inventario_id;
    
    // Inserir item
    const itemQuery = `
      INSERT INTO ITEM 
        (item_id, nome_item, peso, valor, descricao_item, tipo_item, proprietario_id)
      VALUES 
        ((SELECT COALESCE(MAX(item_id), 0) + 1 FROM ITEM),
         $1, $2, $3, $4, $5, $6)
      RETURNING *
    `;
    const result = await client.query(itemQuery, [
      nome_item, peso || 1, valor || 0, descricao_item, tipo_item, inventario_id
    ]);
    
    console.log(`✅ Item ${nome_item} adicionado ao inventário!`);
    res.status(201).json({ item: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao adicionar item:", err.message);
    res.status(500).json({ error: "Erro ao adicionar item", details: err.message });
  }
});

// Remover item do inventário
router.delete("/:personagem_id/itens/:item_id", async (req, res) => {
  try {
    const { item_id } = req.params;
    
    const query = "DELETE FROM ITEM WHERE item_id = $1 RETURNING *";
    const result = await client.query(query, [item_id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Item não encontrado" });
    }
    
    console.log(`✅ Item ${item_id} removido do inventário!`);
    res.json({ message: "Item removido", item: result.rows[0] });
  } catch (err) {
    console.error("❌ Erro ao remover item:", err.message);
    res.status(500).json({ error: "Erro ao remover item" });
  }
});

module.exports = router;