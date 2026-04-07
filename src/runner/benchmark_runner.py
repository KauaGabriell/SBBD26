import os
import sys
import time
import json
import psutil
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv

# Adicionar raiz do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.scenarios.scenario_a_sql.executor import run_scenario_a
from src.scenarios.scenario_b_python.run_geopandas import run_scenario_b

load_dotenv('.env')
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# CONFIGURAÇÕES
N_RODADAS = 3
RESULTS_DIR = 'results'
RAW_CSV = os.path.join(RESULTS_DIR, 'benchmark_raw.csv')

def get_years_from_db():
    """Detecta quais anos de dados existem no banco de dados."""
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT DISTINCT ano FROM fitofisionomias ORDER BY ano"))
        years = [row[0] for row in res]
    return years

def get_process_metrics():
    process = psutil.Process(os.getpid())
    return {
        'cpu': psutil.cpu_percent(interval=None),
        'mem_rss_mb': process.memory_info().rss / (1024 * 1024)
    }

def run_benchmark():
    years = get_years_from_db()
    if len(years) < 2:
        print(f"Erro: São necessários pelo menos 2 anos de dados. Encontrados: {years}")
        return

    # Gerar pares automáticos (Ex: 2016-2018, 2018-2020)
    pares_anos = [(years[i], years[i+1]) for i in range(len(years)-1)]
    
    print(f"--- INICIANDO GEOBENCH-SBBD 2026 ({datetime.now()}) ---")
    print(f"Janelas Temporais Detectadas: {pares_anos}")
    
    all_metrics = []
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    for ano_inicio, ano_fim in pares_anos:
        print(f"\n🚀 Testando Janela: {ano_inicio} -> {ano_fim}")
        
        for rodada in tqdm(range(1, N_RODADAS + 1), desc="Rodadas"):
            # SQL
            m_before = get_process_metrics()
            res_a = run_scenario_a(ano_inicio, ano_fim)
            m_after = get_process_metrics()
            
            if res_a['success']:
                all_metrics.append({
                    'rodada': rodada, 'cenario': 'SQL (In-Database)',
                    'ano_inicio': ano_inicio, 'ano_fim': ano_fim,
                    'tempo_total_ms': res_a['time_ms'],
                    'cpu_avg': (m_before['cpu'] + m_after['cpu']) / 2,
                    'mem_max': max(m_before['mem_rss_mb'], m_after['mem_rss_mb'])
                })
            
            time.sleep(1)

            # Python
            m_before = get_process_metrics()
            res_b = run_scenario_b(ano_inicio, ano_fim)
            m_after = get_process_metrics()
            
            if res_b['success']:
                all_metrics.append({
                    'rodada': rodada, 'cenario': 'Python (Middleware)',
                    'ano_inicio': ano_inicio, 'ano_fim': ano_fim,
                    'tempo_total_ms': res_b['time_total_ms'],
                    'cpu_avg': (m_before['cpu'] + m_after['cpu']) / 2,
                    'mem_max': max(m_before['mem_rss_mb'], m_after['mem_rss_mb'])
                })
            
            time.sleep(1)

    df_raw = pd.DataFrame(all_metrics)
    df_raw.to_csv(RAW_CSV, index=False)
    print(f"\n✅ Benchmark concluído! Dados em {RAW_CSV}")

if __name__ == "__main__":
    run_benchmark()
