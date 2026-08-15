"""Fase 3 — construye la base del caso desde los crudos congelados.

Ejecuta consultas/01_construir_base.sql y consultas/02_limpiar.sql sobre DuckDB, imprime la
reconciliación de conteos de cada transformación y comprueba que el resultado sigue siendo el
mismo que cerró la fase 2. Si esa comprobación falla, algo se rompió: el pipeline no se da por
bueno porque termine sin error.

Este script no transforma nada por su cuenta. Toda la lógica está en los .sql, que es donde se
puede leer y auditar; aquí solo se resuelven rutas y se cuentan filas.

Uso:  python notebooks/procesar.py
"""

import duckdb
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CRUDOS = BASE / 'datos' / 'crudos'
LIMPIOS = BASE / 'datos' / 'limpios'
CONSULTAS = BASE / 'consultas'

FECHA_SNAPSHOT = '2026-08-14'
TEMPORADAS = ('22/23', '23/24', '24/25', '25/26')

RUTAS = {
    'ruta_traspasos': f'transfermarkt_traspasos_1993-2030_{FECHA_SNAPSHOT}.csv.gz',
    'ruta_jugadores': f'transfermarkt_jugadores_snapshot_{FECHA_SNAPSHOT}.csv.gz',
    'ruta_clubes': f'transfermarkt_clubes_snapshot_{FECHA_SNAPSHOT}.csv.gz',
    'ruta_competiciones': f'transfermarkt_competiciones_snapshot_{FECHA_SNAPSHOT}.csv.gz',
    'ruta_fifa_edad': 'fifa_edad_2018-2025_2026-08-14.csv',
    'ruta_fifa_mercado': 'fifa_mercado_2016-2025_2026-08-14.csv',
}

# Lo que cerró la fase 2, en euros enteros y no en millones redondeados: anclar la comprobación
# al redondeo la hacía fallar por 1 M€ sobre 37.436, que es ruido de coma flotante y no un error
# de filtrado. Las filas sí se comparan exactas — ahí sí, cualquier diferencia es un fallo real.
ESPERADO = {
    'u1_filas': 6716, 'u1_gasto_eur': 37436176000,
    'u2_filas': 5109, 'u2_gasto_eur': 35413528000,
}


def registrar(titulo, **kv):
    print(f'--- {titulo} ---')
    for k, v in kv.items():
        print(f'{k}: {v:,}' if isinstance(v, int) else f'{k}: {v}')
    print()


