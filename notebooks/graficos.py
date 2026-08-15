"""Fase 5 — las figuras del caso.

Cinco figuras, una por hallazgo, con el titular que enuncia el hallazgo y no el tema.

Dos decisiones deliberadas de este caso:

  · **Tema propio.** Verde y violeta, frente al azul y naranja del caso 1. La paleta está
    validada con el verificador de la skill `dataviz` (banda de luminosidad, suelo de croma,
    separación para daltonismo ΔE 18.5 deutan / 12.8 tritan, contraste) y la rampa por
    monotonicidad de luminancia. La composición no se toca: es lo que hace que los casos se
    reconozcan como un mismo cuerpo de trabajo.

  · **Ninguna forma repetida**, ni entre figuras ni con el caso 1, que ya usa dumbbell,
    tabla-matriz, lollipop y barras agrupadas. Adaptar la forma al dato es parte del oficio
    que el portafolio tiene que demostrar.

Uso:  python notebooks/graficos.py   (requiere procesar.py y analizar.py antes)
"""

import sys
from math import comb
from pathlib import Path

import duckdb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilo  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
BD = BASE / 'datos' / 'limpios' / 'football-transfer-market.duckdb'
GRAFICOS = BASE / 'salidas' / 'graficos'

FUENTE_B = 'Transfermarkt via dcaribou/transfermarkt-datasets (CC0), snapshot 2026-08-14'
FUENTE_A = 'FIFA Global Transfer Report (FIFA TMS), editions 2018-2025'

estilo.aplicar(
    acento='#0f7d3f',
    contra='#7b4bb0',
    rampa=['#e9f4ec', '#c3e3cd', '#86c79b', '#3f9e63', '#0f7d3f'],
)
con = duckdb.connect(str(BD), read_only=True)


def filas(sql):
    return con.sql(sql).fetchall()


# ===========================================================================
# 1 - La contradicción, en curva de concentración
# ===========================================================================
# Ordenados de mayor a menor comprador: cuanto más deprisa sube la curva, en menos
# manos está el dinero. La diagonal es el reparto perfectamente igualitario, y sirve
# de referencia sin necesidad de explicarla.
curva = filas("""
    WITH gasto AS (
      SELECT temporada, club_destino_id, sum(fee_eur) AS gasto
      FROM u2 GROUP BY temporada, club_destino_id
    )
    SELECT temporada,
           100.0 * ROW_NUMBER() OVER (PARTITION BY temporada ORDER BY gasto DESC)
                 / count(*) OVER (PARTITION BY temporada)                        AS pct_clubes,
           100.0 * sum(gasto) OVER (PARTITION BY temporada ORDER BY gasto DESC
                                    ROWS UNBOUNDED PRECEDING)
                 / sum(gasto) OVER (PARTITION BY temporada)                      AS pct_gasto
    FROM gasto ORDER BY temporada, pct_clubes
""")
series = {}
for temporada, x, y in curva:
    series.setdefault(temporada, ([0.0], [0.0]))
    series[temporada][0].append(float(x))
    series[temporada][1].append(float(y))

fig, ax = estilo.figura(
    titular='The money spread out instead of concentrating, the opposite of what was expected',
    subtitulo='Cumulative share of European transfer spending, clubs ordered from biggest buyer '
              'down. X axis trimmed to the first 40% of buyers, where the difference lives',
    periodo='2022/23 vs 2025/26  ·  5,109 priced deals  ·  both clubs identified',
    fuente=FUENTE_B,
    nota='The straight line is a perfectly even split. The further a curve bulges above it, the '
         'fewer clubs hold the money. The hypothesis, written before the analysis, expected the '
         'bulge to grow.',
    abajo=0.21,
)
ax.plot([0, 100], [0, 100], color=estilo.REGLA, linewidth=1.4, zorder=1)
for temporada, color, ancho in (('22/23', estilo.CONTRA, 2.6), ('25/26', estilo.ACENTO, 3.0)):
    x, y = series[temporada]
    ax.plot(x, y, color=color, linewidth=ancho, zorder=3, label=temporada)
# Cada temporada tiene distinto número de clubes (340 y 383), así que las curvas no
# comparten malla en X: para sombrear el hueco entre ambas hay que llevarlas antes a
# una común. El área es la desconcentración.
malla = np.linspace(0, 100, 400)
y_antes = np.interp(malla, series['22/23'][0], series['22/23'][1])
y_ahora = np.interp(malla, series['25/26'][0], series['25/26'][1])
ax.fill_between(malla, y_ahora, y_antes, color=estilo.CONTRA, alpha=0.10, zorder=2)
# Eje X recortado al primer 40 % de compradores, y dicho en el subtítulo. Con la escala
# completa las dos curvas se superponen: la diferencia real vive en la cabecera del
# reparto, y a 0-100 el dibujo decía "iguales" mientras los datos decían "cayó".
ax.axvline(10, color=estilo.REGLA, linewidth=1.1, zorder=1)
ax.text(10.6, 4, 'TOP 10% OF BUYERS', va='center', ha='left', color=estilo.TINTA_TENUE,
        **estilo._prop('medio', 8))
