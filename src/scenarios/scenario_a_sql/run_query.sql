-- Calcula matriz de transição entre ano base e ano seguinte
-- Parâmetros: %(ano_inicio)s e %(ano_fim)s (substituídos pelo runner)
WITH
  base AS (
    SELECT poligono_id, classe AS classe_origem, geom
    FROM fitofisionomias
    WHERE ano = %(ano_inicio)s
  ),
  seguinte AS (
    SELECT poligono_id, classe AS classe_destino, geom
    FROM fitofisionomias
    WHERE ano = %(ano_fim)s
  ),
  intersecoes AS (
    SELECT
      b.classe_origem,
      s.classe_destino,
      ST_Intersection(b.geom, s.geom) AS geom_intersec
    FROM base b
    JOIN seguinte s ON b.poligono_id = s.poligono_id
    WHERE ST_Intersects(b.geom, s.geom)
  )
SELECT
  classe_origem,
  classe_destino,
  COUNT(*) AS n_poligonos,
  SUM(ST_Area(geom_intersec::geography)) AS area_m2
FROM intersecoes
GROUP BY classe_origem, classe_destino
ORDER BY classe_origem, classe_destino;
