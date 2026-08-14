<!-- The living artefact of the case. It grows phase by phase; it is not written at the end.
     Each phase closes only when its exit gate passes point by point. If one fails, go BACK
     to an earlier phase instead of improvising forwards.
     Gates: site/framework/caso-de-estudio-datos/references/0X-*.md -->

# Case: The football transfer market — who pays whom, and what age costs

**Status:** Phase 0 — Choose (complete)
**Last updated:** 2026-08-13

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

- **Hypothesis, recorded before any analysis:** the gap is widening and the youth premium is
  outgrowing the market.
- **The trap this design avoids:** in nominal terms "transfers got more expensive" is true by
  construction — the whole market grew. Every figure must be expressed relative to its own
  season's market. If the youth premium dissolves once normalised, that is the finding, and it
  contradicts the hypothesis above. Which is why the hypothesis is written down here, first.

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

**Status:** ⬜ open

- **Business problem:** <the decision that cannot be made today>
- **Analytical question (SMART):** <specific, measurable, with its filters and controls stated>
- **Decision this unlocks:** <what changes once it is answered>
- **Problem type:** <find patterns · predict · categorize · spot something unusual ·
  identify themes · discover connections — exactly one, and it must match `problemType`
  in the site's front-matter>

- **Stakeholders:**

| Who | What they decide / need | Format |
|---|---|---|
| | | |

- **Metrics:**

| Metric | Formula | Unit | Granularity | Window |
|---|---|---|---|---|
| | | | | |

## 2. Prepare

**Status:** ⬜ open

- **Sources:** one ROCCC record per source in `documentacion/fichas-de-fuente.md`.
- **Data dictionary:** `documentacion/diccionario-de-datos.md`.
- **Licence and privacy:** <no personal data, licence allows publication>
- **Raw filename:** `datos/crudos/<origen_tema_periodo_version>.csv`

## 3. Process

**Status:** ⬜ open

Every transformation goes in `bitacora-limpieza.md`, with its rationale. Raw data is never
modified in place: each transformation produces a new file.

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
