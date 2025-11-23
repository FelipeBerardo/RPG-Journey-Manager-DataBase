cat > database.js << 'EOF'
require("dotenv").config();
const { Client } = require("pg");

const client = new Client({
  host: process.env.DB_HOST || "localhost",
  port: Number(process.env.DB_PORT) || 5432,
  user: process.env.DB_USER || "rpg_admin",
  password: process.env.DB_PASSWORD || "rpg_password",
  database: process.env.DB_NAME || "rpg_database",
});

client
  .connect()
  .then(() => console.log("📦 Conectado ao PostgreSQL!"))
  .catch((err) => {
    console.error("❌ Erro ao conectar:", err.message);
    process.exit(1);
  });

module.exports = client;
EOF