"""Fase 4 — las verificaciones del análisis.

Cada bloque puede tumbar un hallazgo. Se ejecutan después de analizar.py y su salida se
transcribe a CASO.md: un hallazgo sin verificación registrada no llega a la fase 5.

Uso:  python notebooks/verificar.py
"""

import duckdb
from math import comb
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BD = BASE / 'datos' / 'limpios' / 'football-transfer-market.duckdb'


def log(titulo):
    print('\n' + '=' * 78)
    print(titulo)
    print('=' * 78)


def main():
    con = duckdb.connect(str(BD), read_only=True)

    # ---------------------------------------------------------------
    # V1 - Sensatez contra una fuente independiente
    # ---------------------------------------------------------------
    log('V1 - Cuota de gasto en 18-23: nuestra cifra contra el censo de FIFA')
    print('Comparacion por ANO NATURAL, que es la unidad de FIFA. Compararlo por temporada')
    print('mezclaba dos mercados de invierno distintos e inflaba la diferencia.')
    print('La brecha de base es esperada (FIFA solo cuenta traspasos internacionales; nosotros')
    print('tambien los domesticos). Lo que se vigila es que no se dispare.\n')
    print(con.sql("""
        WITH nuestro AS (
          SELECT year(fecha) AS anio,
                 ROUND(100.0 * sum(CASE WHEN tramo_fifa = '18-23' THEN fee_eur ELSE 0 END)
                       / sum(fee_eur), 1) AS pct_b,
                 count(*) AS operaciones
          FROM u1
          WHERE year(fecha) BETWEEN 2023 AND 2025
          GROUP BY year(fecha)
        ),
        censo AS (
          SELECT year AS anio,
                 ROUND(100.0 * sum(CASE WHEN age_band = '18-23' THEN gasto ELSE 0 END)
                       / sum(gasto), 1) AS pct_a
          FROM (
            SELECT year, age_band,
                   COALESCE(total_fee_usd_m,
                            transfers_total * pct_with_fee / 100.0 * avg_fee_usd_m) AS gasto
            FROM raw_fifa_edad
          ) GROUP BY year
        )
        SELECT n.anio, n.operaciones, n.pct_b AS fuente_b, c.pct_a AS fuente_a,
               ROUND(c.pct_a - n.pct_b, 1) AS brecha_puntos
        FROM nuestro n JOIN censo c USING (anio)
        ORDER BY n.anio
    """))
    print('LIMITACION: en 2025 la brecha se duplica (7,1 puntos) y no se puede atribuir con')
    print('certeza. Las dos fuentes discrepan incluso en la DIRECCION de la cuota juvenil, asi')
    print('que ninguna afirmacion sobre su nivel o su tendencia se sostiene. La comparacion que')
    print('si aguanta es la de precios relativos: V1b.')

    # ---------------------------------------------------------------
    # V1b - El hallazgo principal, contrastado en las dos fuentes
    # ---------------------------------------------------------------
    log('V1b - Precio relativo 18-23 frente a 24-29: ratio de MEDIAS en ambas fuentes')
    print('Es la comparacion honesta: FIFA publica medias, no medianas. Universos distintos y')
    print('niveles distintos, pero si ambas niegan una prima juvenil creciente, el hallazgo')
    print('no depende de nuestra fuente.\n')
    print(con.sql("""
        WITH censo AS (
          SELECT year AS anio,
                 ROUND(max(CASE WHEN age_band = '18-23' THEN media END)
                       / max(CASE WHEN age_band = '24-29' THEN media END), 3) AS ratio_a
          FROM (
            SELECT year, age_band,
                   COALESCE(avg_fee_usd_m,
                            COALESCE(total_fee_usd_m, 0) / NULLIF(transfers_with_fee, 0)) AS media
            FROM raw_fifa_edad
            WHERE age_band IN ('18-23', '24-29')
          )
          GROUP BY year
        ),
        nuestro AS (
          SELECT year(fecha) AS anio,
                 ROUND(avg(CASE WHEN tramo_fifa = '18-23' THEN fee_eur END)
                       / avg(CASE WHEN tramo_fifa = '24-29' THEN fee_eur END), 3) AS ratio_b
          FROM u1 WHERE year(fecha) BETWEEN 2022 AND 2025
          GROUP BY year(fecha)
        )
        SELECT c.anio, c.ratio_a AS fifa, n.ratio_b AS transfermarkt
        FROM censo c LEFT JOIN nuestro n USING (anio)
        WHERE c.anio >= 2022
        ORDER BY c.anio
    """))
    print('Los NIVELES difieren (FIFA por debajo de 1, nosotros ligeramente por encima) porque')
    print('los universos son distintos. Lo que coincide es lo que importa: en ninguna de las dos')
    print('el ratio ESCALA. FIFA va de 0,971 a 0,909 y nosotros de 1,07 a 1,072.')

    # ---------------------------------------------------------------
    # V5b - ¿El hallazgo aguanta si se cambia la especificación?
    # ---------------------------------------------------------------
    log('V5b - Robustez: el mismo ratio en las cuatro especificaciones posibles')
    print('Con solo cuatro observaciones, un resultado que depende de como se corte el tiempo')
    print('o de que estadistico se use no es un hallazgo, es una eleccion.\n')
    print(con.sql("""
        WITH combinado AS (
          SELECT temporada AS periodo, 'temporada' AS corte, tramo_fifa,
                 median(fee_eur) AS med, avg(fee_eur) AS media
          FROM u1 WHERE tramo_fifa IN ('18-23', '24-29')
          GROUP BY temporada, tramo_fifa
          UNION ALL
          SELECT CAST(year(fecha) AS VARCHAR), 'ano natural', tramo_fifa,
                 median(fee_eur), avg(fee_eur)
          FROM u1
          WHERE tramo_fifa IN ('18-23', '24-29') AND year(fecha) BETWEEN 2023 AND 2025
          GROUP BY year(fecha), tramo_fifa
        )
        SELECT corte, periodo,
               ROUND(max(CASE WHEN tramo_fifa = '18-23' THEN med END)
                     / max(CASE WHEN tramo_fifa = '24-29' THEN med END), 3) AS ratio_mediana,
               ROUND(max(CASE WHEN tramo_fifa = '18-23' THEN media END)
                     / max(CASE WHEN tramo_fifa = '24-29' THEN media END), 3) AS ratio_media
        FROM combinado
        GROUP BY corte, periodo
        ORDER BY corte, periodo
    """))
    print('CONCLUSION: la caida de 1,25 a 0,955 solo aparece cortando por temporada, y depende')
    print('de que 22/23 sea el punto de partida mas alto de los siete. La afirmacion se acota:')
    print('el ratio ronda 1 y NO escala. No se afirma que caiga.')

    # ---------------------------------------------------------------
    # V2 - Recálculo por vía alterna
    # ---------------------------------------------------------------
    log('V2 - Cuota del top-10, recalculada desde el detalle en vez de desde el agregado')
    print(con.sql("""
        WITH top10 AS (
          SELECT temporada, club_destino_id,
                 ROW_NUMBER() OVER (PARTITION BY temporada
                                    ORDER BY sum(fee_eur) DESC) AS puesto
          FROM u2 GROUP BY temporada, club_destino_id
        ),
        alterno AS (
          SELECT u2.temporada,
                 ROUND(100.0 * sum(CASE WHEN t.puesto <= 10 THEN u2.fee_eur ELSE 0 END)
                       / sum(u2.fee_eur), 1) AS pct_top10_alterno
          FROM u2 JOIN top10 t
            ON t.temporada = u2.temporada AND t.club_destino_id = u2.club_destino_id
          GROUP BY u2.temporada
        )
        SELECT m.temporada, m.pct_top10 AS via_agregado, a.pct_top10_alterno AS via_detalle,
               CASE WHEN m.pct_top10 = a.pct_top10_alterno THEN 'coincide' ELSE 'DISCREPA' END AS resultado
        FROM m1_concentracion m JOIN alterno a USING (temporada)
        ORDER BY m.temporada
    """))

    # ---------------------------------------------------------------
    # V3 - Denominadores
    # ---------------------------------------------------------------
    log('V3 - Toda cuota suma 100 dentro de su propia temporada')
    print(con.sql("""
        SELECT temporada, ROUND(sum(pct_gasto), 1) AS suma_pct,
               CASE WHEN abs(sum(pct_gasto) - 100) <= 0.3 THEN 'ok' ELSE 'REVISAR' END AS resultado
        FROM m3_edad GROUP BY temporada ORDER BY temporada
    """))

    # ---------------------------------------------------------------
    # V4 - Desagregar un nivel: ¿es un fenómeno inglés?
    # ---------------------------------------------------------------
    log('V4 - La desconcentracion, excluyendo a los compradores ingleses')
    print('Si solo ocurriera con Inglaterra dentro, el agregado europeo estaria escondiendo')
    print('un fenomeno de una sola liga en vez de midiendo el mercado.\n')
    print(con.sql("""
        WITH sin_inglaterra AS (
          SELECT u2.temporada, u2.club_destino_id, sum(u2.fee_eur) AS gasto
          FROM u2
            JOIN raw_clubes cl ON cl.club_id = u2.club_destino_id
            JOIN raw_competiciones co ON co.competition_id = cl.domestic_competition_id
          WHERE co.country_name <> 'England'
          GROUP BY u2.temporada, u2.club_destino_id
        ),
        r AS (
          SELECT temporada, gasto,
                 ROW_NUMBER() OVER (PARTITION BY temporada ORDER BY gasto DESC) AS puesto
          FROM sin_inglaterra
        )
        SELECT r.temporada,
               m.pct_top10 AS con_inglaterra,
               ROUND(100.0 * sum(CASE WHEN r.puesto <= 10 THEN r.gasto ELSE 0 END)
                     / sum(r.gasto), 1) AS sin_inglaterra
        FROM r JOIN m1_concentracion m USING (temporada)
        GROUP BY r.temporada, m.pct_top10 ORDER BY r.temporada
    """))

    # ---------------------------------------------------------------
    # V4b - La desconcentración, contra la serie larga del censo
    # ---------------------------------------------------------------
    log('V4b - Numero de clubes que pagan y que cobran, censo de FIFA 2018-2025')
    print('Nuestras cuatro temporadas no pueden sostener una frase sobre una decada. Esta serie')
    print('si, y es la unica prueba admisible de que el mercado se ensancha en participantes.\n')
    print(con.sql("""
        SELECT year AS anio, clubs_paying AS clubes_pagan, clubs_receiving AS clubes_cobran,
               ROUND(1.0 * clubs_receiving / clubs_paying, 2) AS cobran_por_cada_pagador
        FROM raw_fifa_mercado
        WHERE clubs_paying IS NOT NULL
        ORDER BY year
    """))
    print(con.sql("""
        SELECT ROUND(100.0 * (max(CASE WHEN year = 2025 THEN clubs_paying END)
                     - max(CASE WHEN year = 2018 THEN clubs_paying END))
                     / max(CASE WHEN year = 2018 THEN clubs_paying END), 1) AS pct_mas_compradores,
               ROUND(100.0 * (max(CASE WHEN year = 2025 THEN clubs_receiving END)
                     - max(CASE WHEN year = 2018 THEN clubs_receiving END))
                     / max(CASE WHEN year = 2018 THEN clubs_receiving END), 1) AS pct_mas_vendedores
        FROM raw_fifa_mercado
    """))

    # ---------------------------------------------------------------
    # V5 - Efecto de tamaño
    # ---------------------------------------------------------------
    log('V5 - Tamano de cada efecto, en puntos y en euros')
    print(con.sql("""
        SELECT 'Concentracion top-10 (22/23 -> 25/26)' AS efecto,
               ROUND(max(CASE WHEN temporada = '25/26' THEN pct_top10 END)
                     - max(CASE WHEN temporada = '22/23' THEN pct_top10 END), 1) AS variacion_puntos
        FROM m1_concentracion
        UNION ALL
        SELECT 'Cuota de gasto 18-23 (22/23 -> 25/26)',
               ROUND(max(CASE WHEN temporada = '25/26' THEN pct_gasto END)
                     - max(CASE WHEN temporada = '22/23' THEN pct_gasto END), 1)
        FROM m3_edad WHERE tramo_fifa = '18-23'
        UNION ALL
        SELECT 'Ratio de precio joven x100 (22/23 -> 25/26)',
               ROUND(100 * (max(CASE WHEN temporada = '25/26' THEN ratio_mediana END)
                     - max(CASE WHEN temporada = '22/23' THEN ratio_mediana END)), 1)
        FROM m4_ratio_precio
    """))

    # ---------------------------------------------------------------
    # V6a - ¿La persistencia del rol es solo azar?
    # ---------------------------------------------------------------
    log('V6a - Persistencia observada contra un modelo nulo (roles repartidos al azar)')
    p = con.sql("""
        SELECT sum(temporadas_vendedor) / (4.0 * count(*)) FROM m2_persistencia
    """).fetchone()[0]
    n = con.sql('SELECT count(*) FROM m2_persistencia').fetchone()[0]
    obs = dict(con.sql("""
        SELECT temporadas_vendedor, clubes FROM m2_persistencia_resumen
    """).fetchall())
    p = float(p)
    print(f'Probabilidad marginal de ser vendedor neto en una temporada: {p:.3f}')
    print(f'Clubes elegibles: {n}\n')
    print(f'{"veces vendedor":>15} {"observado":>10} {"si fuera azar":>14}')
    for k in range(5):
        esperado = comb(4, k) * (p ** k) * ((1 - p) ** (4 - k)) * n
        print(f'{k:>15} {obs.get(k, 0):>10} {esperado:>14.1f}')
    print('\nLos extremos (0 y 4) sobre-representados frente al azar significan que el papel')
    print('de cada club es estable, no que se reparta al tuntun cada verano.')

    # ---------------------------------------------------------------
    # V6b - ¿El ratio de precio joven cayó por culpa de un solo comprador?
    # ---------------------------------------------------------------
    log('V6b - Ratio de precio joven excluyendo al mayor comprador de cada temporada')
    print(con.sql("""
        WITH mayor AS (
          SELECT temporada, club_destino_id,
                 ROW_NUMBER() OVER (PARTITION BY temporada ORDER BY sum(fee_eur) DESC) AS puesto
          FROM u1 GROUP BY temporada, club_destino_id
        ),
        filtrado AS (
          SELECT u1.* FROM u1
            LEFT JOIN mayor m ON m.temporada = u1.temporada
                             AND m.club_destino_id = u1.club_destino_id AND m.puesto = 1
          WHERE m.club_destino_id IS NULL
        ),
        t AS (
          SELECT temporada, tramo_fifa, median(fee_eur) AS med FROM filtrado
          WHERE tramo_fifa IN ('18-23', '24-29') GROUP BY temporada, tramo_fifa
        )
        SELECT t.temporada,
               r.ratio_mediana AS con_todos,
               ROUND(max(CASE WHEN t.tramo_fifa = '18-23' THEN t.med END)
                     / max(CASE WHEN t.tramo_fifa = '24-29' THEN t.med END), 3) AS sin_mayor_comprador
        FROM t JOIN m4_ratio_precio r USING (temporada)
        GROUP BY t.temporada, r.ratio_mediana ORDER BY t.temporada
    """))

    con.close()


if __name__ == '__main__':
    main()
