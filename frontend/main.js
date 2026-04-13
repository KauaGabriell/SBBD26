'use strict';

/* ═══════════════════════════════════════════════════
   DADOS REAIS DO BENCHMARK
   Fonte: execução real com PostGIS 3.4 + GeoPandas 0.14
   Dataset: IBGE LULC · Goiás · 2016–2018 · ~680k polígonos
═══════════════════════════════════════════════════ */
const DADOS = {
  sql_media_s:   5.23,
  sql_media_ms:  5236.86,
  py_media_s:    62.28,
  py_media_ms:   62288.20,
  speedup:       11.89,
  reducao_pct:   91.6,
  diferenca_s:   57.05,
  poligonos:     680506,
  poligonos_ano: 340253,
  regiao:        'Goiás, Brasil',
  periodo:       '2016–2018',
  operacao:      'Interseção espacial + cálculo de área',
};

/* ═══════════════════════════════════════════════════
   CHART.JS — CONFIGURAÇÃO BASE
═══════════════════════════════════════════════════ */
const CFG_BASE = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 800, easing: 'easeOutQuart' },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#0d1f14',
      borderColor: 'rgba(26,86,50,0.5)', borderWidth: 1,
      titleFont: { family: "'JetBrains Mono',monospace", size: 11 },
      bodyFont:  { family: "'JetBrains Mono',monospace", size: 11 },
      titleColor: '#d4f2e0', bodyColor: '#8fa898',
      padding: 10, cornerRadius: 6,
    }
  },
  scales: {
    x: {
      ticks: { color: '#8fa898', font: { family: "'JetBrains Mono',monospace", size: 10 } },
      grid:  { color: 'rgba(26,86,50,0.07)' },
      border:{ color: 'rgba(26,86,50,0.12)' },
    },
    y: {
      ticks: { color: '#8fa898', font: { family: "'JetBrains Mono',monospace", size: 10 } },
      grid:  { color: 'rgba(26,86,50,0.07)' },
      border:{ color: 'rgba(26,86,50,0.12)' },
    }
  }
};

/* ═══════════════════════════════════════════════════
   GRÁFICO DE TEMPO (segundos)
═══════════════════════════════════════════════════ */
new Chart(document.getElementById('graf-tempo'), {
  type: 'bar',
  data: {
    labels: ['PostGIS (SQL)', 'GeoPandas (Python)'],
    datasets: [{
      label: 'Tempo médio (s)',
      data: [DADOS.sql_media_s, DADOS.py_media_s],
      backgroundColor: ['rgba(26,86,50,0.25)', 'rgba(224,112,48,0.22)'],
      borderColor:     ['#1a5632', '#e07030'],
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
    }]
  },
  options: {
    ...CFG_BASE,
    scales: {
      ...CFG_BASE.scales,
      y: {
        ...CFG_BASE.scales.y,
        title: {
          display: true, text: 'Tempo médio (s)',
          color: '#8fa898', font: { size: 10, family: "'JetBrains Mono',monospace" }
        }
      }
    },
    plugins: {
      ...CFG_BASE.plugins,
      tooltip: {
        ...CFG_BASE.plugins.tooltip,
        callbacks: {
          label: ctx => ` ${ctx.parsed.y.toFixed(2).replace('.', ',')} segundos`
        }
      }
    }
  }
});

/* ═══════════════════════════════════════════════════
   GRÁFICO EM MILISSEGUNDOS
═══════════════════════════════════════════════════ */
new Chart(document.getElementById('graf-ms'), {
  type: 'bar',
  data: {
    labels: ['PostGIS (SQL)', 'GeoPandas (Python)'],
    datasets: [{
      label: 'Tempo (ms)',
      data: [DADOS.sql_media_ms, DADOS.py_media_ms],
      backgroundColor: ['rgba(26,86,50,0.25)', 'rgba(224,112,48,0.22)'],
      borderColor:     ['#1a5632', '#e07030'],
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
    }]
  },
  options: {
    ...CFG_BASE,
    indexAxis: 'y',
    scales: {
      x: {
        ...CFG_BASE.scales.x,
        title: {
          display: true, text: 'Tempo (ms)',
          color: '#8fa898', font: { size: 10, family: "'JetBrains Mono',monospace" }
        }
      },
      y: CFG_BASE.scales.y
    },
    plugins: {
      ...CFG_BASE.plugins,
      tooltip: {
        ...CFG_BASE.plugins.tooltip,
        callbacks: {
          label: ctx => ` ${ctx.parsed.x.toLocaleString('pt-BR')} ms`
        }
      }
    }
  }
});

