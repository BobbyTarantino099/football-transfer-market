"""Descarga el snapshot de Transfermarkt a datos/crudos/ y registra su huella.

La fuente se refresca cada semana, así que el snapshot se versiona en el repo: sin
congelarlo, los números del caso dejan de reproducirse en cuanto pasa un mes. Este
script existe para poder rehacer el snapshot de forma trazable, no para ejecutarse
en cada reproducción — quien clone el repo ya tiene los archivos.

Si vuelves a ejecutarlo, los datos serán más recientes que los del análisis y las
cifras cambiarán. Eso es esperado: compara los hashes contra los de la ficha de
fuente antes de dar por buena cualquier diferencia.

Uso:  python notebooks/descargar.py
"""

import hashlib
import shutil
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CRUDOS = BASE / 'datos' / 'crudos'

URL = 'https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/{tabla}.csv.gz'
FECHA = '2026-08-14'

# tabla remota -> nombre local, siguiendo origen_tema_periodo_fecha
TABLAS = {
    'transfers': f'transfermarkt_traspasos_1993-2030_{FECHA}.csv.gz',
    'players': f'transfermarkt_jugadores_snapshot_{FECHA}.csv.gz',
    'clubs': f'transfermarkt_clubes_snapshot_{FECHA}.csv.gz',
    'competitions': f'transfermarkt_competiciones_snapshot_{FECHA}.csv.gz',
}


def descargar(url, destino):
    # El almacenamiento rechaza con 403 el User-Agent por defecto de urllib.
    peticion = urllib.request.Request(url, headers={'User-Agent': 'curl/8'})
    with urllib.request.urlopen(peticion) as respuesta, open(destino, 'wb') as f:
        shutil.copyfileobj(respuesta, f)


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 20), b''):
            h.update(bloque)
    return h.hexdigest()


def main():
    CRUDOS.mkdir(parents=True, exist_ok=True)
    for tabla, nombre in TABLAS.items():
        destino = CRUDOS / nombre
        descargar(URL.format(tabla=tabla), destino)
        print(f'{nombre}\n  {destino.stat().st_size:,} bytes\n  sha256 {sha256(destino)}')


if __name__ == '__main__':
    main()