# Las dos curvas casi se tocan aquí, así que las cifras se separan en vertical: pegadas
# a su punto se solapaban entre sí y sobre la curva contraria.
for temporada, color, dx, dy, lado in (('22/23', estilo.CONTRA, -1.0, 8.5, 'right'),
                                       ('25/26', estilo.ACENTO, 1.4, -7.0, 'left')):
    x, y = series[temporada]
    i = min(range(len(x)), key=lambda k: abs(x[k] - 10))
    ax.scatter([x[i]], [y[i]], s=70, color=color, zorder=4,
               edgecolor=estilo.PAPEL, linewidth=1.7)
    ax.text(x[i] + dx, y[i] + dy, f'{y[i]:.0f}%', va='center', ha=lado,
            color=color, **estilo._prop('negrita', 13))
ax.set_xlabel('Share of buying clubs (%), largest first')
ax.set_ylabel('Cumulative share of spending (%)')
ax.set_xlim(0, 40)
ax.set_ylim(0, 100)
ax.grid(axis='both')
ax.set_axisbelow(True)
# Leyenda con ancla fija: `leyenda()` estira el eje para abrirse hueco, y en un eje de
# porcentaje acumulado eso lo llevaba hasta 120 %, que no existe.
leg = ax.legend(loc='lower right', frameon=True, fancybox=False, framealpha=1.0,
                facecolor=estilo.PAPEL, edgecolor=estilo.REGLA, borderpad=0.7)
leg.get_frame().set_linewidth(0.9)
for t in leg.get_texts():
    t.set_color(estilo.TINTA_SUAVE)
    t.set_fontsize(9)
estilo.guardar(fig, GRAFICOS / '01_concentracion_cae.png')

# ===========================================================================
# 2 - La evidencia de década: solo el censo puede hablar de tendencia
# ===========================================================================
censo = filas("""
    SELECT year, clubs_paying, clubs_receiving FROM raw_fifa_mercado
    WHERE clubs_paying IS NOT NULL ORDER BY year
""")
anios = [r[0] for r in censo]
pagan = [r[1] for r in censo]
cobran = [r[2] for r in censo]

fig, ax = estilo.figura(
    titular='45% more clubs pay transfer fees than eight years ago',
    subtitulo='Number of clubs worldwide paying and receiving at least one transfer fee per year',
    periodo='2018-2025  ·  FIFA TMS census of every international transfer',
    fuente=FUENTE_A,
    nota='Our four seasons cannot carry a claim about a decade. This series can: it is a census, '
         'not a sample, and carries no survivorship bias.',
)
ax.plot(anios, cobran, color=estilo.CONTEXTO, linewidth=2.4, marker='o', markersize=5,
        markeredgecolor=estilo.PAPEL, markeredgewidth=1.4, label='Clubs receiving a fee')
ax.plot(anios, pagan, color=estilo.ACENTO, linewidth=3.0, marker='o', markersize=6,
        markeredgecolor=estilo.PAPEL, markeredgewidth=1.6, label='Clubs paying a fee')
ax.text(anios[-1] + 0.08, pagan[-1], f'{pagan[-1]:,}', va='center', ha='left',
        color=estilo.ACENTO, **estilo._prop('medio', 10))
ax.text(anios[-1] + 0.08, cobran[-1], f'{cobran[-1]:,}', va='center', ha='left',
        color=estilo.CONTEXTO, **estilo._prop('medio', 10))
ax.set_ylabel('Clubs')
ax.set_xlim(anios[0] - 0.2, anios[-1] + 0.9)
ax.set_ylim(0, max(cobran) * 1.15)
ax.grid(axis='y')
ax.set_axisbelow(True)
estilo.leyenda(ax)
estilo.guardar(fig, GRAFICOS / '02_mas_clubes_cada_ano.png')

# ===========================================================================
# 3 - Vender es una posición, no un mal año
# ===========================================================================
obs = dict(filas('SELECT temporadas_vendedor, clubes FROM m2_persistencia_resumen'))
p = float(filas('SELECT sum(temporadas_vendedor) / (4.0 * count(*)) FROM m2_persistencia')[0][0])
n = filas('SELECT count(*) FROM m2_persistencia')[0][0]

esperado = [comb(4, k) * (p ** k) * ((1 - p) ** (4 - k)) * n for k in range(5)]
observado = [obs.get(k, 0) for k in range(5)]
exceso = [o - e for o, e in zip(observado, esperado)]
etiquetas = ['Never', '1 season', '2 seasons', '3 seasons', 'All four']

fig, ax = estilo.figura(
    titular='96 clubs were net sellers in all four seasons; chance alone would have given 61',
    subtitulo='Clubs above or below what random role assignment would produce, by seasons as a '
              'net seller',
    periodo='2022/23-2025/26  ·  350 clubs present in all four seasons',
    fuente=FUENTE_B,
    nota='The baseline is a binomial with the same marginal probability of being a net seller '
         '(0.65). Both ends come out over-represented and the middle under-represented: roles '
         'persist rather than being redealt each summer.',
    abajo=0.20,
)
estilo.barras_divergentes(ax, etiquetas, exceso)
ax.set_xlabel('Clubs above (+) or below (-) chance')
estilo.guardar(fig, GRAFICOS / '03_vender_es_estructural.png')

