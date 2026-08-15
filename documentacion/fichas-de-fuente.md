<!-- Phase 2 deliverable: one record per source. A source that fails ROCCC is not
     automatically discarded, but the failure must be declared and its effect on the
     conclusion assessed. -->

# Data source records — the football transfer market

Two sources doing two different jobs. **They are never joined at record level.** A is the official
census and sets the scale; B names the clubs and players. Where they disagree, A wins on level and
B wins on detail — the reason is in "What it cannot answer" below.

---

## Source A: FIFA Global Transfer Report

- **Link:** <https://inside.fifa.com/legal/football-regulatory/player-transfers/tms-reports>
- **Publisher:** FIFA, from the International Transfer Matching System (ITMS/TMS), the system
  through which every international transfer must legally be registered.
- **Licence:** FIFA publication, no open licence. The PDFs are **not redistributed** in this
  repository. What is stored here is our own transcription of published aggregate figures, each
  row carrying its edition, figure and page — facts, cited.
- **Period covered:** age breakdown 2018–2025; market series 2016–2025.
- **Volume:** 36 rows × 10 columns (age); 10 rows × 9 columns (market).
- **Downloaded on:** 2026-08-14 (nine editions consulted: 2016 to 2025).
- **Saved as:** `datos/crudos/fifa_edad_2018-2025_2026-08-14.csv` and
  `datos/crudos/fifa_mercado_2016-2025_2026-08-14.csv`

### ROCCC

| Letter | Assessment | Detail |
|---|---|---|
| **R**eliable | High | Not a sample or a scrape: every international transfer is legally required to pass through TMS, so this is a census. |
| **O**riginal | High | First party. FIFA operates the system that generates the data. |
| **C**omprehensive | **Low** | Aggregates only. It never names a club or a player, so it cannot answer anything about who buys from whom — which is half of the phase 1 question. |
| **C**urrent | High | Published every January; the 2025 edition arrived in January 2026. |
| **C**ited | High | Each edition carries its own methodology and disclaimer; every transcribed row records edition, figure and page. |

### What it can and cannot answer

- **Can:** the size of the market year by year, how spending splits across age bands, and how many
  clubs pay versus receive fees — all on a full census, free of survivorship bias.
- **Cannot:** name a single club or player. Any question about concentration among named buyers or
  about which clubs are structural sellers is outside what this source will ever answer.

### Declared limitations

- **The age series starts in 2018, not 2016.** The 2016 edition reports age year by year rather
  than in bands, and the 2017 edition publishes no fee by band. Two years of a longer series were
  dropped rather than reconstructed.
- **The bands change in 2022.** Editions 2018–2021 split 30–35 and >35; from 2022 they are merged
  into ≥30. Both are transcribed separately and summed downstream, so the aggregation stays
  auditable.
- **Average fee by band is missing for 2020 and 2021** — those editions publish only counts and
  total spend.
- **FIFA revises its own figures.** The 2018 edition sums to USD 7.03bn while the retrospective
  series in the 2025 edition gives 6.93bn for the same year, a 1.4% gap. Transcription follows the
  edition of each year for the age breakdown; the market series comes from the 2025 edition.
- **2016 and 2017 have no club counts here.** In that figure the numbers extract out of order and
  could not be assigned with certainty, so the cells are empty rather than guessed.
- All figures are in **USD**, while source B is in EUR. The two are never added together.

### Privacy check

- [x] No personally identifiable data — aggregates only.
- [x] Publishing derived analysis is standard use of published statistics; the PDFs themselves are
      not redistributed.

---

## Source B: `dcaribou/transfermarkt-datasets`

- **Link:** <https://github.com/dcaribou/transfermarkt-datasets>
- **Publisher:** David Cariboo, an open-source project that scrapes and cleans Transfermarkt.
  The underlying data belongs to **Transfermarkt**, which is where it must be credited.
- **Licence:** **CC0-1.0** (verified via the GitHub licence API, 2026-08-13). Permits any reuse,
  including publication of derived work.
- **Period covered:** transfers dated 1993-07-01 to 2030-06-30 (future dates are pre-agreed moves).
  **Used only over seasons 22/23 to 25/26** — see the survivorship limitation below.
- **Volume:** transfers 175,165 × 10 · players 50,149 × 26 · clubs 796 × 17 · competitions 65 × 11.
- **Downloaded on:** 2026-08-14, via `notebooks/descargar.py`.
- **Saved as:** `datos/crudos/transfermarkt_*_2026-08-14.csv.gz`, with SHA-256 recorded below.

