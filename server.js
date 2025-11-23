// server.js - Servidor Principal da API RPG
const express = require("express");
const personagensRouter = require("./api/routes/personagens");
const jogadoresRouter = require("./api/routes/jogadores");
const missoesRouter = require("./api/routes/missoes");
const sessoesRouter = require("./api/routes/sessoes");
const inventariosRouter = require("./api/routes/inventarios");
const classesRouter = require("./api/routes/classes");
const npcsRouter = require("./api/routes/npcs");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Rota raiz com documentação
app.get("/", (req, res) => {
  res.json({
    message: "🎲 API RPG Database - Node.js Edition",
    endpoints: {
      "/personagens": "GET, POST - Gerenciar personagens",
      "/personagens/:id": "GET, PUT, DELETE - Personagem específico",
      "/jogadores": "GET, POST - Gerenciar jogadores",
      "/jogadores/:id": "GET, PUT, DELETE - Jogador específico",
      "/jogadores/:id/personagens": "GET - Personagens de um jogador",
      "/missoes": "GET, POST - Gerenciar missões",
      "/missoes/:id": "GET, PUT, DELETE - Missão específica",
      "/missoes/status/:status": "GET - Filtrar por status",
      "/sessoes": "GET, POST - Gerenciar sessões",
      "/sessoes/:id": "GET - Sessão específica",
      "/inventarios/:personagem_id": "GET - Inventário de personagem",
      "/inventarios/:personagem_id/itens": "POST - Adicionar item",
      "/classes": "GET - Listar classes com habilidades",
      "/npcs/mestre/:mestre_id": "GET - NPCs de um mestre"
    },
    version: "1.0.0"
  });
});

// Rotas
app.use("/personagens", personagensRouter);
app.use("/jogadores", jogadoresRouter);
app.use("/missoes", missoesRouter);
app.use("/sessoes", sessoesRouter);
app.use("/inventarios", inventariosRouter);
app.use("/classes", classesRouter);
app.use("/npcs", npcsRouter);

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor RPG rodando na porta ${PORT}!`);
  console.log(`📖 Acesse http://localhost:${PORT} para documentação`);
});