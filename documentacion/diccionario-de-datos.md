<!-- Phase 2 deliverable. Only the columns this case actually uses are documented:
     a dictionary of 60 unused columns is a dictionary nobody reads. -->

# Data dictionary — the football transfer market

Figures in **EUR** come from source B, figures in **USD** from source A. They are never added
together.

---

## Source B — `transfermarkt_traspasos_1993-2030_2026-08-14.csv.gz`

One row = one transfer of one player between two clubs. 175,165 rows.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `player_id` | integer | — | — | Transfermarkt player identifier. Joins to `jugadores`. | none |
| `player_name` | text | — | — | Player display name. | none |
| `transfer_date` | date | — | 1993-07-01 to 2030-06-30 | Date the move takes effect. Dates after the download are pre-agreed future moves and are excluded. | none |
| `transfer_season` | text | — | `93/94` … `27/28` | Season label, running 1 July to 30 June. The analysis window is `22/23`–`25/26`. | none |
| `from_club_id` | integer | — | — | Selling club. Joins to `clubes`; resolves for 72% of priced deals in the window. | none |
| `to_club_id` | integer | — | — | Buying club. Resolves for 85% of priced deals in the window. | none |
| `from_club_name` / `to_club_name` | text | — | — | Club names as scraped. Present even when the id does not resolve to the `clubes` table. | none |
| `transfer_fee` | decimal | EUR | ≥ 0 or null | Fee paid. **Only `> 0` carries price information:** upstream, loans, free transfers and unrecorded fees all collapse to 0 or null and cannot be told apart. 17,554 of 175,165 rows are positive. | 61,526 null, 96,085 zero |
| `market_value_in_eur` | decimal | EUR | ≥ 0 or null | Transfermarkt's community-estimated value at the time of the move. **Reference only, never a price** — it reacts to transfer rumours, so any fee-to-value ratio would partly measure its own input. Out of scope per §1. | 68,160 null |

## Source B — `transfermarkt_jugadores_snapshot_2026-08-14.csv.gz`

One row = one player. 50,149 rows, 26 columns; those used:

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `player_id` | integer | — | — | Join key to `traspasos`. | none |
| `date_of_birth` | timestamp | — | — | Basis for age: **completed years at `transfer_date`**. | 2 of 17,554 priced deals |
| `position` | text | — | Goalkeeper, Defender, Midfield, Attack | Broad position. | some |
| `sub_position` | text | — | e.g. Left Winger, Centre-Back | Detailed position. | some |
| `country_of_citizenship` | text | — | — | Nationality. Not used to decide whether a transfer is European — **club country decides that, not the player's passport**. | some |
| `last_season` | integer | — | e.g. 2025 | Last season the player appears in the base. Used to measure survivorship bias, not in any metric. | none |

## Source B — `transfermarkt_clubes_snapshot_2026-08-14.csv.gz`

One row = one club. 796 rows.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `club_id` | integer | — | — | Join key from `from_club_id` / `to_club_id`. | none |
| `name` | text | — | — | Club name. | none |
| `domestic_competition_id` | text | — | e.g. `GB1`, `ES1` | The club's domestic league. Joins to `competiciones`; this is what makes a club European. | none |

## Source B — `transfermarkt_competiciones_snapshot_2026-08-14.csv.gz`

One row = one competition. 65 rows.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `competition_id` | text | — | e.g. `GB1` | Join key from `clubes`. | none |
| `country_name` | text | — | 31 countries | Country of the competition. | 12 (international competitions) |
| `confederation` | text | — | `europa`, `amerika`, `asien`, `afrika`, `fifa` | **Defines the European universe:** a club is European when its competition is `europa` (53 of 65 competitions, 23 countries). | none |
| `type` | text | — | `domestic_league`, `domestic_cup`, `international_cup`, … | Competition type. | none |

---

## Source A — `fifa_edad_2018-2025_2026-08-14.csv`

One row = one year × one age band, transcribed by hand from the FIFA Global Transfer Report.
36 rows. **Not every edition publishes every column** — blanks are what that edition does not
report, never a zero.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `year` | integer | — | 2018–2025 | Calendar year, not season. | none |
| `age_band` | text | — | `<18`, `18-23`, `24-29`, `30-35`, `>35`, `>=30` | Editions up to 2021 split 30–35 and >35; from 2022 they merge into `>=30`. Sum the two old bands to compare across the change. | none |
| `transfers_total` | integer | count | — | All international transfers in the band, with or without a fee. | 2022, 2023 |
| `transfers_with_fee` | integer | count | — | Transfers carrying a fee. | 2018–2021, 2024, 2025 |
| `pct_with_fee` | decimal | % | 0–100 | Share of the band's transfers that carried a fee. | 2020–2023 |
| `total_fee_usd_m` | decimal | USD million | ≥ 0 | Total spend on the band. | 2024, 2025 (derivable) |
| `avg_fee_usd_m` | decimal | USD million | ≥ 0 | Average fee per priced transfer. | 2020–2023 |
| `edition`, `figure`, `page` | text | — | — | Where the number came from. This is what makes a manual transcription auditable. | none |

Spend is available for all eight years either directly or as
`transfers_total × pct_with_fee ÷ 100 × avg_fee_usd_m`. Cross-checked against the market series:
the two agree within −0.6% to +1.4% every year.

## Source A — `fifa_mercado_2016-2025_2026-08-14.csv`

One row = one year. 10 rows, all from the 2025 edition, figures 1 and 2, page 7.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| `year` | integer | — | 2016–2025 | Calendar year. | none |
| `total_fee_usd_bn` | decimal | USD billion | ≥ 0 | Global spend on international transfer fees. | none |
| `transfers_total` | integer | count | — | International transfers in men's professional football. | none |
| `pct_with_fee` | decimal | % | 0–100 | Share carrying a fee. | none |
| `clubs_paying` | integer | count | — | Clubs that paid at least one fee. | 2016, 2017 |
| `clubs_receiving` | integer | count | — | Clubs that received at least one fee. | 2016, 2017 |

`clubs_paying` and `clubs_receiving` are the census-level version of the buyer/seller axis: how
many clubs are on each side of the market each year.

---

## Derived fields (computed, not stored)

| Field | Definition |
|---|---|
| `edad` | `date_diff('year', date_of_birth, transfer_date)` — completed years at the transfer date. |
| `es_europeo` | true when either club's competition has `confederation = 'europa'`. |
| **U1** | Priced deals where **at least one** club is identified and European. Basis for M3, M4, M5. |
| **U2** | Priced deals where **both** clubs are identified and at least one is European. Basis for M1, M2, which need to attribute spend to a named club. |