# ===========================================================================
# 4 - La prima juvenil que no aparece
# ===========================================================================
tm = dict(filas("""
    SELECT year(fecha),
           ROUND(avg(CASE WHEN tramo_fifa = '18-23' THEN fee_eur END)
                 / avg(CASE WHEN tramo_fifa = '24-29' THEN fee_eur END), 3)
    FROM u1 WHERE year(fecha) IN (2022, 2025) GROUP BY 1
"""))
fifa = dict(filas("""
    SELECT year,
           ROUND(max(CASE WHEN age_band = '18-23' THEN media END)
                 / max(CASE WHEN age_band = '24-29' THEN media END), 3)
    FROM (
      SELECT year, age_band,
             COALESCE(avg_fee_usd_m,
                      COALESCE(total_fee_usd_m, 0) / NULLIF(transfers_with_fee, 0)) AS media
      FROM raw_fifa_edad WHERE age_band IN ('18-23', '24-29')
    ) WHERE year IN (2022, 2025) GROUP BY year
"""))

fig, ax = estilo.figura(
    titular='A young player costs about what a peak-age one costs, and still does',
    subtitulo='Average fee for an 18-23 player divided by the average fee for a 24-29 player',
    periodo='2022 vs 2025  ·  calendar years  ·  both sources, averages for comparability',
    fuente=f'{FUENTE_A}; {FUENTE_B}',
    nota='Above the parity line the young player is dearer; below, cheaper. Levels differ because '
         'the universes do; neither moves far, and neither escalates.',
    izquierda=0.20,
    abajo=0.20,
)
ax.axhline(1.0, color=estilo.TINTA_SUAVE, linewidth=1.1, linestyle=(0, (4, 3)), zorder=1)
estilo.slope(
    ax,
    ['Transfermarkt', 'FIFA census'],
    [float(tm[2022]), float(fifa[2022])],
    [float(tm[2025]), float(fifa[2025])],
    '2022', '2025',
    colores=[estilo.ACENTO, estilo.CONTRA],
    formato='{:.2f}',
)
ax.text(0.5, 1.006, 'PARITY', va='bottom', ha='center', color=estilo.TINTA_SUAVE,
        **estilo._prop('medio', 8))
ax.set_ylabel('Ratio of average fees')
ax.set_ylim(0.80, 1.20)
estilo.guardar(fig, GRAFICOS / '04_prima_juvenil_inexistente.png')

# ===========================================================================
# 5 - Dos velocidades dentro del tramo joven
# ===========================================================================
rangos = filas("""
    SELECT CASE WHEN fee_eur < 5e6 THEN 'Under EUR 5m'
                WHEN fee_eur < 40e6 THEN 'EUR 5m to 40m'
                ELSE 'EUR 40m or more' END AS rango,
           ROUND(100.0 * count(*) / sum(count(*)) OVER (), 1),
           ROUND(100.0 * sum(fee_eur) / sum(sum(fee_eur)) OVER (), 1)
    FROM u1 WHERE tramo_fifa = '18-23'
    GROUP BY rango
    ORDER BY min(fee_eur)
""")
nombres = [r[0] for r in rangos]
pct_ops = [r[1] for r in rangos]
pct_gasto = [r[2] for r in rangos]
colores = [estilo.RAMPA[1], estilo.RAMPA[3], estilo.ACENTO]

fig, ax = estilo.figura(
    titular='2% of young-player deals take a quarter of the money spent on them',
    subtitulo='Deals for players aged 18-23 by fee size: share of deals against share of spending',
    periodo='2022/23-2025/26  ·  3,029 priced deals for 18-23 year olds',
    fuente=FUENTE_B,
    nota='The headline signings are real, but they sit on top of a long cheap tail, and it is the '
         'tail that moves the aggregate.',
    izquierda=0.135,
)
for valores, y in ((pct_ops, 1), (pct_gasto, 0)):
    izquierda = 0.0
    for nombre, valor, color in zip(nombres, valores, colores):
        ax.barh(y, valor, left=izquierda, height=0.46, color=color,
                edgecolor=estilo.PAPEL, linewidth=1.6,
                label=nombre if y == 1 else None)
        if valor >= 6:
            ax.text(izquierda + valor / 2, y, f'{valor:.0f}%', va='center', ha='center',
                    color=estilo.PAPEL if color == estilo.ACENTO else estilo.TINTA,
                    **estilo._prop('medio', 10))
        izquierda += valor
ax.set_yticks([1, 0])
ax.set_yticklabels(['Deals', 'Spending'])
ax.set_xlim(0, 100)
ax.set_ylim(-0.55, 1.75)
ax.set_xlabel('Percent of the 18-23 bracket')
estilo.leyenda(ax, ncol=3)
estilo.guardar(fig, GRAFICOS / '05_dos_velocidades.png')

con.close()

print('Figuras generadas:')
for f in sorted(GRAFICOS.glob('*.png')):
    print(f'  {f.name:<40} {f.stat().st_size / 1024:>7.1f} KB')
