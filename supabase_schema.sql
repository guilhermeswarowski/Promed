-- ============================================================
--  Promed CRM · Schema para Supabase (PostgreSQL)
--  Execute este arquivo no SQL Editor do Supabase
-- ============================================================

CREATE TABLE IF NOT EXISTS clientes (
    id        BIGSERIAL PRIMARY KEY,
    nome      TEXT NOT NULL,
    email     TEXT,
    telefone  TEXT,
    empresa   TEXT,
    status    TEXT DEFAULT 'Ativo',
    origem    TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    notas     TEXT
);

CREATE TABLE IF NOT EXISTS negocios (
    id               BIGSERIAL PRIMARY KEY,
    titulo           TEXT NOT NULL,
    cliente_id       BIGINT REFERENCES clientes(id) ON DELETE SET NULL,
    valor            NUMERIC DEFAULT 0,
    estagio          TEXT DEFAULT 'Prospecção',
    probabilidade    INTEGER DEFAULT 0,
    data_fechamento  TEXT,
    criado_em        TIMESTAMPTZ DEFAULT NOW(),
    notas            TEXT
);

CREATE TABLE IF NOT EXISTS atividades (
    id              BIGSERIAL PRIMARY KEY,
    tipo            TEXT NOT NULL,
    descricao       TEXT,
    cliente_id      BIGINT REFERENCES clientes(id) ON DELETE SET NULL,
    negocio_id      BIGINT REFERENCES negocios(id) ON DELETE SET NULL,
    responsavel     TEXT,
    data_atividade  TEXT,
    status          TEXT DEFAULT 'Pendente',
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

-- ── Row Level Security ────────────────────────────────────────────────────────
ALTER TABLE clientes   ENABLE ROW LEVEL SECURITY;
ALTER TABLE negocios   ENABLE ROW LEVEL SECURITY;
ALTER TABLE atividades ENABLE ROW LEVEL SECURITY;

-- Permite acesso total via chave anon (ajuste conforme necessidade)
CREATE POLICY "allow_all_clientes"   ON clientes   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_negocios"   ON negocios   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_atividades" ON atividades FOR ALL USING (true) WITH CHECK (true);
