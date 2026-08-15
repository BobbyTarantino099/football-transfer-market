<!-- The living artefact of the case. It grows phase by phase; it is not written at the end.
     Each phase closes only when its exit gate passes point by point. If one fails, go BACK
     to an earlier phase instead of improvising forwards.
     Gates: site/framework/caso-de-estudio-datos/references/0X-*.md -->

# Case: The football transfer market — who pays whom, and what age costs

**Status:** Phase 3 — Process (complete). Next: phase 4, Analyse.
**Last updated:** 2026-08-15

## 0. Choose (decision sheet)

**Date:** 2026-08-13

### The case

- **Sector:** professional football economics — where sporting performance meets money.
- **Fictional client:** a **multi-club investment fund** holding stakes in several European clubs.
  Chosen deliberately: a client that were only a selling club could not reason about a *gap*
  between buyers and sellers, because it only ever sees one side of it.
- **Business problem:** the fund cannot decide where to place its next tranche of capital —
  a developing, net-selling club, a mid-table club, or an elite one — without knowing whether the
  "develop and sell" model still carries a margin or has been squeezed.
- **Decision it unlocks:** which link of the chain to buy into, and whether the premium paid for
  young players justifies doubling down on academy investment.
- **Audience:** the fund's investment committee — financial readers, not football people.

**What triggered it:** in the 2026 window, very large fees were paid for players with no
superstar record, and for players aged 17–21 still in development.

### The question

> Across the European transfer market over the last decade, has the gap between net-buying and
> net-selling clubs widened, and has the premium paid for players aged 17–21 grown **faster than
> the market as a whole**?

Two cuts of one table, not two cases: **who pays whom**, and **what is paid by age**.

The hypothesis and the measurement trap it has to survive are recorded in §1, where phase 4 will
look for them.

### Scope of the universe

The **European market**, defined operationally as *any transfer where at least one of the two
clubs belongs to a European association*. Purchases from South America and sales to Saudi Arabia
or MLS are in scope on purpose: a new buyer with deep pockets is exactly the kind of shock that
widens a gap. Club nationality, not player nationality.

### The data — two sources, two different jobs

| # | Source | Job | Licence |
|---|---|---|---|
| A | **FIFA Global Transfer Report** (FIFA TMS) | The decade-long series and the age axis | FIFA publication; aggregate figures transcribed and cited |
| B | **`dcaribou/transfermarkt-datasets`** | Deal-level detail, 22/23–25/26 | **CC0-1.0** |

They are never joined at record level. A is the official **census** of international transfers —
it has no survivorship bias and sets the context. B is a scrape of Transfermarkt that names clubs
and players, which is what makes the buyer/seller gap computable at all.

**Source A — checked 2026-08-13.** Annual since 2011, published every January; 2025 edition is 69
pages, downloadable without an account. Reports global spend (USD 13.08bn in 2025, +52.3% on the
USD 8.59bn of 2024), 24,558 international transfers, 1,214 clubs paying a fee and 1,495 receiving
one, plus breakdowns by player age, by fee size and by transfer type. Aggregates only: no
deal-level records.

**Source B — integrity test run 2026-08-13.** 175,165 transfers, 23,379 players, DuckDB file and
gzipped CSVs served directly, refreshed weekly.

| Check | Result |
|---|---|
| Candidate key (player, date, from, to) | ✅ 0 duplicates |
| Date of birth (so age is computable) | ✅ 2 missing out of 17,554 priced deals |
| Fee present and positive | ⚠️ 17,554 of 175,165 rows (10%) — see below |
| Country of both clubs | ⚠️ origin unknown in 27.7%, destination in 14.4% of priced deals |
| Extreme values | ✅ plausible — Neymar 222M€, Mbappé 180M€, Isak 145M€ |
| Transfer dates | ⚠️ range runs to 2030-06-30: pre-agreed future moves must be filtered |