| File | Bytes | SHA-256 |
|---|---|---|
| `transfermarkt_traspasos_1993-2030_2026-08-14.csv.gz` | 5,433,917 | `f295f35af12fe1b7d46ed4f78f66c016c89036b66b16a42be2e11302a4ff7559` |
| `transfermarkt_jugadores_snapshot_2026-08-14.csv.gz` | 4,160,452 | `1457768f75cb27adb38b2227b9c8facc53174a626cbe1e18f9019b5647fa8d3c` |
| `transfermarkt_clubes_snapshot_2026-08-14.csv.gz` | 48,683 | `a6736d4fd85a1e30a86c70fc6ec88b7dbd2d13eefcc486ab8264409f6b2e27c8` |
| `transfermarkt_competiciones_snapshot_2026-08-14.csv.gz` | 2,139 | `226968a488ade41f96ae54b9d2acf5a35a92350c678b9365586d15827e789773` |

The upstream dataset is **refreshed weekly**, so the snapshot is versioned in this repository. Any
reproduction that yields different numbers should compare hashes first: a mismatch means a newer
snapshot, not a bug.

### ROCCC

| Letter | Assessment | Detail |
|---|---|---|
| **R**eliable | Medium | Fees are reported figures, not estimates, and the extremes are plausible (Neymar 222M€, Mbappé 180M€). But coverage is partial and the fee parser collapses loans, free moves and unknown fees to 0 or null. |
| **O**riginal | **Low** | Third party twice over: a scrape of Transfermarkt, which is itself a compiler of publicly reported deals, not the registry of record. |
| **C**omprehensive | High, within its window | Names both clubs, the player, the date, the fee and the date of birth — everything M1–M5 need. |
| **C**urrent | High | Refreshed weekly; covers the window that is open as this is written. |
| **C**ited | High | Public repository with its transformation code visible, explicit licence, documented schema. |

### What it can and cannot answer

- **Can:** who bought from whom, for how much, at what age — the deal-level detail that makes
  concentration and net-seller persistence computable at all.
- **Cannot:** carry a decade. Its history is rebuilt from players present in the base today, so
  coverage thins going backwards **and does so differentially by age**. Any claim about the 2018–19
  shift has to come from source A.

### Declared limitations

- **Survivorship bias, quantified.** Priced deals per season rise from 143 (10/11) to 2,367
  (25/26) while mean age rises 20.8 → 24.4 and the 18–21 share falls 53.8% → 21.2%. None of that
  is football; it is who survives in the base. The series stabilises from 22/23, which is why the
  window starts there.
- **Fee parsing.** Only `fee > 0` rows carry price information: loans, free transfers and unknown
  fees all arrive as 0 or null and cannot be told apart. The analysis population is priced deals.
- **Partial club coverage.** The `clubs` table holds 796 clubs from 65 competitions in 31
  countries. In the window, both clubs are identified in 70.5% of priced deals — but those carry
  93% of the money. Deals with only the buyer identified are cheaper and younger (60.2% aged
  18–23, median 0.5M€ against 2.2M€), so excluding them would strip out exactly the phenomenon
  under study. Hence two declared universes; see `CASO.md` §2.
- **Minors are undercovered.** Under-18s are 0.1–0.4% of spending here against 0.6–1.5% in the
  FIFA census — three to five times less.
- **It is not the census, and does not match it.** Our 18–23 spending share runs 4 to 8 points
  below FIFA's every year. That is expected: FIFA counts only *international* transfers while this
  source also includes domestic ones, and seasons are not calendar years. The consequence is a
  rule, not a caveat: **claims about level come from A, claims about who come from B.**
- **Future-dated transfers.** Rows run to 2030-06-30 (pre-agreed moves); anything after the
  download date is excluded.

### Privacy check

- [x] No sensitive personal data. Player names and dates of birth are published facts about public
      figures, already public on the source site; no contact details, no salaries of private
      individuals.
- [x] CC0-1.0 permits publishing the derived analysis.

---

## How "European" is decided

By the source's own `competitions.confederation` field, where `europa` covers 53 of the 65
competitions across 23 countries. A club is European when its `domestic_competition_id` resolves
to a competition in that confederation.

This was cross-checked against a UEFA membership list built by hand from the 31 countries present
in the data, and the two agree exactly — so the hand-built table was deleted rather than kept as a
second thing to maintain. The eight non-European countries are Argentina, Australia, Brazil,
Japan, South Korea, Mexico, Saudi Arabia and the United States.

Two notes on edge cases the field gets right: England, Scotland and the other UK associations
count separately, as they do in football; and Russia stays European — suspended from competition
since 2022, but its clubs still transfer.
