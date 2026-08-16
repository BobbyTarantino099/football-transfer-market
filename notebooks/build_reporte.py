"""Builds entregables/reporte-tecnico.html and .pdf — the case's technical report.

Condenses what CASO.md records across 590 lines: the eight phases, the decisions that
could have gone another way, and where it ended. The executive summary answers "what
should we do"; this answers "how do I know you did it properly".

Content is written here rather than parsed from the Markdown, same as build_docx.py, so
the two stay in sync deliberately and not by regex accident.

Run: python notebooks/build_reporte.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reporte  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
G = BASE / 'salidas' / 'graficos'

doc = reporte.Reporte(
    titulo='The football transfer market: who pays whom, and what age costs',
    acento='#0f7d3f',
    contra='#7b4bb0',
)

# --- Portada ---------------------------------------------------------------
doc.portada(
    eyebrow='Technical report · Portfolio case study',
    hallazgo='Two things the industry treats as settled turn out to be wrong. Spending is '
             'spreading out, not concentrating, and young players carry no price premium. Both '
             'were written down as a hypothesis before the analysis — and contradicted by it.',
    meta=[
        ('Domain', 'Football / sports finance'),
        ('Tools', 'SQL · DuckDB · Python · matplotlib'),
        ('Scale', '6,716 priced transfers · €37.4bn'),
        ('Sources', 'FIFA TMS census · Transfermarkt (CC0)'),
        ('Window', '2022/23–2025/26 · census 2016–2025'),
        ('Published', '15 August 2026'),
    ],
    figura=G / '03_vender_es_estructural.png',
    pie_figura='Clubs above or below what random role assignment would produce. Both tails are '
               'over-represented: the role persists rather than rotating each summer.',
)

# --- Las ocho fases --------------------------------------------------------
doc.seccion(
    'The eight phases, and what each one settled',
    'Every phase closes on an exit gate checked point by point. When one fails the process goes '
    '<em>back</em> a phase rather than improvising forward — which is what happened in phase 2.',
    salto=True,
)
doc.fases([
    ('0 · Choose',
     'A client that can see both sides of the market',
     'A multi-club fund, not a selling club: a client on one side of a gap cannot reason about '
     'the gap. Source picked only after an integrity test, not before.'),
    ('1 · Ask',
     'A SMART question, and the hypothesis written down first',
     'Three measurable parts: concentration, persistence of role, age. The expected answer was '
     'recorded before any analysis — the only way a later contradiction is credible.'),
    ('2 · Prepare',
     'Two sources with separate jobs, and a bias caught in time',
     'ROCCC on each. The integrity test exposed a survivorship bias that would have inverted the '
     'conclusion, forcing the deal-level window down to four seasons.'),
    ('3 · Process',
     'SQL on DuckDB, with a reconciliation that must hold',
     '175,165 rows down to 8,480 priced deals. Nothing needed correcting; every transformation is '
     'a selection, and the checks that came back empty are recorded anyway.'),
    ('4 · Analyse',
     'Five metrics, ten verification blocks',
     'Two findings survived unchanged, one was narrowed after failing a robustness check, and the '
     'hypothesis fell on both axes.'),
    ('5 · Share',
     'Five figures, five different forms',
     'One message per figure, each headline carrying a number. No form repeated from the previous '
     'case: matching form to question is part of the craft.'),
    ('6 · Act',
     'Three recommendations, each with its risk and its assumption',
     'Plus one deliberately withheld: the Saudi channel is a real finding, but four seasons cannot '
     'separate a structural change from a spending cycle.'),
    ('7 · Portfolio',
     'Published against a contract enforced by code',
     'The site build fails if a required field is missing. Aggregates cross; raw data stays in the '
     'repository.'),
])
doc.cerrar()

# --- Decisiones ------------------------------------------------------------
doc.seccion(
    'The decisions that defined the case',
    'Eight of the twenty-one recorded in <strong>CASO.md</strong>. The discarded alternative is '
    'the line that matters: it shows the choice was reasoned rather than reflexive.',
    salto=True,
)
doc.decisiones([
    ('The client is a multi-club fund, not a selling club',
     'The question is about a gap between the two sides of the market, so the client has to be '
     'able to see both.',
     'An academy club that sells talent — it would only ever have seen its own side.'),
    ('DuckDB as the engine, not BigQuery',
     'The result has to rebuild from the repository alone. DuckDB reads the compressed CSVs '
     'directly and needs no server and no account.',
     'BigQuery — it would have forced a cloud account on anyone verifying the work.'),
    ('Two sources, never joined at record level',
     'FIFA is a census with no survivorship bias but never names a club; Transfermarkt names '
     'everyone but its coverage is uneven. Each covers the other\'s blind spot.',
     'A single source — Transfermarkt alone would have produced a confident, wrong decade trend.'),
    ('Deal-level analysis restricted to four seasons',
     'Coverage before 22/23 thins backwards and differentially by age, which is the very axis '
     'under study.',
     'The full 2010–2026 range, or a statistical correction — neither could be validated, and a '
     'decade of wrong-but-confident trend is worse than four honest seasons.'),
    ('Two declared universes instead of one',
     'Deals with only the buyer identified are 60% aged 18–23 at a quarter of the median price — '
     'the cheap purchases of young talent that are the phenomenon itself.',
     'Keeping only fully-identified deals: 93% of the money, and biased against exactly what the '
     'case set out to measure.'),
    ('The youth-premium claim narrowed after verification',
     'The reading "the ratio fell from 1.25 to 0.955" appeared only when cutting by season and '
     'hung on one starting observation.',
     'Publishing the fall — a better headline, and an artefact of specification.'),
    ('Level claims from FIFA, "who bought from whom" from Transfermarkt',
     'Our youth share runs 4–8 points below the census every year, because FIFA counts only '
     'international transfers.',
     'Trusting one source for both — it would have understated the youth share by up to 8 points.'),
    ('Outliers investigated and kept',
     'Bellingham at €127m, Gvardiol at €90m and Højlund at €79.8m are real deals and the subject '
     'of the case. The skew is handled with medians.',
     'Trimming the top percentile — statistically tidier, and it would delete the phenomenon.'),
])
doc.cerrar()

# --- El momento crítico ----------------------------------------------------
doc.seccion(
    'The moment the case nearly went the other way',
    salto=True,
)
doc.critico('Survivorship bias, caught in phase 2 rather than discovered in phase 5', [
    'Transfermarkt rebuilds each player\'s history from the players present in its base '
    '<em>today</em>. Coverage therefore thins going backwards — and, critically, it thins '
    '<strong>differentially by age</strong>.',
    'Taken at face value the source says the youth share of spending collapsed since 2010. That '
    'is not football: it is who survives in the database. The naive reading would have answered '
    'the <strong>opposite</strong> of the hypothesis, for reasons unrelated to the sport.',
])
doc.tabla(
    ['Season', 'Priced deals', 'Mean age', 'Share aged 18–21'],
    [
        ['2010/11', '143', '20.8', '53.8%'],
        ['2013/14', '372', '21.5', '44.9%'],
        ['2017/18', '936', '23.2', '27.5%'],
        ['2021/22', '1,343', '23.9', '25.5%'],
        ['2022/23', '1,746', '24.4', '19.9%'],
        ['2025/26', '2,367', '24.4', '21.2%'],
    ],
    numericas=(1, 2, 3),
)
doc.html_libre(
    '<p>The real 2010/11 market had thousands of priced transfers, not 143. From 22/23 the series '
    'stabilises — mean age flat at 24.4 — so deal-level analysis uses those four seasons and every '
    'claim about a decade comes from FIFA\'s census instead. <strong>Cross-checking two sources is '
    'what caught it</strong>; a single source would have looked perfectly consistent.</p>'
)
doc.cerrar()

# --- Hallazgos -------------------------------------------------------------
doc.seccion(
    'What the data says',
    'Each finding was written as a sentence carrying a number before any chart was drawn — the '
    'last check that it was closed rather than a topic.',
    salto=True,
)
doc.html_libre('<h3>1 · The money is spreading out, not concentrating</h3>')
doc.figura(G / '01_concentracion_cae.png',
           'Top 10% of buyers: 65% of spending in 2022/23, 60% in 2025/26.')
doc.html_libre(
    '<p>Top-10 share fell from <strong>32.1% to 26.7%</strong> while buying clubs rose from 339 to '
    '382. It holds without English buyers (30.6% → 24.0%), and FIFA\'s census backs it over eight '
    'years: <strong>45% more clubs paying fees</strong> than in 2018.</p>'
)
doc.figura(G / '02_mas_clubes_cada_ano.png',
           'FIFA TMS census: clubs paying a fee up 45% since 2018, clubs receiving one up 49%.')
doc.html_libre('<h3>2 · Youth carries no premium</h3>')
doc.figura(G / '04_prima_juvenil_inexistente.png',
           'Ratio of average fees, 18-23 against 24-29, in both sources.')
doc.html_libre(
    '<p>An 18–23 player costs about what a 24–29 player costs, and the ratio does not escalate in '
    'either source. Levels differ because the universes do; the direction is what matters, and '
    'neither rises.</p>'
    '<h3>3 · But the young market runs at two speeds</h3>'
)
doc.figura(G / '05_dos_velocidades.png',
           'Share of deals against share of spending, players aged 18-23.')
doc.html_libre(
    '<p>Deals of €40m or more are <strong>2.3% of transactions and 23.8% of the money</strong>; the '
    '71% under €5m account for 15%. Seven of the ten largest buyers are English.</p>'
)
doc.cerrar()

# --- Verificación ----------------------------------------------------------
doc.seccion(
    'What each check ruled out',
    'A finding that survives only one way of measuring it is a choice, not a result.',
    salto=True,
)
doc.tabla(
    ['Check', 'What it ruled out', 'Outcome'],
    [
        ['V1 · Census sanity', 'That our youth share tracks FIFA', 'Gap widens to 7.1 pts in 2025 — no claim made on that axis'],
        ['V1b · Both sources', 'That the finding depends on our data', 'Neither source shows escalation'],
        ['V2 · Recomputation', 'An aggregation error', 'Identical from deal level'],
        ['V3 · Denominators', 'A wrong base', 'Every share sums to 100 within its season'],
        ['V4 · Without England', 'A Premier League artefact', 'Holds: 30.6% → 24.0%'],
        ['V4b · Census decade', 'A four-season blip', '+44.7% buyers over eight years'],
        ['V5 · Effect size', 'Differences too small to act on', '−5.4 points of concentration'],
        ['V5b · Specification', 'A result that depends on how time is cut', 'It did — the claim was narrowed'],
        ['V6a · Null model', 'That persistence is arithmetic', 'Both tails over-represented'],
        ['V6b · Largest buyer', 'That one club drives the ratio', 'Barely moves without it'],
    ],
)
doc.cerrar()

# --- Cierre ----------------------------------------------------------------
doc.seccion('Conclusions, limits and what this case demonstrates', salto=True)
doc.html_libre(
    '<h3>Recommendations</h3>'
    '<ul>'
    '<li><strong>Buy into a persistent net seller in a mid-tier league</strong>, not an elite club. '
    'Ajax banked €267m net across four seasons, Salzburg €234m; Chelsea (−€800m) and Manchester '
    'United (−€672m) never sold.</li>'
    '<li><strong>Cap prices against the market band</strong> and write into the mandate that age '
    'carries no premium. A policy line, not a project.</li>'
    '<li><strong>Make each club pick its lane</strong> — cheap volume or elite few.</li>'
    '</ul>'
    '<h3>What these data cannot answer</h3>'
    '<ul>'
    '<li><strong>Four seasons are not a trend.</strong> Every claim about direction over time rests '
    'on the census.</li>'
    '<li><strong>The youth spending share is not claimable</strong> in level or direction: the two '
    'sources disagree and the 2025 gap doubles without a defensible explanation.</li>'
    '<li><strong>Nothing here is causal</strong>, and net transfer income is not profit — without '
    'club accounts, "sells well" is not "makes money".</li>'
    '<li><strong>Under-18s are not analysable</strong> at 2–7 priced deals a season.</li>'
    '</ul>'
    '<h3>What this case demonstrates</h3>'
    '<p>A hypothesis written down before the analysis and published unchanged when the data '
    'contradicted it, on both axes. Underneath it, the reason the answer is trustworthy: a '
    'data-quality decision taken in phase 2 rather than discovered in phase 5, by reconciling a '
    'scraped dataset against an official census instead of trusting either alone.</p>'
)
doc.pie(
    'Full phase log, cleaning log with every discarded alternative, ROCCC source records and the '
    'ten verification blocks: <strong>CASO.md</strong> in the case repository — '
    'github.com/BobbyTarantino099/football-transfer-market'
)
doc.cerrar()

doc.escribir(BASE / 'entregables' / 'reporte-tecnico.html')
