-- Colunas da classificação por IA (já criadas no banco local)
ALTER TABLE rodomax.demandas
ADD COLUMN IF NOT EXISTS classificacao_ia VARCHAR(30);

ALTER TABLE rodomax.demandas
ADD COLUMN IF NOT EXISTS score_ia NUMERIC(12,8);

-- Conferir as colunas da tabela
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'rodomax'
AND table_name = 'demandas';

-- Conferir os dados classificados
SELECT
    cliente,
    origem,
    destino,
    valor_frete,
    classificacao_ia,
    score_ia
FROM rodomax.demandas;
