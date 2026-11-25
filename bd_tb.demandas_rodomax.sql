CREATE SCHEMA rodomax;

CREATE TABLE rodomax.demandas (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    telefone VARCHAR(20),
    origem VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    valor_frete NUMERIC(12,2),
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rodomax.logs_processamento (
    id SERIAL PRIMARY KEY,
    data_processamento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    arquivos_processados INTEGER,
    registros_recebidos INTEGER,
    registros_incompletos INTEGER,
    duplicados_removidos INTEGER,
    registros_finais INTEGER,
    registros_inseridos INTEGER,
    registros_ignorados INTEGER
);

CREATE TABLE IF NOT EXISTS rodomax.importacoes (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    arquivos_processados INTEGER NOT NULL,
    registros_recebidos INTEGER NOT NULL,
    registros_incompletos INTEGER NOT NULL,
    duplicados_removidos INTEGER NOT NULL,
    registros_finais INTEGER NOT NULL,
    registros_inseridos INTEGER NOT NULL,
    registros_ignorados INTEGER NOT NULL
);

TRUNCATE TABLE rodomax.demandas RESTART IDENTITY;

SELECT *
FROM rodomax.demandas;