/* ═══════════════════════════════════════════════════
   TEXTO DO ARTIGO
═══════════════════════════════════════════════════ */
document.getElementById('texto-artigo').innerHTML =
`Os experimentos foram conduzidos com dados reais de cobertura e uso da terra do <span class="at-hi">estado de Goiás, Brasil</span>, compreendendo aproximadamente <span class="at-num">680.506 polígonos fitofisionômicos</span> (340.253 por ano de referência), obtidos da base <span class="at-hi">IBGE LULC para os anos de 2016 e 2018</span>. A operação avaliada foi a <span class="at-hi">interseção espacial com cálculo de área</span> (ST_Intersection + ST_Area), executada com índice GIST (R-Tree) ativo no PostgreSQL 16 + PostGIS 3.4.

A abordagem <span class="at-hi">In-Database (PostGIS)</span> apresentou tempo médio de <span class="at-num">5,23 segundos</span> (5.236,86 ms), enquanto a abordagem <span class="at-py">Middleware Python (GeoPandas 0.14)</span> registrou <span class="at-num">62,28 segundos</span> (62.288,20 ms). O fator de speedup observado foi de <span class="at-num">11,89×</span>, representando uma redução de <span class="at-num">91,6%</span> no tempo de processamento ao optar pela arquitetura in-database.

A vantagem do PostGIS se explica pelo <span class="at-hi">Princípio da Localidade de Dados</span>: o processamento ocorre diretamente onde os dados residem, eliminando o custo de serialização e transferência de ~680 mil polígonos para o processo cliente Python. O índice <span class="at-hi">GIST (R-Tree)</span> permite filtragem espacial em O(log n) antes da operação de interseção, e a execução nativa em C/C++ via biblioteca GEOS reduz o overhead de interpretação presente no Python.

Os resultados validam empiricamente a adoção da arquitetura in-database para processamento geoespacial de larga escala no contexto de transição fitofisionômica, sendo esta a abordagem recomendada para aplicações com volumes similares ou superiores ao dataset de Goiás aqui utilizado.
<span class="at-ref">
Referência da configuração: PostgreSQL 16, PostGIS 3.4, Python 3.11, GeoPandas 0.14, Shapely 2.0, Docker.
Fonte dos dados: IBGE — Mapeamento de Uso e Cobertura da Terra (LULC), Goiás, 2016–2018.</span>`;

/* ═══════════════════════════════════════════════════
   COPIAR RESULTADOS PARA ARTIGO
═══════════════════════════════════════════════════ */
function copiarResultados() {
  const texto =
`RESULTADOS — GeoBench · SBBD 2026 · Goiás 2016–2018
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Região:       Goiás, Brasil
Volume:       ~680.506 polígonos (340.253/ano)
Operação:     Interseção espacial + cálculo de área
Período:      2016–2018 (IBGE LULC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostGIS (SQL)         5,23 s    (5.236,86 ms)
GeoPandas (Python)   62,28 s   (62.288,20 ms)
Speedup:             11,89× (SQL mais rápido)
Redução:             91,6% no tempo de execução
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conclusão: In-database (PostGIS) é a melhor
abordagem para processamento geoespacial em
larga escala.`;
  navigator.clipboard.writeText(texto);
  mostrarToast('Resultados copiados para a área de transferência!');
}

/* ═══════════════════════════════════════════════════
   COPIAR TRECHO DO ARTIGO
═══════════════════════════════════════════════════ */
function copiarArtigo() {
  const el = document.getElementById('texto-artigo');
  navigator.clipboard.writeText(el.innerText);
  mostrarToast('Trecho do artigo copiado!');
}

/* ═══════════════════════════════════════════════════
   EXPORTAR TABELA LATEX
═══════════════════════════════════════════════════ */
function copiarLatex() {
  const latex =
`\\begin{table}[ht]
\\centering
\\caption{Resultados do benchmark geoespacial --- Goiás 2016--2018}
\\label{tab:geobench-goias}
\\begin{tabular}{lrrl}
\\hline
\\textbf{Método} & \\textbf{Tempo médio (s)} & \\textbf{Tempo (ms)} & \\textbf{Observação} \\\\
\\hline
PostGIS (In-Database) & 5,23 & 5.236,86 & Índice GIST ativo \\\\
GeoPandas (Python)    & 62,28 & 62.288,20 & geopandas.overlay() \\\\
\\hline
\\multicolumn{2}{l}{\\textbf{Speedup}} & \\multicolumn{2}{r}{\\textbf{11,89$\\times$ favorável ao PostGIS}} \\\\
\\hline
\\end{tabular}
\\\\[4pt]
\\small{Dados: IBGE LULC, Goiás 2016--2018. Volume: $\\sim$680.506 polígonos.}
\\end{table}`;
  navigator.clipboard.writeText(latex);
  mostrarToast('Tabela LaTeX copiada para a área de transferência!');
}

/* ═══════════════════════════════════════════════════
   TOAST
═══════════════════════════════════════════════════ */
function mostrarToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('visivel');
  setTimeout(() => t.classList.remove('visivel'), 3200);
}

/* ═══════════════════════════════════════════════════
   NAVEGAÇÃO LATERAL
═══════════════════════════════════════════════════ */
function ir(id, btn) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  if (btn) {
    document.querySelectorAll('.lat-nav-item').forEach(x => x.classList.remove('ativo'));
    btn.classList.add('ativo');
  }
}

/* ═══════════════════════════════════════════════════
   TABS DO MAPA
═══════════════════════════════════════════════════ */
document.querySelectorAll('.mapa-nav-item').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.mapa-nav-item').forEach(x => x.classList.remove('ativo'));
    el.classList.add('ativo');
  });
});

/* ═══════════════════════════════════════════════════
   SPEEDUP NO HERO (calculado a partir dos dados reais)
═══════════════════════════════════════════════════ */
(function () {
  const sp = (DADOS.py_media_s / DADOS.sql_media_s).toFixed(2).replace('.', ',');
  document.querySelectorAll('.hero-destaque-num').forEach(el => el.textContent = sp + '×');
}());
