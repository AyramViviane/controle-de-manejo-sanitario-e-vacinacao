-- =====================================================================
-- PROJETO: Controle de Manejo Sanitário e Vacinação (SQLite)
-- =====================================================================

-- 1. TABELAS DO SISTEMA
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    quantidade_animais INTEGER NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vacinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_vacina TEXT NOT NULL,
    fabricante TEXT,
    dosagem_recomendada TEXT
);

CREATE TABLE IF NOT EXISTS manejo_sanitario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL,
    tipo_manejo TEXT NOT NULL,
    data_manejo DATE NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (lote_id) REFERENCES lotes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vacinacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL,
    vacina_id INTEGER NOT NULL,
    data_vacinacao DATE NOT NULL,
    proxima_dose DATE,
    FOREIGN KEY (lote_id) REFERENCES lotes(id) ON DELETE CASCADE,
    FOREIGN KEY (vacina_id) REFERENCES vacinas(id) ON DELETE CASCADE
);

-- Tabela de Usuários (Atende ao critério de múltiplos usuários no BD)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL -- 'admin' ou 'app_user'
);

-- Tabela de Auditoria / Logs
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acao TEXT,
    detalhes TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Inserindo usuários padrão (Admin e Aplicação)
INSERT OR IGNORE INTO usuarios (username, senha, perfil) VALUES ('admin_db', 'AdminSecure2026*', 'admin');
INSERT OR IGNORE INTO usuarios (username, senha, perfil) VALUES ('app_user', 'AppManejo2026!', 'app_user');
 
-- 2. TRIGGER (Gatilho) NO SQLITE
-- Registra um log de auditoria automaticamente após a inserção de um manejo
CREATE TRIGGER IF NOT EXISTS trg_after_insert_manejo
AFTER INSERT ON manejo_sanitario
BEGIN
    INSERT INTO audit_log (acao, detalhes) 
    VALUES ('INSERCAO_MANEJO', 'Novo manejo cadastrado para o lote ID: ' || NEW.lote_id);
END;