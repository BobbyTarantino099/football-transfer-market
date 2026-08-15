/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: subpregunta C de la fase 1 — qué cuota del gasto de cada temporada va a cada tramo
             de edad, y cuánto cuesta un joven frente a un jugador en su pico. Métricas M3 y M4.
   Universo: U1. Conserva las compras baratas de talento joven a clubes de fuera de las
             competiciones cubiertas, que es donde vive medio fenómeno.
   Salida:   m3_edad, m3_edad_fino, m4_ratio_precio

   Toda cuota se calcula sobre el total DE SU PROPIA TEMPORADA. Es lo que impide que el
   crecimiento nominal del mercado se cuele como si fuera un hallazgo.
*/

CREATE OR REPLACE VIEW m3_edad AS
SELECT
  temporada,
  tramo_fifa,
  count(*)                                                                 AS operaciones,
  sum(fee_eur)                                                             AS gasto_eur,
  ROUND(100.0 * sum(fee_eur)
        / sum(sum(fee_eur)) OVER (PARTITION BY temporada), 1)              AS pct_gasto,
  ROUND(median(fee_eur) / 1e6, 2)                                          AS mediana_meur,
  ROUND(avg(fee_eur) / 1e6, 2)                                             AS media_meur
FROM
  u1
GROUP BY
  temporada, tramo_fifa
ORDER BY
  temporada, tramo_fifa;

/* El corte fino: 18-23 mete en el mismo saco a un chico de 18 y a un jugador ya formado de 23,
   y esa distinción es justamente la que motivó el caso. */

CREATE OR REPLACE VIEW m3_edad_fino AS
SELECT
  temporada,
  tramo_fino,
  count(*)                                                                 AS operaciones,
  ROUND(100.0 * sum(fee_eur)
        / sum(sum(fee_eur)) OVER (PARTITION BY temporada), 1)              AS pct_gasto,
  ROUND(median(fee_eur) / 1e6, 2)                                          AS mediana_meur
FROM
  u1
GROUP BY
  temporada, tramo_fino
ORDER BY
  temporada, tramo_fino;

/* M4. La mediana es la cifra del hallazgo: la distribución es muy asimétrica y una media
   seguiría a media docena de operaciones. La media se calcula igualmente, y solo para poder
   contrastar contra el censo de FIFA, que publica medias y no medianas. */

CREATE OR REPLACE VIEW m4_ratio_precio AS
WITH por_tramo AS (
  SELECT
    temporada,
    tramo_fifa,
    median(fee_eur) AS mediana_eur,
    avg(fee_eur)    AS media_eur
  FROM
    u1
  WHERE
    tramo_fifa IN ('18-23', '24-29')
  GROUP BY
    temporada, tramo_fifa
)
SELECT
  temporada,
  ROUND(max(CASE WHEN tramo_fifa = '18-23' THEN mediana_eur ELSE NULL END)
        / max(CASE WHEN tramo_fifa = '24-29' THEN mediana_eur ELSE NULL END), 3) AS ratio_mediana,
  ROUND(max(CASE WHEN tramo_fifa = '18-23' THEN media_eur ELSE NULL END)
        / max(CASE WHEN tramo_fifa = '24-29' THEN media_eur ELSE NULL END), 3)   AS ratio_media
FROM
  por_tramo
GROUP BY
  temporada
ORDER BY
  temporada;
