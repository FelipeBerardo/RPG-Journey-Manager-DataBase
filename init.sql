-- 1. Criação da tabela base de Usuários
CREATE TABLE USUARIO (
    user_id INT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    data_registro DATE DEFAULT CURRENT_DATE,
    data_nascimento DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Especialização: Mestre (Herança de Usuario)
CREATE TABLE MESTRE (
    mestreUser_id INT PRIMARY KEY,
    FOREIGN KEY (mestreUser_id) REFERENCES USUARIO(user_id)
);

-- 3. Especialização: Jogador (Herança de Usuario)
CREATE TABLE JOGADOR (
    jogadorUser_id INT PRIMARY KEY,
    FOREIGN KEY (jogador User_id) REFERENCES USUARIO(user_id)
);

-- 4 e 5. Tabelas de Meta-jogo (Raça e Classe)
CREATE TABLE RACA (
    raca_id INT PRIMARY KEY,
    nome_raca VARCHAR(50) NOT NULL,
    bonus INT[] NOT NULL DEFAULT ARRAY[0,0,0,0,0], 
    descricao_raca TEXT
);

CREATE TABLE CLASSE (
    classe_id INT PRIMARY KEY,
    nome_classe VARCHAR(50) NOT NULL,
    dado_vida INT NOT NULL, 
    dado_energia INT NOT NULL,
    descricao_classe TEXT
);

-- 6. Habilidades ligadas à Classe
CREATE TABLE HABILIDADE (
    habilidade_id INT PRIMARY KEY,
    classeHabilidade_id INT,
    tipo VARCHAR(50) NOT NULL,
    custo INT NOT NULL DEFAULT 0,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    FOREIGN KEY (classeHabilidade_id) REFERENCES CLASSE(classe_id)
);

-- 7 . Sessão de Jogo
CREATE TABLE SESSAO (
    sessao_id INT PRIMARY KEY,
    data_criacao DATE DEFAULT CURRENT_DATE,
    titulo VARCHAR(150),
    mUser_id INT,
    FOREIGN KEY (mUser_id) REFERENCES MESTRE(mestreUser_id)
);

-- 8  . Tabela Principal: Personagem
CREATE TABLE PERSONAGEM (
    personagem_id INT PRIMARY KEY,
    nome_personagem VARCHAR(200) NOT NULL,
    pontos_vida INT NOT NULL DEFAULT 10,
    nivel INT NOT NULL DEFAULT 1,
    destreza INT NOT NULL DEFAULT 1,
    forca INT NOT NULL DEFAULT 1,
    carisma INT NOT NULL DEFAULT 1,
    sabedoria INT NOT NULL DEFAULT 1,
    inteligencia INT NOT NULL DEFAULT 1,
    personagemRaca_id INT NOT NULL,
    personagemClasse_id INT,
    FOREIGN KEY (personagemRaca_id) REFERENCES RACA(raca_id),
    FOREIGN KEY (personagemClasse_id) REFERENCES CLASSE(classe_id)
);

-- 9. Especialização: NPC (Non-Player Character)
CREATE TABLE NPC (
    npc_id INT PRIMARY KEY,
    mestreNpc_id INT NOT NULL,
    tipo_NPC VARCHAR(50) NOT NULL,
    FOREIGN KEY (npc_id) REFERENCES PERSONAGEM(personagem_id),
    FOREIGN KEY (mestreNpc_id) REFERENCES MESTRE(mestreUser_id)
);

-- 10. Especialização: PC (Player Character)
CREATE TABLE PC (
    pc_id INT PRIMARY KEY,
    pc_jogador_id INT NOT NULL,
    experiencia INT NOT NULL DEFAULT 0,
    FOREIGN KEY (pc_id) REFERENCES PERSONAGEM(personagem_id),
    FOREIGN KEY (pc_jogador_id) REFERENCES JOGADOR(jogadorUser_id)
);

-- 11. Inventário
CREATE TABLE INVENTARIO (
    inventario_id INT PRIMARY KEY,
    iPersonagem_id INT UNIQUE,
    FOREIGN KEY (iPersonagem_id) REFERENCES PERSONAGEM(personagem_id)
);

-- 12. ITEM 
CREATE TABLE ITEM (
    item_id INT PRIMARY KEY,
    nome_item VARCHAR(100) NOT NULL,
    peso INT NOT NULL DEFAULT 70,
    valor INT NOT NULL DEFAULT 0,
    descricao_item TEXT,
    tipo_item VARCHAR(50) NOT NULL,
    proprietario_id INT NOT NULL,
    FOREIGN KEY (proprietario_id) REFERENCES INVENTARIO(inventario_id)
);

-- 13. Recompensa
CREATE TABLE RECOMPENSA (
    recompensa_id INT PRIMARY KEY,
    rItem_id INT,
    qtd_ouro INT NOT NULL DEFAULT 0,
    qtd_xp INT NOT NULL DEFAULT 0,
    qtd_reputacao INT NOT NULL DEFAULT 0,
    titulo VARCHAR(100),
    FOREIGN KEY (rItem_id) REFERENCES ITEM(item_id)
);

-- 14. Missão
CREATE TABLE MISSAO (
    missao_id INT PRIMARY KEY,
    nome_missao VARCHAR(150),
    status VARCHAR(50) NOT NULL DEFAULT 'Aberta',
    descricao_missao TEXT,
    s_id INT NOT NULL,          
    mRecompensa_id INT NOT NULL, 
    FOREIGN KEY (s_id) REFERENCES SESSAO(sessao_id),
    FOREIGN KEY (mRecompensa_id) REFERENCES RECOMPENSA(recompensa_id)
);

-- 15. Personagem em Missão
CREATE TABLE EM_MISSAO (
    mPersonagem_id INT,
    mMissao_id INT,
    PRIMARY KEY (mPersonagem_id, mMissao_id),
    FOREIGN KEY (mPersonagem_id) REFERENCES PERSONAGEM(personagem_id),
    FOREIGN KEY (mMissao_id) REFERENCES MISSAO(missao_id)
);

-- ============================================================
-- 1. USUÁRIOS (Expansão Multi-Campanhas)
-- ============================================================
INSERT INTO USUARIO (user_id, nome_usuario, data_nascimento, email) VALUES
-- Critical Role (Grupo 1)
(1, 'Matthew Mercer', '1982-06-29', 'matt@criticalrole.com'),
(2, 'Travis Willingham', '1981-08-03', 'travis@criticalrole.com'),
(3, 'Laura Bailey', '1981-05-28', 'laura@criticalrole.com'),
(4, 'Sam Riegel', '1976-10-09', 'sam@criticalrole.com'),
(5, 'Liam O''Brien', '1976-05-28', 'liam@criticalrole.com'),
(6, 'Marisha Ray', '1989-05-10', 'marisha@criticalrole.com'),
(7, 'Taliesin Jaffe', '1977-01-19', 'taliesin@criticalrole.com'),

-- Dimension 20 (Grupo 2)
(8, 'Brennan Lee Mulligan', '1988-01-04', 'brennan@dimension20.com'),
(9, 'Lou Wilson', '1990-10-10', 'lou@dimension20.com'),
(10, 'Emily Axford', '1984-07-26', 'emily@dimension20.com'),
(11, 'Siobhan Thompson', '1984-07-29', 'siobhan@dimension20.com'),
(12, 'Ally Beardsley', '1991-05-06', 'ally@dimension20.com'),

-- The Adventure Zone (Grupo 3)
(13, 'Griffin McElroy', '1987-04-17', 'griffin@theadventurezone.com'),
(14, 'Justin McElroy', '1980-11-08', 'justin@theadventurezone.com'),
(15, 'Travis McElroy', '1983-11-08', 'travismcelroy@theadventurezone.com'),
(16, 'Clint McElroy', '1955-08-14', 'clint@theadventurezone.com'),

-- Jogadores Casuais
(17, 'Ana Silva', '1995-03-15', 'ana.silva@email.com'),
(18, 'Pedro Costa', '1992-07-22', 'pedro.costa@email.com'),
(19, 'Carla Mendes', '1998-11-30', 'carla.mendes@email.com'),
(20, 'João Santos', '1990-02-14', 'joao.santos@email.com');

-- ============================================================
-- 2. PAPÉIS (Mestres e Jogadores)
-- ============================================================
-- Mestres
INSERT INTO MESTRE (mestreUser_id) VALUES 
(1),  -- Matt Mercer
(8),  -- Brennan Lee Mulligan
(13), -- Griffin McElroy
(17); -- Ana Silva (mesa casual)

-- Jogadores (incluindo mestres que também jogam)
INSERT INTO JOGADOR (jogadorUser_id) VALUES 
(1), (2), (3), (4), (5), (6), (7),     -- Critical Role
(8), (9), (10), (11), (12),             -- Dimension 20
(14), (15), (16),                       -- Adventure Zone
(18), (19), (20);                       -- Jogadores casuais

-- ============================================================
-- 3. META-DADOS: RAÇAS (Expandido)
-- Padrão do Array Bônus: [DES, FOR, CAR, SAB, INT]
-- ============================================================
INSERT INTO RACA (raca_id, nome_raca, bonus, descricao_raca) VALUES
(1, 'Humano', ARRAY[1, 1, 1, 1, 1], 'Versatilidade e ambição. A raça mais comum.'),
(2, 'Elfo', ARRAY[2, 0, 1, 1, 1], 'Graciosidade e afinidade mágica natural.'),
(3, 'Anão', ARRAY[0, 2, 0, 2, 0], 'Robustez e sabedoria da pedra.'),
(4, 'Orc', ARRAY[1, 3, 0, 0, 0], 'Força bruta e fúria tribal.'),
(5, 'Gnomo', ARRAY[0, 0, 1, 0, 2], 'Pequenos e engenhosos inventores.'),
(6, 'Tiefling', ARRAY[0, 0, 2, 0, 1], 'Herança infernal, adaptáveis e carismáticos.'),
(7, 'Meio-Elfo', ARRAY[1, 0, 2, 1, 0], 'Combinação de diplomacia humana e graça élfica.'),
(8, 'Halfling', ARRAY[2, 0, 1, 0, 0], 'Pequenos, ágeis e sortudos.'),
(9, 'Draconato', ARRAY[0, 2, 1, 0, 0], 'Descendentes de dragões com sopro elemental.'),
(10, 'Goblin', ARRAY[2, 0, 0, 0, 1], 'Pequenos, espertos e ágeis sobreviventes.');

-- ============================================================
-- 4. META-DADOS: CLASSES (Expandido)
-- ============================================================
INSERT INTO CLASSE (classe_id, nome_classe, dado_vida, dado_energia, descricao_classe) VALUES
(1, 'Bárbaro', 12, 0, 'Guerreiro feroz que usa fúria em batalha.'),
(2, 'Paladino', 10, 10, 'Guerreiro santo jurado a um ideal sagrado.'),
(3, 'Ladino', 8, 5, 'Especialista em furtividade e astúcia.'),
(4, 'Mago', 6, 30, 'Usuário de magia escolástica capaz de manipular a realidade.'),
(5, 'Bardo', 8, 20, 'Mágico inspirador cujo poder ecoa a música da criação.'),
(6, 'Druida', 8, 25, 'Sacerdote da Antiga Fé, assumindo formas animais.'),
(7, 'Arqueiro', 10, 10, 'Guerreiro que usa proeza marcial e magia natural.'),
(8, 'Clérigo', 8, 20, 'Sacerdote que canaliza poder divino.'),
(9, 'Monge', 8, 15, 'Mestre das artes marciais e energia ki.'),
(10, 'Feiticeiro', 6, 25, 'Mago inato com magia no sangue.'),
(11, 'Bruxo', 8, 15, 'Conjurador que fez pacto com entidade poderosa.'),
(12, 'Guerreiro', 10, 5, 'Mestre das armas e táticas de combate.');

-- ============================================================
-- 5. HABILIDADES (Expandido por Classe)
-- ============================================================
INSERT INTO HABILIDADE (habilidade_id, classeHabilidade_id, tipo, custo, nome, descricao) VALUES
-- Bárbaro
(1, 1, 'Buff', 0, 'Fúria', 'Entra em estado de fúria, ganhando resistência e dano extra.'),
(2, 1, 'Passiva', 0, 'Defesa sem Armadura', 'Adiciona CON à CA quando não usa armadura.'),
(3, 1, 'Ataque', 0, 'Ataque Imprudente', 'Ganha vantagem em ataques mas inimigos têm vantagem contra você.'),

-- Ladino
(4, 3, 'Passiva', 0, 'Ataque Furtivo', 'Causa dano extra se tiver vantagem no ataque.'),
(5, 3, 'Utilidade', 0, 'Astúcia', 'Pode Desengajar ou Esconder como ação bônus.'),
(6, 3, 'Passiva', 0, 'Evasão', 'Evita totalmente dano de efeitos em área com sucesso em teste.'),

-- Mago
(7, 4, 'Magia', 5, 'Bola de Fogo', 'Explosão de fogo em área causando 8d6 de dano.'),
(8, 4, 'Magia', 3, 'Mísseis Mágicos', 'Dardos de energia que sempre acertam o alvo.'),
(9, 4, 'Magia', 8, 'Parar o Tempo', 'Congela o tempo por alguns turnos.'),

-- Bardo
(10, 5, 'Buff', 3, 'Inspiração de Bardo', 'Concede um dado extra para um aliado usar em testes.'),
(11, 5, 'Magia', 4, 'Palavra de Cura', 'Cura aliados à distância.'),
(12, 5, 'Magia', 5, 'Confusão', 'Confunde inimigos em área fazendo-os atacar aliados.'),

-- Druida
(13, 6, 'Transformação', 4, 'Forma Selvagem', 'Assume a forma de uma besta por horas.'),
(14, 6, 'Magia', 6, 'Invocar Relâmpagos', 'Canaliza tempestade causando dano elétrico.'),
(15, 6, 'Magia', 3, 'Curar Ferimentos', 'Cura pontos de vida com toque.'),

-- Paladino
(16, 2, 'Cura', 5, 'Impor as Mãos', 'Cura pontos de vida ao toque usando pool de cura.'),
(17, 2, 'Buff', 0, 'Aura de Proteção', 'Aliados próximos ganham bônus em salvamentos.'),
(18, 2, 'Ataque', 8, 'Golpe Divino', 'Ataque imbuído com energia radiante devastadora.'),

-- Arqueiro
(19, 7, 'Ataque', 2, 'Marca do Caçador', 'Causa dano extra no alvo marcado.'),
(20, 7, 'Ataque', 3, 'Flecha Perfurante', 'Flecha atravessa múltiplos inimigos em linha.'),

-- Clérigo
(21, 8, 'Magia', 5, 'Curar Ferimentos em Massa', 'Cura múltiplos aliados em área.'),
(22, 8, 'Magia', 7, 'Reviver os Mortos', 'Traz criatura morta de volta à vida.'),
(23, 8, 'Buff', 4, 'Escudo da Fé', 'Aumenta CA de um aliado.'),

-- Monge
(24, 9, 'Ataque', 2, 'Rajada de Golpes', 'Dois ataques desarmados extras.'),
(25, 9, 'Utilidade', 3, 'Passo do Vento', 'Move-se como vento, atravessando inimigos.'),
(26, 9, 'Defesa', 1, 'Aparar Projéteis', 'Reduz dano de ataques à distância.'),

-- Feiticeiro
(27, 10, 'Buff', 0, 'Metamagia: Acelerar', 'Conjura magia como ação bônus.'),
(28, 10, 'Magia', 6, 'Relâmpago em Cadeia', 'Relâmpago salta entre múltiplos inimigos.'),

-- Bruxo
(29, 11, 'Ataque', 0, 'Rajada Mística', 'Feixes de energia que acertam automaticamente.'),
(30, 11, 'Invocação', 5, 'Invocar Patrono', 'Chama a entidade do pacto para auxiliar.'),

-- Guerreiro
(31, 12, 'Ataque', 0, 'Ação Extra', 'Pode atacar mais vezes por turno.'),
(32, 12, 'Defesa', 0, 'Segundo Fôlego', 'Recupera pontos de vida em batalha.');

-- ============================================================
-- 6. SESSÕES (Múltiplas Campanhas)
-- ============================================================
INSERT INTO SESSAO (sessao_id, data_criacao, titulo, mUser_id) VALUES
-- Critical Role
(1, '2023-01-15', 'Vox Machina: A Chegada em Kraghammer', 1),
(2, '2023-01-22', 'Vox Machina: O Julgamento de Vasselheim', 1),
(3, '2023-01-29', 'Vox Machina: A Queda de Emon', 1),
(4, '2023-02-05', 'Mighty Nein: O Circo dos Horrores', 1),
(5, '2023-02-12', 'Bells Hells: Despertar em Marquet', 1),

-- Dimension 20
(6, '2023-03-01', 'Unsleeping City: O Sonho de Nova York', 8),
(7, '2023-03-15', 'Fantasy High: Primeiro Dia de Aula', 8),
(8, '2023-03-29', 'A Crown of Candy: O Massacre do Chá', 8),

-- Adventure Zone
(9, '2023-04-10', 'Balance: Aqui Há Gerblins', 13),
(10, '2023-04-24', 'Balance: O Templo da Cristalândia', 13),

-- Campanha Casual
(11, '2023-05-01', 'A Taverna do Dragão Dançante', 17),
(12, '2023-05-15', 'Masmorra dos Segredos Esquecidos', 17);

-- ============================================================
-- 7. PERSONAGENS (Grande Variedade)
-- ============================================================
INSERT INTO PERSONAGEM (personagem_id, nome_personagem, pontos_vida, nivel, destreza, forca, carisma, sabedoria, inteligencia, personagemRaca_id, personagemClasse_id) VALUES
-- CRITICAL ROLE - Vox Machina
(1, 'Grog Strongjaw', 140, 10, 15, 20, 10, 8, 6, 4, 1),
(2, 'Vex''ahlia', 85, 10, 20, 12, 14, 16, 12, 2, 7),
(3, 'Scanlan Shorthalt', 70, 10, 14, 10, 20, 12, 16, 5, 5),
(4, 'Keyleth', 90, 10, 14, 10, 10, 20, 14, 2, 6),
(5, 'Percival de Rolo', 80, 10, 20, 12, 14, 14, 18, 1, 3),
(6, 'Pike Trickfoot', 75, 10, 10, 14, 16, 18, 12, 5, 8),
(7, 'Vax''ildan', 78, 10, 20, 14, 16, 12, 14, 2, 3),

-- CRITICAL ROLE - Mighty Nein
(8, 'Caleb Widogast', 55, 8, 14, 10, 12, 16, 20, 1, 4),
(9, 'Jester Lavorre', 85, 8, 14, 12, 18, 16, 14, 6, 8),
(10, 'Fjord', 92, 8, 12, 16, 16, 10, 12, 7, 11),
(11, 'Beauregard', 70, 8, 18, 14, 10, 16, 12, 1, 9),
(12, 'Nott/Veth', 65, 8, 20, 10, 12, 14, 16, 10, 3),

-- DIMENSION 20 - Fantasy High
(13, 'Fig Faeth', 68, 7, 14, 12, 18, 10, 14, 6, 5),
(14, 'Gorgug Thistlespring', 95, 7, 10, 18, 8, 12, 14, 7, 1),
(15, 'Fabian Seacaster', 78, 7, 18, 16, 16, 10, 10, 1, 12),
(16, 'Adaine Abernant', 52, 7, 12, 8, 10, 14, 20, 2, 4),
(17, 'Kristen Applebees', 70, 7, 12, 12, 14, 18, 12, 1, 8),

-- DIMENSION 20 - Unsleeping City
(18, 'Kingston Brown', 82, 9, 10, 14, 14, 18, 12, 1, 8),
(19, 'Leiland Stillwell', 88, 9, 12, 16, 16, 12, 10, 1, 2),
(20, 'Sofia Bicicleta', 72, 9, 16, 12, 16, 14, 12, 7, 12),

-- ADVENTURE ZONE - Balance
(21, 'Taako', 60, 10, 16, 10, 16, 12, 18, 2, 4),
(22, 'Magnus Burnsides', 110, 10, 12, 18, 10, 10, 8, 1, 12),
(23, 'Merle Highchurch', 75, 10, 10, 14, 12, 18, 10, 3, 8),

-- CAMPANHA CASUAL
(24, 'Thorin Barba-de-Aço', 95, 5, 10, 16, 8, 14, 10, 3, 12),
(25, 'Liriel Canção-da-Lua', 55, 5, 16, 8, 14, 12, 16, 2, 5),
(26, 'Gornak Quebra-Ossos', 105, 5, 12, 18, 6, 8, 6, 4, 1),

-- NPCs IMPORTANTES
(27, 'Gilmore', 60, 15, 14, 10, 18, 12, 18, 1, 4),
(28, 'Sylas Briarwood', 200, 18, 18, 22, 18, 14, 16, 1, 12),
(29, 'Vecna', 500, 20, 14, 18, 16, 20, 22, 1, 4),
(30, 'Ayda Aguefort', 120, 14, 14, 12, 16, 16, 20, 6, 4),
(31, 'O Estranho', 300, 15, 16, 14, 20, 18, 20, 1, 11),
(32, 'Arthur Aguefort', 250, 20, 12, 14, 20, 16, 22, 1, 4),

-- NPCs Diversos (Mercadores, Aliados, Inimigos Menores)
(33, 'Pumat Sol', 80, 10, 10, 14, 16, 12, 16, 1, 12),
(34, 'Essek Thelyss', 65, 12, 16, 8, 14, 14, 20, 2, 4),
(35, 'Kima de Vord', 110, 12, 12, 18, 14, 16, 10, 3, 2),
(36, 'Allura Vysoren', 75, 15, 14, 10, 16, 16, 20, 1, 4),
(37, 'Victor', 35, 3, 8, 8, 6, 8, 10, 1, 4),
(38, 'Capitão Tusktooth', 125, 10, 14, 18, 16, 12, 10, 4, 12),
(39, 'Barry Bluejeans', 70, 11, 12, 12, 14, 16, 18, 1, 4),
(40, 'Lucretia', 80, 13, 14, 10, 18, 18, 20, 1, 4);

-- ============================================================
-- 8. VINCULANDO PCs e NPCs
-- ============================================================
-- PCs (Critical Role)
INSERT INTO PC (pc_id, pc_jogador_id, experiencia) VALUES
(1, 2, 64000),   -- Grog -> Travis
(2, 3, 64000),   -- Vex -> Laura
(3, 4, 64000),   -- Scanlan -> Sam
(4, 6, 64000),   -- Keyleth -> Marisha
(5, 7, 64000),   -- Percy -> Taliesin
(6, 4, 64000),   -- Pike -> (Ashley, usando Sam como proxy)
(7, 5, 64000),   -- Vax -> Liam
(8, 5, 34000),   -- Caleb -> Liam
(9, 3, 34000),   -- Jester -> Laura
(10, 2, 34000),  -- Fjord -> Travis
(11, 6, 34000),  -- Beau -> Marisha
(12, 4, 34000),  -- Nott -> Sam

-- PCs (Dimension 20)
(13, 10, 28000), -- Fig -> Emily
(14, 12, 28000), -- Gorgug -> Ally
(15, 9, 28000),  -- Fabian -> Lou
(16, 11, 28000), -- Adaine -> Siobhan
(17, 12, 28000), -- Kristen -> Ally
(18, 9, 48000),  -- Kingston -> Lou
(19, 1, 48000),  -- Leiland -> MATT (jogando na mesa do Brennan!)
(20, 10, 48000), -- Sofia -> Emily

-- PCs (Adventure Zone)
(21, 14, 64000), -- Taako -> Justin
(22, 15, 64000), -- Magnus -> Travis McElroy
(23, 16, 64000), -- Merle -> Clint

-- PCs (Campanha Casual)
(24, 18, 6500),  -- Thorin -> Pedro
(25, 19, 6500),  -- Liriel -> Carla
(26, 20, 6500);  -- Gornak -> João

-- NPCs
INSERT INTO NPC (npc_id, mestreNpc_id, tipo_NPC) VALUES
(27, 1, 'Aliado/Mercador'),     -- Gilmore
(28, 1, 'Inimigo/Chefe'),       -- Sylas
(29, 1, 'Inimigo Lendário'),    -- Vecna
(30, 8, 'Aliado/Professora'),   -- Ayda
(31, 13, 'Inimigo/Entidade'),   -- O Estranho
(32, 8, 'Aliado/Mestre'),       -- Arthur Aguefort
(33, 1, 'Aliado/Mercador'),     -- Pumat Sol
(34, 1, 'Aliado/Mago'),         -- Essek
(35, 1, 'Aliado/Paladina'),     -- Kima
(36, 1, 'Aliado/Maga'),         -- Allura
(37, 1, 'Neutro/Excêntrico'),   -- Victor
(38, 1, 'Inimigo/Chefe'),       -- Capitão Tusktooth
(39, 13, 'Aliado'),             -- Barry
(40, 13, 'Aliado/Líder');       -- Lucretia

-- ============================================================
-- 9. INVENTÁRIOS
-- ============================================================
INSERT INTO INVENTARIO (inventario_id, iPersonagem_id) VALUES
-- PCs Critical Role - Vox Machina
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
-- PCs Critical Role - Mighty Nein
(8, 8), (9, 9), (10, 10), (11, 11), (12, 12),
-- PCs Dimension 20
(13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20),
-- PCs Adventure Zone
(21, 21), (22, 22), (23, 23),
-- PCs Casual
(24, 24), (25, 25), (26, 26),
-- NPCs com inventário
(27, 27), (28, 28), (29, 29), (30, 30), (33, 33);

-- ============================================================
-- 10. ITENS (Grande Variedade)
-- ============================================================
INSERT INTO ITEM (item_id, nome_item, peso, valor, descricao_item, tipo_item, proprietario_id) VALUES
-- Itens do Grog (Inv 1)
(1, 'Machado de Sangue', 15, 500, 'Machado que causa dano necrótico adicional.', 'Arma', 1),
(2, 'Barril de Cerveja', 20, 10, 'Nunca esvazia completamente.', 'Consumível', 1),
(3, 'Cinto do Gigante', 5, 8000, 'Aumenta força para 25.', 'Vestimenta', 1),

-- Itens da Vex (Inv 2)
(4, 'Fenthras', 5, 5000, 'Arco lendário da Cisne Branco.', 'Arma Lendária', 2),
(5, 'Vassoura Voadora', 3, 2000, 'Permite voo.', 'Veículo', 2),
(6, 'Armadura de Couro +2', 10, 4000, 'Proteção aprimorada.', 'Armadura', 2),

-- Itens do Scanlan (Inv 3)
(7, 'Mythcarver', 3, 5000, 'Espada lendária que potencializa bardos.', 'Arma Lendária', 3),
(8, 'Boina da Inspiração', 1, 200, 'Aumenta carisma.', 'Vestuário', 3),
(9, 'Alaúde Mágico', 2, 1500, 'Foco arcano poderoso.', 'Foco Arcano', 3),

-- Itens da Keyleth (Inv 4)
(10, 'Cajado do Bosque', 4, 3000, 'Aumenta poder de magias druídicas.', 'Arma/Foco', 4),
(11, 'Manto da Natureza', 3, 2500, 'Permite falar com animais livremente.', 'Vestimenta', 4),

-- Itens do Percy (Inv 5)
(12, 'A Lista', 4, 1000, 'Pistola com seis nomes gravados.', 'Arma', 5),
(13, 'Pólvora Negra', 1, 50, 'Munição especial.', 'Munição', 5),
(14, 'Óculos de Identificação', 0, 500, 'Identifica propriedades mágicas.', 'Item Mágico', 5),

-- Itens do Caleb (Inv 8)
(15, 'Grimório de Caleb', 3, 2000, 'Contém todas as magias conhecidas.', 'Livro', 8),
(16, 'Âmbar Transmutador', 1, 1500, 'Pedra de poder transmutação.', 'Componente Arcano', 8),
(17, 'Gato Familiar (Frumpkin)', 0, 0, 'Companheiro felino mágico.', 'Criatura', 8),

-- Itens da Jester (Inv 9)
(18, 'Pirulito Espiritual', 1, 50, 'Foco divino em forma de pirulito.', 'Foco Divino', 9),
(19, 'Tinta de Duplicata', 0, 100, 'Cria cópias perfeitas de escritos.', 'Consumível', 9),
(20, 'Esboços do Traveler', 1, 10, 'Desenhos de sua divindade.', 'Item Pessoal', 9),

-- Itens do Taako (Inv 21)
(21, 'Guarda-Chuva Mágico', 2, 2000, 'Funciona como varinha e escudo.', 'Arma/Foco', 21),
(22, 'Avental do Chef', 2, 800, 'Impede que comida queime.', 'Vestuário', 21),

-- Loot de Vecna (Inv 29) - Tesouros lendários
(23, 'A Mão de Vecna', 2, 999999, 'Artefato amaldiçoado de poder imenso.', 'Artefato', 29),
(24, 'O Olho de Vecna', 0, 999999, 'Artefato que concede visão além da realidade.', 'Artefato', 29),
(25, 'Livro das Trevas', 5, 5000, 'Grimório com magias proibidas.', 'Livro', 29),
(26, 'Coroa do Lich', 3, 10000, 'Aumenta poder sobre mortos-vivos.', 'Vestimenta', 29),

-- Loja do Gilmore (Inv 27) - Mercadorias
(27, 'Poção de Cura Superior', 1, 200, 'Restaura 8d4+8 pontos de vida.', 'Consumível', 27),
(28, 'Capa do Deslocamento', 2, 5000, 'Cria imagem ilusória, dificultando acertos.', 'Vestimenta', 27),
(29, 'Anel de Proteção', 0, 3500, 'Bônus em CA e salvamentos.', 'Acessório', 27),
(30, 'Pergaminho de Reviver Mortos', 0, 1500, 'Uso único de ressurreição.', 'Consumível', 27),

-- Loja do Pumat Sol (Inv 33)
(31, 'Espada Longa +1', 3, 1000, 'Arma mágica básica.', 'Arma', 33),
(32, 'Armadura de Couro Batido +1', 12, 1500, 'Proteção aprimorada.', 'Armadura', 33),
(33, 'Poção de Força do Gigante', 1, 500, 'Força 25 por 1 hora.', 'Consumível', 33),
(34, 'Anel de Conjuração', 0, 8000, 'Armazena magias.', 'Acessório', 33),

-- Loot do Sylas Briarwood (Inv 28)
(35, 'Espada das Sombras', 3, 6000, 'Espada vampírica que drena vida.', 'Arma', 28),
(36, 'Anel da Regeneração', 0, 12000, 'Regenera 1d6 PV por turno.', 'Acessório', 28),
(37, 'Capa de Vampiro', 2, 4000, 'Concede resistência necrótica.', 'Vestimenta', 28),

-- Itens da Ayda (Inv 30)
(38, 'Tomo do Conhecimento Infinito', 4, 15000, 'Livro com todas as informações da biblioteca.', 'Livro', 30),
(39, 'Cajado da Fênix', 4, 10000, 'Permite ressurreição 1x por dia.', 'Arma/Foco', 30),

-- Itens dos PCs Dimension 20
(40, 'Baixo da Rebelião', 8, 3000, 'Instrumento que amplifica magias de bardo.', 'Instrumento', 13),
(41, 'Machado de Batalha de Gorgug', 10, 2500, 'Machado grande personalizado.', 'Arma', 14),
(42, 'Espada de Fabian', 3, 4000, 'Herança de família de corsários.', 'Arma', 15),
(43, 'Familiar Boggy', 0, 0, 'Sapo companheiro da Adaine.', 'Criatura', 16),
(44, 'Símbolo Sagrado do Sim?', 1, 100, 'Foco divino questionador.', 'Foco Divino', 17),

-- Itens Kingston e Sofia
(45, 'Martelo da Cidade', 6, 5000, 'Martelo que canaliza poder urbano.', 'Arma', 18),
(46, 'Bicicleta Encantada', 20, 3000, 'Veículo mágico veloz.', 'Veículo', 20),

-- Itens dos PCs Casuais
(47, 'Machado de Batalha Anão', 7, 300, 'Arma tradicional anã.', 'Arma', 24),
(48, 'Armadura de Placas', 25, 1500, 'Proteção pesada.', 'Armadura', 24),
(49, 'Harpa Élfica', 3, 500, 'Instrumento de qualidade superior.', 'Instrumento', 25),
(50, 'Clava Grande', 10, 100, 'Arma simples mas efetiva.', 'Arma', 26),

-- Itens diversos de aventura
(51, 'Corda de Escalada (50 pés)', 5, 25, 'Corda resistente.', 'Equipamento', 1),
(52, 'Kit de Ladrão', 2, 75, 'Ferramentas de arrombamento.', 'Equipamento', 5),
(53, 'Tochas (10 unidades)', 5, 5, 'Iluminação básica.', 'Equipamento', 26),
(54, 'Ração de Viagem (7 dias)', 7, 35, 'Comida preservada.', 'Consumível', 22),
(55, 'Tenda para 2 pessoas', 10, 20, 'Abrigo portátil.', 'Equipamento', 24),
(56, 'Kit de Cura', 3, 50, 'Bandagens e remédios.', 'Consumível', 6),

-- Itens raros/únicos
(57, 'Crânio de Dragão Branco', 50, 2000, 'Troféu de caçada épica.', 'Troféu', 1),
(58, 'Pena de Fênix', 0, 5000, 'Componente para ressurreição.', 'Componente Arcano', 30),
(59, 'Fragmento da Pedra Filosofal', 1, 8000, 'Permite transmutação limitada.', 'Componente Arcano', 8),
(60, 'Mapa do Plano Astral', 0, 1000, 'Guia para viagem planar.', 'Documento', 21);

-- ============================================================
-- 11. RECOMPENSAS
-- ============================================================
INSERT INTO RECOMPENSA (recompensa_id, rItem_id, qtd_ouro, qtd_xp, qtd_reputacao, titulo) VALUES
(1, 57, 1000, 5000, 100, 'Matador de Dragões'),
(2, NULL, 500, 1000, 50, 'Herói de Whitestone'),
(3, 23, 0, 25000, -100, 'Portador do Artefato Amaldiçoado'),
(4, NULL, 2000, 8000, 200, 'Libertador de Vasselheim'),
(5, NULL, 5000, 15000, 500, 'Destruidor de Vecna'),
(6, 58, 3000, 10000, 150, 'Guardião da Fênix'),
(7, NULL, 800, 3000, 75, 'Explorador de Masmorras'),
(8, NULL, 1500, 5000, 100, 'Campeão da Arena'),
(9, 59, 10000, 20000, 300, 'Mestre Alquimista'),
(10, NULL, 300, 800, 25, 'Protetor da Aldeia'),
(11, NULL, 50000, 50000, 1000, 'Herói Lendário do Reino'),
(12, 60, 4000, 12000, 200, 'Viajante Planar');

-- ============================================================
-- 12. MISSÕES
-- ============================================================
INSERT INTO MISSAO (missao_id, nome_missao, status, descricao_missao, s_id, mRecompensa_id) VALUES
-- Missões do Critical Role
(1, 'Matar Umbrasyl', 'Em Progresso', 'Derrotar o dragão negro antigo que aterroriza a região.', 3, 1),
(2, 'Resgatar Kima', 'Concluída', 'Salvar a paladina das profundezas das minas.', 1, 2),
(3, 'Destruir os Briarwood', 'Concluída', 'Libertar Whitestone do domínio vampírico.', 2, 4),
(4, 'Impedir a Ascensão de Vecna', 'Aberta', 'Evitar que o lich se torne um deus.', 3, 5),
(5, 'Recuperar os Vestígios da Divergência', 'Em Progresso', 'Encontrar armas lendárias perdidas.', 2, 6),
(6, 'Investigar o Circo Sombrio', 'Em Progresso', 'Descobrir segredos do circo amaldiçoado.', 4, 7),
(7, 'O Contrato com Uk''otoa', 'Aberta', 'Lidar com a entidade marinha que persegue Fjord.', 4, 8),

-- Missões do Dimension 20
(8, 'Passar no Exame Final', 'Concluída', 'Sobreviver aos testes mortais de Aguefort.', 7, 7),
(9, 'Salvar Nova York do Colapso Onírico', 'Concluída', 'Impedir que sonhos e realidade se fundam.', 6, 9),
(10, 'Guerra dos Doces', 'Em Progresso', 'Sobreviver à política mortal de Candelabra.', 8, 11),
(11, 'Encontrar a Coroa da Memória', 'Aberta', 'Recuperar relíquia que restaura lembranças perdidas.', 6, 12),

-- Missões do Adventure Zone
(12, 'Recuperar a Pedra Filosofal', 'Concluída', 'Obter artefato antes que cause destruição.', 9, 9),
(13, 'Sobreviver ao Trem Assassino', 'Concluída', 'Escapar da Locomotiva Rockport Limited.', 10, 7),
(14, 'Confrontar o Sofrimento', 'Aberta', 'Enfrentar a entidade que devora mundos.', 10, 11),

-- Missões da Campanha Casual
(15, 'Limpar a Adega de Ratos Gigantes', 'Concluída', 'Exterminar praga na taverna local.', 11, 10),
(16, 'Explorar as Ruínas Antigas', 'Em Progresso', 'Investigar templo esquecido na floresta.', 12, 7),
(17, 'Escoltar Caravana Mercante', 'Aberta', 'Proteger comerciantes de bandidos.', 11, 10),
(18, 'O Mistério do Assassino da Névoa', 'Em Progresso', 'Descobrir quem mata cidadãos durante a noite.', 12, 8);

-- ============================================================
-- 13. PERSONAGENS EM MISSÕES
-- ============================================================
INSERT INTO EM_MISSAO (mPersonagem_id, mMissao_id) VALUES
-- Missão 1: Matar Umbrasyl (Vox Machina)
(1, 1), (2, 1), (3, 1), (5, 1), (6, 1), (7, 1),

-- Missão 2: Resgatar Kima (Vox Machina)
(1, 2), (2, 2), (3, 2), (4, 2), (5, 2),

-- Missão 3: Destruir os Briarwood (Vox Machina)
(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3),

-- Missão 4: Impedir Vecna (Vox Machina completo)
(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),

-- Missão 5: Vestígios da Divergência (Parte do grupo)
(2, 5), (5, 5), (7, 5),

-- Missão 6: Circo Sombrio (Mighty Nein)
(8, 6), (9, 6), (10, 6), (11, 6), (12, 6),

-- Missão 7: Uk'otoa (Mighty Nein focado em Fjord)
(10, 7), (9, 7), (8, 7),

-- Missão 8: Exame Final (Bad Kids - Fantasy High)
(13, 8), (14, 8), (15, 8), (16, 8), (17, 8),

-- Missão 9: Salvar NY (Unsleeping City)
(18, 9), (19, 9), (20, 9),

-- Missão 10: Guerra dos Doces (Crown of Candy - usando mesmos PCs)
(13, 10), (14, 10), (15, 10),

-- Missão 11: Coroa da Memória (Unsleeping City)
(18, 11), (19, 11), (20, 11),

-- Missão 12: Pedra Filosofal (The Balance)
(21, 12), (22, 12), (23, 12),

-- Missão 13: Trem Assassino (The Balance)
(21, 13), (22, 13), (23, 13),

-- Missão 14: Confrontar Sofrimento (The Balance)
(21, 14), (22, 14), (23, 14),

-- Missão 15: Ratos Gigantes (Grupo Casual)
(24, 15), (25, 15), (26, 15),

-- Missão 16: Ruínas Antigas (Grupo Casual)
(24, 16), (25, 16), (26, 16),

-- Missão 17: Escoltar Caravana (Parte do grupo casual)
(24, 17), (26, 17),

-- Missão 18: Assassino da Névoa (Grupo Casual completo)
(24, 18), (25, 18), (26, 18);