**⚠️ The finding that shaped the design — survivorship bias.** Source B builds each player's
history from the players *present in the base today*, not season by season. Coverage therefore
thins going backwards, and it thins **differentially by age**:

| Season | Priced deals | Mean age | Share of deals aged 18–21 |
|---|---|---|---|
| 10/11 | 143 | 20.8 | 53.8% |
| 13/14 | 372 | 21.5 | 44.9% |
| 17/18 | 936 | 23.2 | 27.5% |
| 21/22 | 1,343 | 23.9 | 25.5% |
| 22/23 | 1,746 | 24.4 | 19.9% |
| 25/26 | 2,367 | 24.4 | 21.2% |

The real 2010/11 market had thousands of priced transfers, not 143. Only players who were young
then and are still active now survive in the base — which makes mean age *rise* and the 18–21
share *fall* as artefacts. Taken naively, source B would answer the opposite of the hypothesis for
reasons that have nothing to do with football. **From 22/23 onwards the series stabilises**
(mean age flat at 24.4, 18–21 share around 21%), so source B is used only over 22/23–25/26 — four
clean windows, 8,480 priced deals — and the decade comes from source A.

The parser also collapses loans, free transfers and unknown fees to 0 or null, so only `fee > 0`
rows carry price information. Priced deals are the analysis population; that is defensible, since
the question is about what gets paid.

### Calibration

- **Effort:** ~1 week.
- **Enough for a 30-minute talk?** Yes: two axes, a decade of context, a live 2026 hook, and a
  data-quality decision worth explaining on its own.
- **Real cleaning to document?** Yes — the fee parser, the survivorship window, unmatched clubs,
  future-dated transfers.

### Portfolio fit

- **What it demonstrates that `steam-price-reception` doesn't:** SQL as the primary tool,
  longitudinal data, sport/finance domain, and reconciling an official census against a scraped
  dataset instead of trusting one source.
- **Primary tool:** SQL on **DuckDB** — local, reads CSV/Parquet directly, so the whole result
  rebuilds from the repo with no cloud account. Figures stay in Python via `estilo.py`, which is
  what keeps every case looking like one family.
- **Dataset saturation:** medium. Transfermarkt is heavily used; this angle — buyer/seller gap and
  a normalised age premium, cross-checked against FIFA TMS — is not.

### Decision

- [x] **Go.**

## 1. Ask

**Status:** ✅ closed 2026-08-14

- **Business problem:** the fund is about to commit capital to a football club and cannot say which
  end of the market pays. Buying into a developing, net-selling club only makes sense if selling
  talent is still where the margin sits; buying into an elite one only makes sense if the money
  really is concentrating there.

- **Analytical question (SMART):**

  > Across the European transfer market, and over the four windows from 2022/23 to 2025/26, is
  > spending concentrating on fewer buying clubs, and is a larger share of it going to players
  > under 24?

  Broken into three measurable parts, because one compound question cannot be answered at once:

  - **A. Concentration.** What share of each season's total spending is captured by the ten
    largest buying clubs, and does that share move across the four windows?
  - **B. Persistence of role.** How many clubs are net sellers in three or more of the four
    seasons? A role that repeats is a structural position; a role that alternates is noise.
  - **C. The age axis.** What share of each season's spending goes to each FIFA age band, and how
    does the median fee for an 18–23 player compare with a 24–29 one?

- **Decision this unlocks:** which link of the chain gets the next tranche — a net-selling
  developer, a mid-table club or an elite buyer — and whether the price paid for young players
  justifies funding an academy over buying a squad.

- **Problem type:** `find patterns`.

- **Initial hypothesis, written before any analysis:** the gap is widening — spending concentrates
  on fewer buyers — and the share going to young players is growing faster than the market itself.

- **The measurement trap this design has to survive:** in nominal terms "transfers got more
  expensive" is true by construction, because the whole market grew. Every figure here is therefore
  a **share of its own season's total** (M5), which makes nominal growth incapable of passing for a
  finding. If the youth premium dissolves once normalised, that is the result, and phase 4 records
  it as contradicting the line above.

