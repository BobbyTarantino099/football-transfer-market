"""Fase 4 — ejecuta las consultas de análisis y exporta los agregados.

Crea las vistas definidas en consultas/03 a 06 sobre la base construida por procesar.py y
exporta a salidas/tablas/ solo lo que la fase 5 y el sitio necesitan. Únicamente cruzan
agregados: el detalle operación a operación se queda aquí.

Uso:  python notebooks/analizar.py   (requiere haber corrido procesar.py antes)
"""

import duckdb
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CONSULTAS = BASE / 'consultas'
TABLAS = BASE / 'salidas' / 'tablas'
BD = BASE / 'datos' / 'limpios' / 'football-transfer-market.duckdb'

# vista -> archivo exportado. Lo que no esté aquí no cruza al sitio.
EXPORTAR = {
    'm1_concentracion': 'concentracion_por_temporada.csv',
    'm1_por_pais': 'gasto_por_pais_comprador.csv',
    'm2_persistencia_resumen': 'persistencia_rol_vendedor.csv',
    'm3_edad': 'gasto_por_tramo_edad.csv',
    'm3_edad_fino': 'gasto_por_tramo_fino.csv',
    'm4_ratio_precio': 'ratio_precio_joven.csv',
    'm6_dos_velocidades': 'dos_velocidades_tramo_joven.csv',
    'm6_grandes_compradores_jovenes': 'compradores_jovenes_40m.csv',
    'm6_top_operaciones_jovenes': 'top_operaciones_jovenes.csv',
}


def main():
    if not BD.exists():
        raise SystemExit('Falta la base. Ejecuta antes: python notebooks/procesar.py')

    TABLAS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(BD))

    for archivo in sorted(CONSULTAS.glob('0[3-6]_*.sql')):
        con.execute(archivo.read_text(encoding='utf-8'))
        print(f'ejecutada  {archivo.name}')
    print()

    for vista, nombre in EXPORTAR.items():
        destino = TABLAS / nombre
        con.execute(f"COPY (SELECT * FROM {vista}) TO '{destino.as_posix()}' (HEADER, DELIMITER ',')")
        filas = con.sql(f'SELECT count(*) FROM {vista}').fetchone()[0]
        print(f'{nombre:<40} {filas:>5} filas  {destino.stat().st_size / 1024:>6.1f} KB')

    total_kb = sum(f.stat().st_size for f in TABLAS.glob('*.csv')) / 1024
    print(f'\nTotal exportado: {total_kb:.1f} KB')
    if total_kb > 1024:
        # Regla de arquitectura: si un agregado pesa megas, la agregación está incompleta.
        print('AVISO: mas de 1 MB. Volver a la fase 4 y resumir mas, en vez de subirselo al sitio.')

    con.close()


if __name__ == '__main__':
    main()
