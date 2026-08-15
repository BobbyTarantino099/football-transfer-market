/* Fecha:    2026-08-15
   Analista: Juanes
   Objetivo: cargar en la base del caso el snapshot congelado de Transfermarkt y las cifras
             transcritas de los informes de FIFA. Aquí no se transforma nada: la carga debe ser
             fiel al crudo para que 02_limpiar.sql sea auditable contra él.
   Entrada:  datos/crudos/ — las rutas llegan como variables de sesión, inyectadas por
             notebooks/procesar.py, de modo que este archivo no contiene ninguna ruta.
   Salida:   tablas raw_*
*/

-- SELECT * es deliberado aquí y solo aquí: una carga que elige columnas ya es una
-- transformación, y entonces no se podría contrastar lo limpio contra lo crudo.

CREATE OR REPLACE TABLE raw_traspasos AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_traspasos'));

CREATE OR REPLACE TABLE raw_jugadores AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_jugadores'));

CREATE OR REPLACE TABLE raw_clubes AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_clubes'));

CREATE OR REPLACE TABLE raw_competiciones AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_competiciones'));

-- Fuente A. Agregados de FIFA: no se cruzan con lo anterior a nivel de registro, viven en la
-- misma base solo para que una sola consulta pueda comparar ambos lados.

CREATE OR REPLACE TABLE raw_fifa_edad AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_fifa_edad'));

CREATE OR REPLACE TABLE raw_fifa_mercado AS
SELECT
  *
FROM
  read_csv_auto(getvariable('ruta_fifa_mercado'));