- **Out of scope** — stated now so it cannot be negotiated later:
  - *Why* prices move — broadcast money, state ownership, accounting amortisation. This case
    describes the structure; it does not explain it.
  - Any prediction or causal claim.
  - Women's football: source B covers it too thinly to say anything honest.
  - Loans and free transfers (see §0: they cannot be told apart upstream).
  - Whether a signing worked out on the pitch — no performance data enters this design.
  - The 26/27 window, open while this is written: it is the hook, never a data point.
  - Fee-to-market-value multiples: Transfermarkt valuations move on transfer rumours, so the
    multiple would partly be measuring its own input.

- **Stakeholders:**

| Who | What they decide / need | Format |
|---|---|---|
| Investment committee of the fund *(primary)* | Approves where the next tranche goes. Needs to know whether the net-seller role is structural, and whether the youth premium is real once normalised | 8–10 slides + a one-page summary |
| Sporting directors of the fund's clubs *(secondary)* | Execute the sales. Need the age band where price peaks | Table by age band |
| Risk function of the fund *(secondary)* | Signs off the assumptions. Needs the coverage limits stated plainly, not buried | Technical note — this file and `bitacora-limpieza.md` |

- **Analysis population:** priced transfers only — `transfer_fee > 0`, `transfer_date` not in the
  future, and at least one club belonging to a European association. A season runs 1 July to
  30 June. Age is completed years at `transfer_date`.

- **Metrics:**

| Metric | Formula | Unit | Granularity | Window |
|---|---|---|---|---|
| **M1 · Top-10 buyer concentration** | rank clubs by inbound spend; Σ fees of the top 10 ÷ Σ fees of all deals × 100 | % of season spend | season | 22/23–25/26 · source B |
| **M2 · Net-seller persistence** | `net(club, season) = fees paid − fees received`; count seasons with `net < 0`, out of 4. Eligible clubs are those with at least one priced deal in **each** of the four seasons — a club absent from a season would otherwise score `net = 0` there and read as "not a seller", which is not the same thing | seasons (0–4) | club | 22/23–25/26 · source B |
| **M3 · Age-band spend share** | Σ fees of the band ÷ Σ fees of the season × 100. Bands: FIFA `<18 / 18–23 / 24–29 / 30+`, plus a finer `<18 / 18–20 / 21–23` inside the young block | % of season spend | season × band | 2015–2025 · source A; 22/23–25/26 · source B |
| **M4 · Youth price ratio** | median fee of 18–23 ÷ median fee of 24–29. Median, not mean: FIFA reports 3.8% of deals carrying nearly half of all spending, so a mean would track a handful of moves | ratio | season | 22/23–25/26 · source B |
| **M5 · Season market size** *(control, not a finding)* | Σ fees of the season | EUR | season | both sources |

M3 is the metric that answers the question and the one comparable against the official census;
M4 says what a typical young player costs against a typical peak-age one. M1 and M2 answer the
buyer/seller half — and M2 is the one that actually decides where capital goes, since a role held
in three or four seasons out of four is a position, not a coincidence.

## 2. Prepare

**Status:** ✅ closed 2026-08-14

- **Sources:** one ROCCC record per source in `documentacion/fichas-de-fuente.md`.
- **Data dictionary:** `documentacion/diccionario-de-datos.md`.

### The fields the question demands, written before looking

| Need | Granularity | Period | Where it comes from |
|---|---|---|---|
| Fee paid | per deal | 4 seasons | B `transfer_fee` |
| Player age at transfer | per deal | 4 seasons | B `date_of_birth` + `transfer_date` |
| Both clubs, identifiable, with country | per deal | 4 seasons | B `clubes` → `competiciones` |
| Spend by age band | per year | a decade | A, transcribed |
| Market size | per year | a decade | A `total_fee_usd_bn` |
| Clubs paying vs receiving | per year | a decade | A |

