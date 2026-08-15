/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: subpregunta A de la fase 1 — ¿qué cuota del gasto de cada temporada se lleva el
             puñado de clubes que más compra, y se mueve esa cuota entre las cuatro ventanas?
             Métricas M1 (concentración) y M5 (tamaño del mercado).
   Universo: U2. Atribuir gasto a un club exige saber quiénes son las dos partes.
   Salida:   m1_concentracion, m1_por_pais
*/

CREATE OR REPLACE VIEW m1_gasto_por_comprador AS
SELECT
  temporada,
  club_destino_id                 AS club_id,
  any_value(club_destino_nombre)  AS club,
  sum(fee_eur)                    AS gasto_eur,
  count(*)                        AS operaciones
FROM
  u2
GROUP BY
  temporada, club_destino_id;

CREATE OR REPLACE VIEW m1_concentracion AS
WITH ranking AS (
  SELECT
    temporada,
    club,
    gasto_eur,
    ROW_NUMBER() OVER (PARTITION BY temporada ORDER BY gasto_eur DESC) AS puesto
  FROM
    m1_gasto_por_comprador
)
SELECT
  temporada,
  ROUND(sum(gasto_eur) / 1e6)                                                   AS mercado_meur,
  ROUND(100.0 * sum(CASE WHEN puesto <= 10 THEN gasto_eur ELSE 0 END)
        / sum(gasto_eur), 1)                                                    AS pct_top10,
  ROUND(100.0 * sum(CASE WHEN puesto <= 20 THEN gasto_eur ELSE 0 END)
        / sum(gasto_eur), 1)                                                    AS pct_top20,
  count(*)                                                                      AS clubes_compradores
FROM
  ranking
GROUP BY
  temporada
ORDER BY
  temporada;

/* Eje secundario: el país del club comprador. Sirve para descartar la lectura alternativa más
   obvia — que lo que llamamos estructura del mercado europeo sea en realidad un fenómeno de una
   sola liga. El JOIN es INNER porque en U2 ambos clubes están identificados por construcción. */

CREATE OR REPLACE VIEW m1_por_pais AS
SELECT
  co.country_name        AS pais_comprador,
  u2.temporada           AS temporada,
  sum(u2.fee_eur)        AS gasto_eur,
  count(*)               AS operaciones
FROM
  u2
  JOIN raw_clubes AS cl
    ON cl.club_id = u2.club_destino_id
  JOIN raw_competiciones AS co
    ON co.competition_id = cl.domestic_competition_id
GROUP BY
  co.country_name, u2.temporada;
