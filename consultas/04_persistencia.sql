/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: subpregunta B de la fase 1 — ¿cuántos clubes son vendedores netos de forma
             sostenida? Un papel que se repite es una posición estructural; uno que alterna es
             ruido, y solo el primero justifica una decisión de capital. Métrica M2.
   Universo: U2.
   Salida:   m2_flujo_club, m2_persistencia, m2_persistencia_resumen

   El CROSS JOIN es deliberado: hace falta una fila por club y temporada incluso cuando el club
   no operó, porque "no compró ni vendió" y "vendió neto" son cosas distintas y un LEFT JOIN
   normal las confundiría dejando la fila fuera.
*/

CREATE OR REPLACE VIEW m2_flujo_club AS
WITH compras AS (
  SELECT temporada, club_destino_id AS club_id, sum(fee_eur) AS pagado_eur
  FROM u2 GROUP BY temporada, club_destino_id
),

ventas AS (
  SELECT temporada, club_origen_id AS club_id, sum(fee_eur) AS cobrado_eur
  FROM u2 GROUP BY temporada, club_origen_id
),

clubes AS (
  SELECT club_destino_id AS club_id, any_value(club_destino_nombre) AS club FROM u2 GROUP BY 1
  UNION
  SELECT club_origen_id  AS club_id, any_value(club_origen_nombre)  AS club FROM u2 GROUP BY 1
),

temporadas AS (
  SELECT DISTINCT temporada FROM u2
)

SELECT
  te.temporada                                             AS temporada,
  cl.club_id                                               AS club_id,
  any_value(cl.club)                                       AS club,
  COALESCE(cp.pagado_eur, 0)                               AS pagado_eur,
  COALESCE(vt.cobrado_eur, 0)                              AS cobrado_eur,
  COALESCE(cp.pagado_eur, 0) - COALESCE(vt.cobrado_eur, 0) AS neto_eur,
  CASE
    WHEN cp.pagado_eur IS NOT NULL OR vt.cobrado_eur IS NOT NULL THEN 1
    ELSE 0
  END                                                      AS presente
FROM
  temporadas AS te
  CROSS JOIN clubes AS cl
  LEFT JOIN compras AS cp ON cp.club_id = cl.club_id AND cp.temporada = te.temporada
  LEFT JOIN ventas  AS vt ON vt.club_id = cl.club_id AND vt.temporada = te.temporada
GROUP BY
  te.temporada, cl.club_id, cp.pagado_eur, vt.cobrado_eur;

/* Elegibles: presentes en LAS CUATRO temporadas. Un club ausente en una de ellas puntuaría
   neto = 0 ahí y se leería como "no vendedor", que no es lo mismo que "no vendió". */

CREATE OR REPLACE VIEW m2_persistencia AS
WITH elegibles AS (
  SELECT club_id
  FROM m2_flujo_club
  GROUP BY club_id
  HAVING sum(presente) = 4
)
SELECT
  fc.club_id                                              AS club_id,
  any_value(fc.club)                                      AS club,
  sum(CASE WHEN fc.neto_eur < 0 THEN 1 ELSE 0 END)        AS temporadas_vendedor,
  sum(fc.cobrado_eur) - sum(fc.pagado_eur)                AS saldo_4_temporadas_eur
FROM
  m2_flujo_club AS fc
  JOIN elegibles AS el ON el.club_id = fc.club_id
GROUP BY
  fc.club_id;

CREATE OR REPLACE VIEW m2_persistencia_resumen AS
SELECT
  temporadas_vendedor,
  count(*)                                                          AS clubes,
  ROUND(100.0 * count(*) / sum(count(*)) OVER (), 1)                AS pct_clubes
FROM
  m2_persistencia
GROUP BY
  temporadas_vendedor
ORDER BY
  temporadas_vendedor;
