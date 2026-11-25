# Rodomax HUB — Detecção de Anomalias em Fretes

Sistema de integração de dados e análise preditiva desenvolvido para o projeto **UNIVEL x RODOMAX** (4º Período — Data Science e IA).

## Sobre o Projeto
O sistema coleta pedidos de frete em múltiplos formatos (`CSV`, `JSON` e `XLSX`), realiza o saneamento e padronização da base e aplica um modelo de **Inteligência Artificial** para sinalizar automaticamente valores fora do padrão (`NORMAL` ou `REVISAR`) antes da aprovação operacional.

## Como a Solução Funciona
1. **ETL e Saneamento:** Remoção de registros incompletos, duplicados e padronização de campos via `Pandas`.
2. **Análise com IA:** Aplicação de estatística robusta (**Mediana + MAD**) combinada com **Isolation Forest** sobre o logaritmo do valor do frete.
3. **Banco e Interface:** Armazenamento no **PostgreSQL** e disponibilização em uma **API Flask** com painel web para consulta e cadastro em tempo real.

## Stack Utilizada
* **Backend & Dados:** Python, Pandas, NumPy, Scikit-Learn, Flask
* **Banco de Dados:** PostgreSQL, SQLAlchemy, Psycopg
* **Frontend:** HTML5, CSS3, JavaScript

## Organização dos Arquivos
* `main.py` — Executa o pipeline completo (leitura, limpeza, IA e gravação no banco)
* `api.py` — API REST e servidor do painel web (`http://localhost:5000`)
* `src/ia_classificacao.py` — Modelo híbrido de detecção de anomalias
* `src/pipeline.py` — Orquestração das etapas de limpeza, normalização e validação
* `src/banco.py` — Conexão e persistência no PostgreSQL
* `frontend/index.html` — Interface visual do sistema
* `data/` — Bases brutas (`raw`) e arquivos processados/logs (`processed`)

