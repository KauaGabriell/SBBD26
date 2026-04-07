import os
import glob
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
from dotenv import load_dotenv

# Carregar configurações do .env
load_dotenv('.env')
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def import_real_data():
    engine = create_engine(DB_URL)
    
    print("Limpando banco de dados...")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fitofisionomias;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("""
            CREATE TABLE fitofisionomias (
                id SERIAL PRIMARY KEY,
                poligono_id INTEGER,
                classe VARCHAR(100),
                ano INTEGER,
                geom GEOMETRY(MultiPolygon, 4674)
            );
        """))
    
    # BUSCA DINÂMICA: Procura por pastas numéricas dentro de 'shp/'
    shp_base_path = "shp"
    year_folders = [f for f in os.listdir(shp_base_path) if f.isdigit()]
    
    if not year_folders:
        print(f"Erro: Nenhuma pasta de ano (ex: 2016) encontrada em '{shp_base_path}/'")
        return

    print(f"Anos detectados para importação: {sorted(year_folders)}")

    for year_str in sorted(year_folders):
        ano = int(year_str)
        folder_path = os.path.join(shp_base_path, year_str)
        
        # Encontrar o primeiro arquivo .shp dentro da pasta do ano
        shp_files = glob.glob(os.path.join(folder_path, "*.shp"))
        if not shp_files:
            print(f"Aviso: Nenhum .shp encontrado na pasta {folder_path}. Pulando...")
            continue
            
        path = shp_files[0]
        print(f"\nProcessando Ano {ano} (Arquivo: {os.path.basename(path)})...")
        
        gdf = gpd.read_file(path)
        
        if gdf.crs is None or gdf.crs.to_epsg() != 4674:
            gdf = gdf.to_crs(epsg=4674)
        
        gdf['ano'] = ano
        gdf['p_id'] = gdf.index + 1
        
        print(f"Convertendo {len(gdf)} geometrias para WKT...")
        gdf['geom_wkt'] = gdf.geometry.to_wkt()
        
        df_to_save = gdf[['p_id', 'classe', 'ano', 'geom_wkt']].dropna(subset=['geom_wkt'])
        records = df_to_save.to_dict('records')

        batch_size = 5000
        total = len(records)
        print(f"Inserindo no PostGIS (Lotes de {batch_size})...")
        
        for i in tqdm(range(0, total, batch_size), desc=f"Gravando {ano}"):
            batch = records[i:i + batch_size]
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO fitofisionomias (poligono_id, classe, ano, geom) 
                        VALUES (:p_id, :classe, :ano, ST_Multi(ST_GeomFromText(:geom_wkt, 4674)))
                    """),
                    batch
                )
        print(f"Sucesso ao importar Ano {ano}!")

    print("\nFinalizando: Criando índices espaciais...")
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX idx_fitofisionomias_geom ON fitofisionomias USING GIST(geom);"))
        conn.execute(text("CREATE INDEX idx_fitofisionomias_ano ON fitofisionomias(ano);"))
    
    print("\n✅ Importação concluída para todos os anos detectados!")

if __name__ == "__main__":
    import_real_data()
