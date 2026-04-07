# 📊 Relatório Técnico: Benchmark de Processamento Geoespacial (Goiás 2016-2018)

Este documento apresenta os resultados do benchmark entre o processamento **In-Database (PostGIS)** e o processamento **Middleware (GeoPandas)**, utilizando dados reais do Índice de Cobertura e Uso de Terras do Estado de Goiás.

## 📋 Resumo dos Dados
- **Abrangência Geográfica:** Estado de Goiás, Brasil.
- **Volume de Dados:** ~680.506 polígonos (340.253 por ano).
- **Operação Testada:** Interseção Espacial (Overlay) + Cálculo de Área por Classe.
- **Hardware de Teste:** Executado em ambiente local (CPU x86_64).

## 📈 Resultados Comparativos

A tabela abaixo resume os tempos médios obtidos após 3 rodadas de execução:

| Cenário de Execução | Tempo Médio (ms) | Tempo Médio (s) | Performance Relativa (Speedup) |
| :--- | :--- | :--- | :--- |
| **PostGIS (SQL)** | ~5.236,86 | 5,23s | **11,89x mais rápido** |
| **GeoPandas (Python)** | ~62.288,20 | 62,28s | 1,00x (Referência) |

## 🧠 Análise de Arquitetura

### 1. O Princípio da Localidade de Dados
A vitória esmagadora do **PostGIS** confirma o princípio da localidade: **é mais barato mover o código até o dado do que mover o dado até o código.** 
No cenário do GeoPandas, o computador precisou:
1.  Ler 340 mil registros do disco/banco.
2.  Transferir via rede (I/O).
3.  Desserializar em memória RAM.
4.  Processar sem o auxílio de índices espaciais pré-calculados no banco.

### 2. O Poder do Índice GIST
O PostGIS utiliza índices **R-Tree (GIST)**. Isso permite que ele ignore polígonos que não se sobrepõem geograficamente antes mesmo de começar o cálculo. O GeoPandas, por padrão, realiza uma comparação muito mais custosa em termos de CPU e Memória para volumes deste tamanho.

## 🏁 Conclusão
Para análises de larga escala (Estado ou País), a arquitetura **In-Database** é a única viável para produção. O GeoPandas permanece excelente para prototipagem rápida e visualização de pequenos recortes de dados, mas sofre gargalos significativos de I/O e processamento em cenários de Big Data Geográfico.

