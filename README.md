# 🌎 GeoBench-SBBD 2026: Benchmark de Performance Geoespacial Universal

Este projeto é um framework para análise comparativa de performance entre o processamento **In-Database (PostGIS)** e o processamento **Middleware (GeoPandas)**. Ele foi desenhado para ser **agnóstico a localização**, permitindo testar qualquer conjunto de dados de cobertura e uso de terra (Shapefiles).

O objetivo é validar o **Princípio da Localidade de Dados**: processar informações geográficas massivas diretamente onde residem (no banco de dados) vs. transferi-las para o código (Python).

---

## 📊 Destaques do Projeto
- **Universal:** Funciona com qualquer Estado, País ou Recorte Geográfico.
- **Escalável:** Detecta automaticamente múltiplos anos de análise.
- **Visualização Premium:** Dashboards automáticos com tema Dark (estilo GitHub).
- **Relatório Técnico:** Análise detalhada dos resultados e speedup.

---

## 🚀 Como Executar

### 1. Infraestrutura (Docker)
Suba o banco de dados espacial (PostgreSQL 16 + PostGIS):
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Ambiente Python
Instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Importar Dados Geográficos (Qualquer Localidade)
Os arquivos Shapefile (.shp) podem ser baixados em plataformas oficiais (ex: **IBGE** para o Brasil):
- **Fonte Sugerida:** [IBGE - Mudança na Cobertura e Uso da Terra](https://www.ibge.gov.br/geociencias/cartas-e-mapas/informacoes-ambientais/15831-mudanca-na-cobertura-e-uso-da-terra.html)
- **Instruções:** Extraia os dados para pastas numeradas dentro de `shp/` (ex: `shp/2016/`, `shp/2018/`) e execute a importação:
```bash
python src/seed/seed_real_data.py
```
*O script detecta automaticamente os anos e arquivos .shp presentes nas pastas.*

### 4. Execução do Benchmark
Roda as rodadas de teste comparativo para todos os pares de anos detectados:
```bash
python src/runner/benchmark_runner.py
```

### 5. Geração de Resultados
Gera o Dashboard Profissional e os KPIs de performance:
```bash
python src/analysis/plot_results.py
```

---

## 📂 Estrutura do Projeto
- **`src/scenarios/`**: Lógica de cálculo (SQL puro vs GeoPandas Overlay).
- **`results/figures/`**: Galeria de gráficos gerados (Boxplot, Violin, Speedup Hero).
- **`results/ANALISE_TECNICA.md`**: Relatório detalhado com a conclusão científica.

---

## 🏁 Conclusão Esperada
Os testes demonstram que para grandes volumes de dados geográficos, a arquitetura **In-Database** elimina o gargalo de transferência de dados (I/O), resultando em speedups significativos (frequentemente superiores a 10x).

*Desenvolvido para fins acadêmicos (SBBD 2026).*
