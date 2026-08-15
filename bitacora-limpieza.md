<!-- Phase 3 deliverable. Raw data is NEVER modified in place: every transformation
     produces a new file and is logged here. Written as you clean, not afterwards. -->

# Cleaning log — the football transfer market

**Input datasets:** `datos/crudos/transfermarkt_*.csv.gz` — 175,165 transfers · 50,149 players ·
796 clubs · 65 competitions. Plus `datos/crudos/fifa_*.csv` — 46 transcribed rows.

**Output dataset:** `datos/limpios/football-transfer-market.duckdb` —
`traspasos_ventana`, 8,480 rows (1 row = one priced transfer inside the window), with the views
`u1` (6,716 rows) and `u2` (5,109 rows).

**Tool:** **SQL on DuckDB.** Chosen because the work is four tables that have to be joined, a
window to select and a categorisation to apply — exactly what SQL does well — and because DuckDB
reads the compressed CSVs directly, so the whole thing rebuilds from `git clone` with no database
server and no cloud account. The queries live in `consultas/` as real `.sql` files rather than
inside Python strings, so they can be read and judged on their own.

Full pipeline: `notebooks/procesar.py`, which executes `consultas/01_construir_base.sql` and
`consultas/02_limpiar.sql` and prints the reconciliation below.

## Transformations

### T1 — Load the raw snapshot unchanged
- **What:** four compressed CSVs and two transcribed CSVs, loaded into `raw_*` tables.
- **Why:** a load that already selects columns cannot be checked against the raw file afterwards.
- **How:** `read_csv_auto` with `SELECT *`, deliberately — the only place in the case where
  `SELECT *` is right. Paths arrive as DuckDB session variables so no `.sql` contains a path.
- **Rows affected:** none. 175,165 in, 175,165 out.
- **Alternative discarded:** selecting only the used columns at load time. Faster, and it would
  have made the cleaning unauditable against the source.

### T2 — Restrict to seasons 22/23–25/26
- **What:** 109,038 transfers outside the window dropped.
- **Why:** coverage before 22/23 is biased by survivorship **and differentially by age**, which is
  the very axis of the question. Quantified in `CASO.md` §0: mean age drifts 20.8 → 24.4 and the
  18–21 share falls 53.8% → 21.2% for reasons that have nothing to do with football.
- **How:** `WHERE transfer_season IN ('22/23','23/24','24/25','25/26')`.
- **Rows affected:** 175,165 → 66,127.
- **Alternative discarded:** keeping the full history and correcting the bias statistically. It
  would need a model of who survives in the base, which nobody can validate — and a decade of
  wrong-but-confident trend is worse than four honest seasons.

### T3 — Drop transfers dated after the snapshot
- **What:** 15 pre-agreed future moves, the raw data running to 2030-06-30.
- **Why:** a transfer that has not happened yet has no place in a count of what was paid.
- **How:** `WHERE transfer_date <= DATE '2026-08-14'`, the snapshot date.
- **Rows affected:** 66,127 → 66,112.
- **Alternative discarded:** cutting at "today" at run time. It would make the result drift every
  time the script runs, so the same repository would stop reproducing its own numbers.

### T4 — Keep only priced transfers
- **What:** 57,632 rows without a usable fee dropped.
- **Why:** upstream, the parser collapses loans, free transfers and unrecorded fees to `0` or
  `NULL` indistinguishably. A zero here does not mean "moved for free" — it can equally mean
  "moved on loan" or "the fee was never reported". Only `> 0` carries price information.
- **How:** `WHERE transfer_fee > 0`.
- **Rows affected:** 66,112 → 8,480.
- **Alternative discarded:** treating `0` as a genuine free transfer. It would have mixed loans
  into every price statistic, and loans skew young — which would have quietly inflated exactly the
  age effect the case is testing.

### T5 — Exclude players without a date of birth
- **What:** nothing, in this window.
- **Why:** without a birth date there is no age, and age is half the question.
- **How:** `LEFT JOIN` to `raw_jugadores` and then `WHERE edad IS NOT NULL`. The join is `LEFT`
  on purpose: an `INNER` join would have dropped such rows silently and reported no exclusion.