Classification: **A** is first-party, external, structured, quantitative and longitudinal — but
aggregate. **B** is third-party, external, structured, quantitative and longitudinal at deal level.
Neither is first-party to us; both are external and public.

### The two universes, and why there are two

Coverage of the `clubes` table is partial, and *not at random*. In the window, priced deals split:

| | Deals | % of spend | Mean age | 18–23 share | Median fee |
|---|---|---|---|---|---|
| Both clubs identified | 5,977 | 93.0% | 24.8 | 38.8% | 2.2M€ |
| Only the buyer identified | 1,579 | 4.8% | 23.0 | **60.2%** | 0.5M€ |
| Only the seller identified | 406 | 1.5% | 25.4 | 31.8% | 0.6M€ |
| Neither | 518 | 0.7% | 22.7 | 51.7% | 0.3M€ |

Keeping only "both identified" would have been the obvious move and the wrong one: that block is
the oldest and most expensive, while the deals it discards are the cheap purchases of young talent
from clubs outside the covered competitions — the exact phenomenon under study. So:

- **U1** — at least one club identified and European. Basis for M3, M4, M5.
  **6,716 deals · €37,436m** across the four seasons.
- **U2** — both clubs identified, at least one European. Basis for M1 and M2, which have to
  attribute spend to a named club. **5,109 deals · €35,414m**, i.e. 94.6% of U1's money.

Every published figure states which universe it came from. "European" is decided by the source's
own `confederation` field, not by player nationality.

### Biases, in writing

- **Survivorship** — quantified in §0 and answered with the 22/23 cut-off. This is the one that
  would have inverted the conclusion.
- **Sampling** — partial club coverage, non-random by age and price. Answered with the two
  universes above rather than by dropping the inconvenient rows.
- **Observer** — Transfermarkt *estimates* market values but *reports* fees. Only fees are used;
  estimated values are out of scope (§1).
- **Confirmation** — the hypothesis is written in §1 before any analysis. The countermeasure is
  stated too: if the result confirms it too cleanly, it gets checked harder, not less.
- **Interpretation** — the nominal/normalised trap. Every figure is a share of its own season.

### Licence, privacy, security, accessibility

- **Licence.** B is CC0-1.0, verified via the GitHub API. A has no open licence: aggregate figures
  are transcribed and cited, and the PDFs are not redistributed.
- **Privacy.** No sensitive personal data. Player names and dates of birth are published facts
  about public figures; no contact details, no private individuals' salaries.
- **Security.** Nothing confidential; all inputs are public and the snapshot lives in the repo.
- **Accessibility.** Anyone can rebuild this: `git clone` gives the frozen snapshot, the FIFA CSVs
  and `notebooks/descargar.py`. No account, no key, no cloud. SHA-256 of each file is recorded in
  the source record so a reproducer can tell "newer snapshot" from "bug".

### Integrity test on the final window

| Season | U1 deals | U1 spend | U2 deals | U2 spend |
|---|---|---|---|---|
| 22/23 | 1,359 | €7,460m | 1,070 | €7,092m |
| 23/24 | 1,651 | €9,508m | 1,251 | €8,993m |
| 24/25 | 1,780 | €9,225m | 1,329 | €8,626m |
| 25/26 | 1,926 | €11,242m | 1,459 | €10,703m |

Key unique (0 duplicates), age computable on every row of the window, future-dated moves excluded,
extremes plausible.

**External cross-check — and the rule it produces.** Our 18–23 spending share against FIFA's:

| | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|
| Source B (U1) | 50.7% | 45.7% | 47.2% | 47.1% |
| Source A (calendar year) | 54.4% | 50.8% | 52.2% | 55.1% |

Same order of magnitude, but B runs 4–8 points low every year, and B's under-18 share is three to
five times smaller than the census. Expected: FIFA counts only *international* transfers while B
also includes domestic ones, and seasons are not calendar years. The consequence is a rule for
phase 4: **claims about level come from A; claims about who from B.**

### Can these data answer the phase 1 question?

