import os
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Carregar variaveis do .env na raiz do projeto
env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(env_path)

def get_connection():
    """Retorna uma conexão com o banco de dados PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def run_scenario_a(ano_inicio, ano_fim):
    """
    Executa o Cenario A (SQL/PostGIS In-Database) e retorna o tempo e os dados.
    """
    conn = None
    try:
        # 1. Ler o arquivo SQL
        sql_file_path = os.path.join(os.path.dirname(__file__), 'run_query.sql')
        with open(sql_file_path, 'r', encoding='latin-1') as f:
            query = f.read()

        conn = get_connection()
        # Usar DictCursor para retornar os resultados como dicionarios
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # 2. Executar e medir o tempo (ms)
        start_time = time.perf_counter()
        cur.execute(query, {'ano_inicio': ano_inicio, 'ano_fim': ano_fim})
        results = [dict(row) for row in cur.fetchall()]
        end_time = time.perf_counter()

        execution_time_ms = (end_time - start_time) * 1000

        cur.close()
        return {
            'success': True,
            'time_ms': execution_time_ms,
            'results': results
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'time_ms': 0,
            'results': []
        }
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Teste rapido do executor
    print("Testando Cenario A (SQL)...")
    res = run_scenario_a(2005, 2006)
    if res['success']:
        print(f"Sucesso! Tempo: {res['time_ms']:.2f}ms | Linhas: {len(res['results'])}")
    else:
        print(f"Erro: {res['error']}")


