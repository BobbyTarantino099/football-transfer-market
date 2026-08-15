/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: llevar el crudo a la población de análisis de la fase 1 — traspasos con precio,
             del mercado europeo, en las cuatro temporadas donde la cobertura es estable — y
             etiquetar cada fila con su tramo de edad y su universo.
   Entrada:  raw_traspasos, raw_jugadores, raw_clubes, raw_competiciones
   Salida:   traspasos_ventana (una fila = un traspaso con precio), más las vistas u1 y u2.

   Decisiones que esta consulta materializa, todas razonadas en bitacora-limpieza.md:
     · ventana 22/23-25/26     -> sesgo de supervivencia cuantificado en CASO.md §0
     · fee > 0                 -> aguas arriba, cesiones/libres/desconocidos colapsan a 0 o NULL
     · fecha <= snapshot       -> el crudo llega a 2030 con movimientos ya pactados
     · club europeo            -> por confederation = 'europa', no por nacionalidad del jugador

   DuckDB compara cadenas de forma SENSIBLE a mayúsculas ('europa' = 'EUROPA' es falso), así que
   'europa' se escribe tal y como viene en la fuente. Verificado el 2026-08-15.
*/

CREATE OR REPLACE TABLE traspasos_ventana AS

WITH club_confederacion AS (
  -- Un club es europeo por la competición doméstica en la que juega. LEFT JOIN a propósito:
  -- los clubes fuera de las 65 competiciones cubiertas deben sobrevivir con confederación
  -- desconocida, no desaparecer. Son el 29,5 % de las operaciones y el 6,3 % del dinero.
  SELECT
    cl.club_id                              AS club_id,
    cl.name                                 AS club_nombre,
    co.confederation                        AS confederacion
  FROM
    raw_clubes AS cl
    LEFT JOIN raw_competiciones AS co
      ON co.competition_id = cl.domestic_competition_id
),

traspasos_con_precio AS (
  -- Población de análisis. Los tres filtros van juntos porque los tres responden a la
  -- misma pregunta: qué filas contienen un precio real de un mercado que sabemos leer.
  SELECT
    tr.player_id                            AS player_id,
    tr.player_name                          AS jugador,
    tr.transfer_date                        AS fecha,
    tr.transfer_season                      AS temporada,
    tr.from_club_id                         AS club_origen_id,
    tr.to_club_id                           AS club_destino_id,
    tr.from_club_name                       AS club_origen_nombre,
    tr.to_club_name                         AS club_destino_nombre,
    CAST(tr.transfer_fee AS DECIMAL(18, 2)) AS fee_eur
  FROM
    raw_traspasos AS tr
  WHERE
    tr.transfer_fee > 0
    AND tr.transfer_date <= CAST(getvariable('fecha_snapshot') AS DATE)
    AND tr.transfer_season IN ('22/23', '23/24', '24/25', '25/26')
),

con_edad AS (
  -- LEFT JOIN, no INNER: si a un jugador le faltara la fecha de nacimiento queremos verlo
  -- como NULL y contarlo, no perderlo en silencio. La exclusión se hace explícita más abajo.
  SELECT
    tp.*,
    DATE_DIFF('year', ju.date_of_birth, tp.fecha) AS edad,
    ju.position                                   AS posicion
  FROM
    traspasos_con_precio AS tp
    LEFT JOIN raw_jugadores AS ju
      ON ju.player_id = tp.player_id
),

etiquetado AS (
  SELECT
    ce.player_id,
    ce.jugador,
    ce.fecha,
    ce.temporada,
    ce.club_origen_id,
    ce.club_destino_id,
    ce.club_origen_nombre,
    ce.club_destino_nombre,
    ce.fee_eur,
    ce.edad,
    ce.posicion,

    -- Tramos de FIFA: son los que permiten contrastar contra el censo oficial.
    CASE
      WHEN ce.edad < 18                  THEN '<18'
      WHEN ce.edad BETWEEN 18 AND 23     THEN '18-23'
      WHEN ce.edad BETWEEN 24 AND 29     THEN '24-29'
      WHEN ce.edad >= 30                 THEN '>=30'
      ELSE 'desconocido'
    END                                             AS tramo_fifa,

    -- Corte fino dentro del bloque joven: 18-23 mezcla a un chico de 18 con un jugador ya
    -- formado de 23, y esa distinción es media pregunta del caso.
    CASE
      WHEN ce.edad < 18                  THEN '<18'
      WHEN ce.edad BETWEEN 18 AND 20     THEN '18-20'
      WHEN ce.edad BETWEEN 21 AND 23     THEN '21-23'
      WHEN ce.edad >= 24                 THEN '24+'
      ELSE 'desconocido'
    END                                             AS tramo_fino,

    CASE WHEN cf_o.club_id IS NOT NULL THEN TRUE ELSE FALSE END AS origen_identificado,
    CASE WHEN cf_d.club_id IS NOT NULL THEN TRUE ELSE FALSE END AS destino_identificado,
    CASE WHEN cf_o.confederacion = 'europa' THEN TRUE ELSE FALSE END AS origen_europeo,
    CASE WHEN cf_d.confederacion = 'europa' THEN TRUE ELSE FALSE END AS destino_europeo
  FROM
    con_edad AS ce
    LEFT JOIN club_confederacion AS cf_o ON cf_o.club_id = ce.club_origen_id
    LEFT JOIN club_confederacion AS cf_d ON cf_d.club_id = ce.club_destino_id
)

SELECT
  et.*,
  -- U1: basta con que un extremo sea europeo e identificable. Es el universo de las métricas
  -- de precio y edad, porque conserva las compras baratas de talento joven a clubes de fuera.
  CASE
    WHEN et.origen_europeo OR et.destino_europeo THEN TRUE
    ELSE FALSE
  END                                               AS es_u1,
  -- U2: hacen falta los dos extremos, porque atribuir gasto a un club exige saber quién es
  -- cada parte. Es el universo de la concentración y de la persistencia del rol.
  CASE
    WHEN (et.origen_europeo OR et.destino_europeo)
         AND et.origen_identificado
         AND et.destino_identificado THEN TRUE
    ELSE FALSE
  END                                               AS es_u2
FROM
  etiquetado AS et
WHERE
  et.edad IS NOT NULL;   -- exclusión explícita: sin edad no hay tramo, y el tramo es la pregunta

CREATE OR REPLACE VIEW u1 AS
SELECT * FROM traspasos_ventana WHERE es_u1;

CREATE OR REPLACE VIEW u2 AS
SELECT * FROM traspasos_ventana WHERE es_u2;