def main():
    LIMPIOS.mkdir(parents=True, exist_ok=True)
    destino = LIMPIOS / 'football-transfer-market.duckdb'
    destino.unlink(missing_ok=True)   # desde cero: un pipeline que reusa estado no es reproducible

    con = duckdb.connect(str(destino))
    for nombre, archivo in RUTAS.items():
        con.execute(f"SET VARIABLE {nombre} = '{(CRUDOS / archivo).as_posix()}'")
    con.execute(f"SET VARIABLE fecha_snapshot = '{FECHA_SNAPSHOT}'")

    def uno(sql):
        return con.sql(sql).fetchone()[0]

    def gasto_eur(vista):
        # fee_eur es DECIMAL en DuckDB y llega como decimal.Decimal: se convierte a int, no a
        # float, para que la comparación no dependa del redondeo.
        return int(uno(f'SELECT sum(fee_eur) FROM {vista}'))

    def gasto_meur(vista):
        return round(gasto_eur(vista) / 1e6)

    # =========================================================
    # T1 — Carga fiel del crudo
    # =========================================================
    con.execute((CONSULTAS / '01_construir_base.sql').read_text(encoding='utf-8'))
    registrar('T1 - Carga del crudo, sin transformar',
              traspasos=uno('SELECT count(*) FROM raw_traspasos'),
              jugadores=uno('SELECT count(*) FROM raw_jugadores'),
              clubes=uno('SELECT count(*) FROM raw_clubes'),
              competiciones=uno('SELECT count(*) FROM raw_competiciones'),
              fifa_edad=uno('SELECT count(*) FROM raw_fifa_edad'),
              fifa_mercado=uno('SELECT count(*) FROM raw_fifa_mercado'))

    # El anexo de SQL pide conteo antes/después de cada JOIN. El de clubes contra competiciones
    # no aparece en la reconciliación de filas porque es una tabla de apoyo, pero si un club
    # resolviera a dos competiciones duplicaría traspasos e inflaría todas las sumas en silencio.
    clubes_antes = uno('SELECT count(*) FROM raw_clubes')
    clubes_despues = uno("""SELECT count(*) FROM raw_clubes AS cl
                            LEFT JOIN raw_competiciones AS co
                              ON co.competition_id = cl.domestic_competition_id""")
    registrar('JOIN clubes x competiciones',
              antes=clubes_antes, despues=clubes_despues,
              duplica='no' if clubes_antes == clubes_despues else 'SI - revisar antes de seguir')
    if clubes_antes != clubes_despues:
        raise SystemExit('El JOIN de clubes duplica filas: las sumas por club serian falsas.')

    # =========================================================
    # T2-T7 — Reconciliación: iniciales menos excluidas igual a finales
    # =========================================================
    lista = ', '.join(f"'{t}'" for t in TEMPORADAS)
    n0 = uno('SELECT count(*) FROM raw_traspasos')
    n1 = uno(f'SELECT count(*) FROM raw_traspasos WHERE transfer_season IN ({lista})')
    n2 = uno(f"""SELECT count(*) FROM raw_traspasos WHERE transfer_season IN ({lista})
                 AND transfer_date <= DATE '{FECHA_SNAPSHOT}'""")
    n3 = uno(f"""SELECT count(*) FROM raw_traspasos WHERE transfer_season IN ({lista})
                 AND transfer_date <= DATE '{FECHA_SNAPSHOT}' AND transfer_fee > 0""")

    con.execute((CONSULTAS / '02_limpiar.sql').read_text(encoding='utf-8'))

    n4 = uno('SELECT count(*) FROM traspasos_ventana')
    n5 = uno('SELECT count(*) FROM u1')
    n6 = uno('SELECT count(*) FROM u2')

    registrar('T2 - Ventana temporal 22/23-25/26',
              antes=n0, excluidas=n0 - n1, despues=n1,
              motivo='sesgo de supervivencia cuantificado en CASO.md, seccion 0')
    registrar('T3 - Traspasos con fecha posterior al snapshot',
              antes=n1, excluidas=n1 - n2, despues=n2,
              motivo='movimientos ya pactados, el crudo llega hasta 2030-06-30')
    registrar('T4 - Poblacion de analisis: solo operaciones con precio',
              antes=n2, excluidas=n2 - n3, despues=n3,
              motivo='cesiones, libres y fees desconocidos colapsan todos a 0 o NULL aguas arriba')
    registrar('T5 - Jugadores sin fecha de nacimiento',
              antes=n3, excluidas=n3 - n4, despues=n4,
              motivo='sin edad no hay tramo, y el tramo es media pregunta del caso')
    registrar('T6 - Universo U1: al menos un club europeo identificado',
              antes=n4, excluidas=n4 - n5, despues=n5,
              gasto_meur=gasto_meur('u1'))
    registrar('T7 - Universo U2: ambos clubes identificados',
              antes=n5, excluidas=n5 - n6, despues=n6,
              gasto_meur=gasto_meur('u2'))

    # =========================================================
    # Verificación
    # =========================================================
    obtenido = {
        'u1_filas': n5,
        'u1_gasto_eur': gasto_eur('u1'),
        'u2_filas': n6,
        'u2_gasto_eur': gasto_eur('u2'),
    }
    fallos = {k: (v, obtenido[k]) for k, v in ESPERADO.items() if obtenido[k] != v}

    registrar('Reconciliacion de conteos',
              cuadra=(n0 - (n0 - n1) - (n1 - n2) - (n2 - n3) - (n3 - n4) == n4))
    registrar('Regresion contra el cierre de la fase 2',
              esperado=ESPERADO, obtenido=obtenido,
              resultado='OK' if not fallos else f'DISCREPANCIA en {fallos}')

    con.close()
    if fallos:
        raise SystemExit('El pipeline no reproduce los numeros de la fase 2. Revisar antes de seguir.')
    print(f'Base construida en {destino.relative_to(BASE)}')


if __name__ == '__main__':
    main()