- **Rows affected:** 8,480 → 8,480. **Zero.** Recorded precisely because it is zero: the check ran.
- **Alternative discarded:** imputing an age from the season. Inventing the dependent variable.

### T6 — Universe U1: at least one identified European club
- **What:** 1,764 transfers with no identifiable European side dropped.
- **Why:** the case is about the European market, and a deal neither of whose clubs can be placed
  cannot be assigned to any market.
- **How:** club → `domestic_competition_id` → `confederation = 'europa'`. Club country, never
  player nationality. Both joins are `LEFT` so unmatched clubs survive as unknown rather than
  vanishing — they are 29.5% of deals but only 6.3% of the money.
- **Rows affected:** 8,480 → 6,716 · €37,436m.
- **Alternative discarded:** filtering by player nationality. It would count a Brazilian sold from
  one Brazilian club to another as European, and miss a Danish club selling to Saudi Arabia.

### T7 — Universe U2: both clubs identified
- **What:** a further 1,607 deals set aside for the club-level metrics only.
- **Why:** attributing spend to a named club requires knowing who both parties are. M1
  (concentration) and M2 (persistence) cannot be computed otherwise.
- **How:** flags `es_u1` / `es_u2` on one table, exposed as the views `u1` and `u2`.
- **Rows affected:** 6,716 → 5,109 · €35,414m, i.e. 94.6% of U1's money.
- **Alternative discarded:** using U2 for everything. The discarded block is 60.2% aged 18–23 at a
  quarter of the median price — the cheap purchases of young talent from outside the covered
  competitions. Dropping it would have removed the phenomenon under study, so price and age
  metrics stay on U1 and only club metrics use U2. This is why there are two universes and not one.

## Dirty-data review

The exit gate asks for each category to be checked explicitly, **even when the answer is "none"** —
an unrecorded check is indistinguishable from a check never run.

| Category | Checked | Result |
|---|---|---|
| Duplicates | same player + same date; `club_id` uniqueness | **0** duplicate operations; 796 clubs / 796 distinct ids |
| Out of date | snapshot frozen at 2026-08-14, hashes recorded | not applicable — the version is pinned |
| Incomplete | missing date of birth in the window | **0** |
| Incorrect | club transferring to itself; impossible ages; non-positive fees | **0**; ages span 14–39, all plausible; **0** |
| Inconsistent | club names with stray whitespace; one name under several ids | **0**; **0** |

**Case sensitivity.** DuckDB compares strings **case-sensitively** (`'europa' = 'EUROPA'` is
false), verified on 2026-08-15. The literal is therefore written exactly as the source stores it.
The anexo requires checking this per dialect; it would have silently emptied the European filter.

**Outliers: investigated, kept.** Fees span €1,000 to €145m, median €1.38m, p95 €22m — heavily
skewed, as the FIFA census also reports. The extremes are real transfers, not data errors: the
most expensive under-21 deals are Bellingham (€127m), Gvardiol (€90m), Højlund (€79.8m), all
verifiable. **They are not noise to filter — they are the subject.** Removing them would delete
the phenomenon and flatter the statistics. The skew is handled by reporting medians (M4), not by
deleting rows.

**Precision.** `transfer_fee` is cast to `DECIMAL(18,2)` rather than left as a float. Summing
6,716 floats moved the total by €1m against the phase 2 figure — noise, but noise that made a
regression check fail. Totals are now exact and the check compares whole euros.

## Integrity checks after cleaning

| Check | Expected | Result |
|---|---|---|
| Rows in vs rows out | 175,165 − 109,038 − 15 − 57,632 − 0 = 8,480 | ✅ reconciles exactly |
| `clubes` × `competiciones` join does not fan out | 796 → 796 | ✅ 796; the pipeline aborts if this ever changes |
| Duplicate keys | 0 | ✅ 0 |
| Nulls in the key columns | 0 | ✅ 0 in fee, date, age, season |
| Values out of range | 0 | ✅ ages 14–39, fees > 0 |
| Regression against phase 2 | U1 6,716 / €37,436,176,000 · U2 5,109 / €35,413,528,000 | ✅ exact |

The pipeline runs from the raw files in one command and rebuilds the database from scratch: it
deletes any previous `.duckdb` before starting, because a pipeline that reuses state is not
reproducible.
