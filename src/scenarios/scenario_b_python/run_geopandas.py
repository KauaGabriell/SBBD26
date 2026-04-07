import os
import time
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# Carregar variáveis do .env na raiz do projeto
env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(env_path)

def get_engine():
    """Retorna o engine de conexão do SQLAlchemy."""
    url = URL.create(
        drivername="postgresql",
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME')
    )
    return create_engine(url)

def run_scenario_b(ano_inicio, ano_fim):
    """
    Executa o Cenário B (Python/GeoPandas Middleware) e retorna o tempo e os dados.
    """
    engine = None
    try:
        engine = get_engine()
        
        # 1. Medir Tempo de I/O (Fetch do banco)
        start_io = time.perf_counter()
        
        query_base = f"SELECT poligono_id, classe as classe_origem, geom FROM fitofisionomias WHERE ano = {ano_inicio}"
        query_seguinte = f"SELECT poligono_id, classe as classe_destino, geom FROM fitofisionomias WHERE ano = {ano_fim}"
        
        # Ler Geometrias Brutas (SRID 4674 - SIRGAS 2000)
        df_base = gpd.read_postgis(query_base, engine, geom_col='geom')
        df_seguinte = gpd.read_postgis(query_seguinte, engine, geom_col='geom')
        
        end_io = time.perf_counter()
        time_io_ms = (end_io - start_io) * 1000

        # 2. Medir Tempo de Processamento GeoPandas
        start_proc = time.perf_counter()
        
        # Realizar Interseção Espacial em Memória (Overlay)
        # how='intersection' mantém apenas as áreas que se sobrepõem
        intersecoes = gpd.overlay(df_base, df_seguinte, how='intersection')
        
        # Calcular área em m2 (Projetando para EPSG:5880 - SIRGAS 2000 / Brazil Polyconic para Goiás)
        # Necessário para cálculo de área em metros
        intersecoes = intersecoes.to_crs(epsg=5880)
        intersecoes['area_m2'] = intersecoes.geometry.area
        
        # Agregação (Agrupar por classes de origem e destino)
        res_grouped = intersecoes.groupby(['classe_origem', 'classe_destino']).agg(
            n_poligonos=('poligono_id_1', 'count'), # id do primeiro df após overlay
            area_m2_sum=('area_m2', 'sum')
        ).reset_index()
        
        # Formatar resultados para o mesmo schema do Cenário A
        results = []
        for _, row in res_grouped.iterrows():
            results.append({
                'classe_origem': row['classe_origem'],
                'classe_destino': row['classe_destino'],
                'n_poligonos': int(row['n_poligonos']),
                'area_m2': float(row['area_m2_sum'])
            })
            
        end_proc = time.perf_counter()
        time_proc_ms = (end_proc - start_proc) * 1000
        time_total_ms = time_io_ms + time_proc_ms

        return {
            'success': True,
            'time_io_ms': time_io_ms,
            'time_proc_ms': time_proc_ms,
            'time_total_ms': time_total_ms,
            'results': results
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time_io_ms': 0,
            'time_proc_ms': 0,
            'time_total_ms': 0,
            'results': []
        }
    finally:
        if engine:
            engine.dispose()

if __name__ == "__main__":
    # Teste rápido do executor
    print("Testando Cenário B (GeoPandas)...")
    res = run_scenario_b(2005, 2006)
    if res['success']:
        print(f"Sucesso!")
        print(f"  I/O Time: {res['time_io_ms']:.2f}ms")
        print(f"  Proc Time: {res['time_proc_ms']:.2f}ms")
        print(f"  Total Time: {res['time_total_ms']:.2f}ms")
        print(f"  Linhas: {len(res['results'])}")
    else:
        print(f"Erro: {res['error']}")