| Metric | Computable | On what |
|---|---|---|
| M1 · Top-10 buyer concentration | ✅ | U2 |
| M2 · Net-seller persistence | ✅ | U2 |
| M3 · Age-band spend share | ✅ | A 2018–2025 · B on U1 |
| M4 · Youth price ratio | ✅ | U1 (median; mean too, to compare against A) |
| M5 · Season market size | ✅ | both |

No metric had to be dropped, so the case does not go back to phase 1.

**Open question carried to phase 4** (Juanes, 2026-08-14): what outliers sit behind the jump from
41.3% to over 50% in the youth spending share? Answerable only in part — the 2018→2019 shift is
visible solely in source A, which never names a deal. What *can* be examined is the expensive
young-player outliers within 22/23–25/26, where source B has deal-level detail.

## 3. Process

**Status:** ✅ closed 2026-08-15

Every transformation is in `bitacora-limpieza.md`, with its rationale and its discarded
alternative. Raw data is never modified in place.

- **Tool:** SQL on DuckDB. Four tables to join, a window to select, a categorisation to apply —
  and a rebuild that needs no server and no account. Queries live in `consultas/` as real `.sql`
  files, not inside Python strings, so they can be read and judged on their own.
- **Pipeline:** `python notebooks/procesar.py` → `consultas/01_construir_base.sql` (faithful load)
  → `consultas/02_limpiar.sql` (window, population, universes, age bands).
- **Output:** `datos/limpios/football-transfer-market.duckdb` — gitignored and regenerated, since
  it is derived from a snapshot that is versioned.

**Reconciliation.** 175,165 − 109,038 (outside the window) − 15 (dated after the snapshot) −
57,632 (no usable fee) − 0 (no date of birth) = **8,480 priced deals**, of which 6,716 are U1 and
5,109 U2. It reconciles exactly, and the script fails loudly if it ever stops doing so.

**Nothing had to be corrected.** No duplicates, no impossible ages, no self-transfers, no stray
whitespace, no club under two ids. Every transformation here is a *selection*, not a repair — and
the checks are recorded precisely because they came back empty. Two things did need deciding:
DuckDB compares strings case-sensitively (verified, or the European filter would have silently
emptied), and fees are cast to `DECIMAL` rather than float, because summing 6,716 floats moved the
total by €1m.

**Outliers were investigated and kept.** Bellingham €127m, Gvardiol €90m, Højlund €79.8m: real
deals, and the subject of the case rather than noise in it. The skew is handled with medians, not
with deletions.

## 4. Analyse

**Status:** ⬜ open

- **Finding:** <the headline — the finding, not the topic. Same claim as `title` on the site.>
- **Checks:** `notebooks/verificar.py` — <what each one rules out>
- **Contradicted the initial hypothesis:** <yes/no — a "yes" is the most valuable outcome
  of all, because it shows the conclusion wasn't forced>

## 5. Share

**Status:** ⬜ open

- Figures in `salidas/graficos/`, built with `estilo.py` so every case looks like one family.
- Deliverables in `entregables/`. Binaries are generated by script, never edited by hand.

## 6. Act

**Status:** ⬜ open

- **Recommendations:** <each one tied to evidence, with its limitations>
- **Before publishing:** `bash scripts/verificar-rutas.sh` must pass.

## 7. Portfolio

**Status:** ⬜ open

- Hand over to the site: front-matter Markdown (template 7 of `plantillas.md`) plus figures and
  aggregate tables. Only that crosses; this file stays here and is linked.
- If an aggregate the site needs weighs megabytes, the aggregation is incomplete — go back to
  phase 4 and summarise further.

## Decision log

<Every decision that could have gone another way. This is what separates a defensible case
from a gallery of charts: it shows what was discarded and why.>

