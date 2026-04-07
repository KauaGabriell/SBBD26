# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os, shutil
from tabulate import tabulate

# ── Paleta & Estilo (Tema Dark/GitHub) ──────────────────────────────────────────
BG_DARK   = "#0D1117"
BG_CARD   = "#161B22"
BG_CARD2  = "#1C2333"
GRID_C    = "#21262D"
TEXT_PRI  = "#E6EDF3"
TEXT_SEC  = "#8B949E"
ACCENT_R  = "#FF6B6B"   # Python / vermelho
ACCENT_G  = "#3DD68C"   # PostGIS / verde
ACCENT_B  = "#58A6FF"   # detalhe azul
ACCENT_Y  = "#F0C419"   # destaque amarelo

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG_CARD)
    ax.tick_params(colors=TEXT_SEC, labelsize=11)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
        spine.set_visible(True)
    ax.xaxis.label.set_color(TEXT_SEC)
    ax.yaxis.label.set_color(TEXT_SEC)
    ax.set_xlabel(xlabel, fontsize=12, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=12, labelpad=10)
    ax.yaxis.grid(True, color=GRID_C, linewidth=0.8, zorder=0, linestyle='--')
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', color=TEXT_PRI, pad=14, loc='left')

def generate_professional_plots():
    results_dir  = 'results'
    figures_dir  = os.path.join(results_dir, 'figures')
    raw_csv      = os.path.join(results_dir, 'benchmark_raw.csv')

    if not os.path.exists(raw_csv):
        print(f"Erro: {raw_csv} não encontrado.")
        return

    if os.path.exists(figures_dir):
        shutil.rmtree(figures_dir)
    os.makedirs(figures_dir, exist_ok=True)

    df = pd.read_csv(raw_csv)

    # Detectar anos para o título
    anos = sorted(pd.concat([df['ano_inicio'], df['ano_fim']]).unique())
    label_anos = f"{anos[0]}-{anos[-1]}" if len(anos) >= 2 else "Goiás"

    py_data  = df[df['cenario'].str.contains('Python')]['tempo_total_ms'].values
    sql_data = df[df['cenario'].str.contains('SQL')]['tempo_total_ms'].values
    py_avg   = py_data.mean(); sql_avg = sql_data.mean()
    speedup  = py_avg / sql_avg

    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans', 'Arial'], 
                         'axes.unicode_minus': False, 'figure.facecolor': BG_DARK, 
                         'savefig.facecolor': BG_DARK, 'text.color': TEXT_PRI})

    # FIGURA 1 — DASHBOARD
    fig = plt.figure(figsize=(20, 12))
    fig.text(0.04, 0.95, f"GEOBENCH-SBBD 2026 · Analise {label_anos}", fontsize=24, fontweight='bold', color=TEXT_PRI, va='top')
    fig.text(0.04, 0.91, "Comparativo de Performance: PostGIS (In-Database) vs GeoPandas (Middleware)", fontsize=14, color=TEXT_SEC, va='top')
    
    gs = gridspec.GridSpec(2, 3, figure=fig, top=0.85, bottom=0.08, left=0.05, right=0.97, hspace=0.45, wspace=0.32)

    ax_box = fig.add_subplot(gs[:, 0]); style_ax(ax_box, "A · Distribuicao do Tempo", ylabel="Tempo (ms)")
    ax_vio = fig.add_subplot(gs[0, 1]); style_ax(ax_vio, "B · Densidade de Probabilidade")
    ax_bar = fig.add_subplot(gs[0, 2]); style_ax(ax_bar, "C · Tempo Medio & Speedup")

    # Plots... (Omitidos para brevidade, mantendo lógica anterior)
    for pos, data, col in zip([1, 2], [py_data, sql_data], [ACCENT_R, ACCENT_G]):
        ax_box.boxplot(data, positions=[pos], widths=0.4, patch_artist=True, notch=True, boxprops=dict(facecolor=col+'33', color=col, linewidth=2), medianprops=dict(color=ACCENT_Y, linewidth=2))
        ax_box.scatter(np.full(len(data), pos) + np.random.uniform(-0.1, 0.1, len(data)), data, color=col, alpha=0.3, s=20)
    ax_box.set_xticks([1, 2]); ax_box.set_xticklabels(["Python", "PostGIS"])

    for i, (data, col) in enumerate(zip([py_data, sql_data], [ACCENT_R, ACCENT_G]), start=1):
        parts = ax_vio.violinplot(data, positions=[i], showmeans=True)
        parts['bodies'][0].set_facecolor(col); parts['bodies'][0].set_alpha(0.4)
    ax_vio.set_xticks([1, 2]); ax_vio.set_xticklabels(["Python", "PostGIS"])

    x_pos = [0.3, 0.7]
    for xp, val, col in zip(x_pos, [py_avg, sql_avg], [ACCENT_R, ACCENT_G]):
        ax_bar.bar(xp, val, width=0.25, color=col, alpha=0.8, zorder=3)
        ax_bar.text(xp, val + py_avg*0.02, f"{val/1000:.2f}s", ha='center', va='bottom', fontweight='bold')
    
    yline = py_avg * 1.15
    ax_bar.annotate("", xy=(x_pos[1], yline), xytext=(x_pos[0], yline), arrowprops=dict(arrowstyle='<->', color=ACCENT_Y, lw=2))
    ax_bar.text(0.5, yline + py_avg*0.04, f"{speedup:.1f}x mais rápido", ha='center', color=ACCENT_Y, fontweight='bold')
    ax_bar.set_xlim(0, 1); ax_bar.set_xticks([]); ax_bar.set_ylim(0, py_avg * 1.4)

    # KPIs
    ax_kpi = fig.add_subplot(gs[1, 1:]); ax_kpi.set_axis_off()
    kpis = [(f"{speedup:.1f}×", "Speedup PostGIS", ACCENT_G), (f"{py_avg/1000:.2f}s", "Média Python", ACCENT_R), 
            (f"{sql_avg/1000:.2f}s", "Média PostGIS", ACCENT_G), (f"{len(df)}", "Execuções", ACCENT_B),
            (f"{py_data.std():.0f}ms", "Desv. Padrão PY", ACCENT_R), (f"{sql_data.std():.0f}ms", "Desv. Padrão SQL", ACCENT_G)]
    
    card_w, card_h = 0.28, 0.40; gap_x, gap_y = 0.045, 0.10; pad_left, pad_top = 0.04, 0.55
    for idx, (val, lbl, col) in enumerate(kpis):
        x0 = pad_left + (idx%3) * (card_w + gap_x); y0 = pad_top - (idx//3) * (card_h + gap_y)
        ax_kpi.add_patch(FancyBboxPatch((x0, y0), card_w, card_h, boxstyle="round,pad=0.01", facecolor=BG_CARD, edgecolor=col, linewidth=1.5, transform=ax_kpi.transAxes))
        ax_kpi.text(x0 + card_w/2, y0 + card_h*0.65, val, ha='center', color=col, fontsize=20, fontweight='bold', transform=ax_kpi.transAxes)
        ax_kpi.text(x0 + card_w/2, y0 + card_h*0.25, lbl, ha='center', color=TEXT_SEC, fontsize=10, transform=ax_kpi.transAxes)

    fig.savefig(os.path.join(figures_dir, 'fig1_dashboard_principal.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    # FIGURA 2 — SPEEDUP HERO
    fig2, ax2 = plt.subplots(figsize=(14, 8)); fig2.patch.set_facecolor(BG_DARK); style_ax(ax2, ylabel="Tempo de Execução (ms)")
    for xp, val, col, lbl in zip([0.3, 0.7], [py_avg, sql_avg], [ACCENT_R, ACCENT_G], ['Python\nMiddleware', 'PostGIS\nIn-Database']):
        ax2.bar(xp, val, width=0.25, color=col, alpha=0.9, zorder=3, edgecolor='white', linewidth=1)
        ax2.text(xp, val + py_avg*0.02, f"{val/1000:.3f}s", ha='center', va='bottom', fontsize=18, fontweight='bold')
        ax2.text(xp, -py_avg*0.08, lbl, ha='center', va='top', color=col, fontsize=13, fontweight='bold')
    ax2.annotate("", xy=(0.7, py_avg*1.1), xytext=(0.3, py_avg*1.1), arrowprops=dict(arrowstyle='<->', color=ACCENT_Y, lw=3))
    ax2.text(0.5, py_avg*1.14, f"{speedup:.1f}x Mais Rápido", ha='center', color=ACCENT_Y, fontsize=22, fontweight='bold')
    ax2.set_xlim(0, 1); ax2.set_xticks([]); ax2.set_ylim(0, py_avg*1.3)
    fig2.text(0.5, 0.95, f"POSTGIS: PERFORMANCE EM GOIÁS ({label_anos})", fontsize=22, fontweight='bold', color=TEXT_PRI, ha='center')
    fig2.savefig(os.path.join(figures_dir, 'fig2_speedup_hero.png'), dpi=200, bbox_inches='tight')
    plt.close(fig2)

    print(f"\n✅ Gráficos gerados para a janela: {label_anos}")

if __name__ == "__main__":
    generate_professional_plots()
