-- 1) PRÉVIA: mostra as linhas duplicadas que seriam apagadas (mantém a de menor id)
SELECT b.id, b.cliente, b.email, b.origem, b.destino, b.valor_frete, b.fonte
FROM rodomax.demandas a
JOIN rodomax.demandas b
  ON a.id < b.id
 AND a.cliente = b.cliente
 AND a.email IS NOT DISTINCT FROM b.email
 AND a.telefone IS NOT DISTINCT FROM b.telefone
 AND a.origem = b.origem
 AND a.destino = b.destino
 AND a.valor_frete IS NOT DISTINCT FROM b.valor_frete
ORDER BY b.id;

-- 2) Depois de conferir a prévia, execute o DELETE abaixo
DELETE FROM rodomax.demandas b
USING rodomax.demandas a
WHERE a.id < b.id
  AND a.cliente = b.cliente
  AND a.email IS NOT DISTINCT FROM b.email
  AND a.telefone IS NOT DISTINCT FROM b.telefone
  AND a.origem = b.origem
  AND a.destino = b.destino
  AND a.valor_frete IS NOT DISTINCT FROM b.valor_frete;