| Date | Decision | Reason | Alternative discarded |
|---|---|---|---|
| 2026-08-13 | Client is a multi-club investment fund | The question is about a *gap* between the two sides of the market; a single-sided client cannot see it | A net-selling academy club — would only have seen its own side |
| 2026-08-13 | DuckDB as the engine | The result must rebuild from the repo alone; DuckDB reads CSV/Parquet directly and needs no account | BigQuery — would force a GCP account on anyone verifying the work |
| 2026-08-13 | Two sources with separate jobs, never joined at record level | Only the FIFA census is free of survivorship bias; only Transfermarkt names clubs | A single source — Transfermarkt alone would have produced a confident, wrong decade trend |
| 2026-08-13 | Source B restricted to 22/23–25/26 | Coverage before 22/23 is biased differentially by age, which is the very axis under study | The full 2010–2026 range; a 2016 cut-off — bias persists there too |
| 2026-08-13 | Analysis population is `fee > 0` | Loans, free moves and unknown fees are all collapsed to 0/null upstream and cannot be told apart | Treating 0 as a genuine free transfer — would mix loans into price statistics |
| 2026-08-13 | `ewenme/transfers` rejected | No licence declared, and coverage stops at 22/23 | It captures by season, so it has no survivorship bias — the better shape, unusable terms |
| 2026-08-14 | FIFA age bands as the main axis, with a finer cut inside the young block | Only official bands let our number be checked against the census; the fine cut keeps the under-21 question answerable | Own bands (17–21 / 22–24 / …) — sharper focus, but nothing would have been comparable |
| 2026-08-14 | The gap is measured as concentration **plus** persistence of role, not net spend alone | Net spend describes clubs; persistence describes the structure, which is what a capital decision turns on | A Gini or HHI — more rigorous, but needs translating for an investment committee, and translation costs minutes on stage |
| 2026-08-14 | Median, not mean, for fee comparisons | FIFA reports 3.8% of deals carrying nearly half of global spending; a mean would track a handful of moves | The mean — easier to explain, and wrong here |
| 2026-08-14 | Fee-to-market-value multiples left out of scope | Transfermarkt valuations react to transfer rumours, so the multiple would partly measure its own input | Using them as the premium metric — the most intuitive framing, and circular |
| 2026-08-14 | Two universes (U1, U2) instead of one | Deals with only the buyer identified are 60% aged 18–23 at a quarter of the median price; dropping them would have removed the phenomenon under study | A single "both clubs identified" universe — 93% of the money, and biased against exactly the young cheap deals |
| 2026-08-14 | The Transfermarkt snapshot is versioned in the repo (9.3 MB) | Upstream refreshes weekly; without freezing it the case stops reproducing within a month | A download script plus recorded hashes — reproducers could detect a difference but not undo it |
| 2026-08-14 | FIFA age series starts in 2018 | The 2016 edition reports age year by year, not in bands, and 2017 publishes no fee by band | Reconstructing 2016–17 from a different structure — two more years, both invented |
| 2026-08-14 | "European" comes from the source's `confederation` field | A hand-built UEFA table agreed with it exactly, so it was deleted rather than kept as a second thing to maintain | Keeping our own country table — one more artefact to drift |
| 2026-08-14 | Level claims from source A, "who" claims from source B | B's youth share runs 4–8 points below the census every year, because it also counts domestic deals | Trusting B on level — would have understated the youth share by up to 8 points |
| 2026-08-15 | Queries as `.sql` files in `consultas/`, Python only as orchestrator | This is the case where SQL is the point; SQL hidden inside Python strings cannot be read or judged | Embedding the SQL in `procesar.py` like case 1 — simpler to run, unreadable as evidence |
| 2026-08-15 | Fees cast to `DECIMAL`, regression checked in whole euros | Summing 6,716 floats moved the total by €1m and failed the check for a rounding artefact rather than a real fault | Keeping floats and loosening the check — would have hidden a genuine drift later |
| 2026-08-15 | Outliers kept, skew handled with medians | The expensive young deals are the subject of the case, not noise in it | Trimming the top percentile — statistically tidier, and it would delete the phenomenon |
