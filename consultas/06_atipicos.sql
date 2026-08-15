/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: los fichajes muy caros de jugadores muy jóvenes. No son ruido a filtrar: son el
             fenómeno que originó el caso, así que se miden. ¿Cuánto del gasto en 18-23 se
             concentra en unas pocas operaciones, y quién las paga?
   Universo: U1 para el peso; el detalle nominal solo donde ambos clubes se conocen.
   Salida:   m6_dos_velocidades, m6_grandes_compradores_jovenes, m6_top_operaciones_jovenes

   El umbral de 40 M€ es una convención declarada, no un resultado: está muy por encima del
   percentil 95 del mercado (22 M€) y separa con holgura la élite de la cola larga.
*/

CREATE OR REPLACE VIEW m6_dos_velocidades AS
SELECT
  temporada,
  count(*)                                                                  AS operaciones,
  sum(CASE WHEN fee_eur >= 40e6 THEN 1 ELSE 0 END)                          AS ops_40m_o_mas,
  ROUND(100.0 * sum(CASE WHEN fee_eur >= 40e6 THEN fee_eur ELSE 0 END)
        / sum(fee_eur), 1)                                                  AS pct_gasto_40m_o_mas,
  ROUND(100.0 * sum(CASE WHEN fee_eur < 5e6 THEN 1 ELSE 0 END)
        / count(*), 1)                                                      AS pct_ops_bajo_5m,
  ROUND(100.0 * sum(CASE WHEN fee_eur < 5e6 THEN fee_eur ELSE 0 END)
        / sum(fee_eur), 1)                                                  AS pct_gasto_bajo_5m
FROM
  u1
WHERE
  tramo_fifa = '18-23'
GROUP BY
  temporada
ORDER BY
  temporada;

CREATE OR REPLACE VIEW m6_grandes_compradores_jovenes AS
SELECT
  club_destino_nombre     AS comprador,
  count(*)                AS operaciones,
  sum(fee_eur)            AS gasto_eur
FROM
  u1
WHERE
  tramo_fifa = '18-23'
  AND fee_eur >= 40e6
GROUP BY
  club_destino_nombre
ORDER BY
  gasto_eur DESC, comprador;   -- el desempate hace el orden reproducible

CREATE OR REPLACE VIEW m6_top_operaciones_jovenes AS
SELECT
  jugador,
  edad,
  temporada,
  club_origen_nombre      AS vendedor,
  club_destino_nombre     AS comprador,
  fee_eur
FROM
  u1
WHERE
  edad <= 21
ORDER BY
  fee_eur DESC, jugador
LIMIT 20;
