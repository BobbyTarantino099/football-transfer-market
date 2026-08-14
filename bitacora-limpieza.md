<!-- Phase 3 deliverable. Raw data is NEVER modified in place: every transformation
     produces a new file and is logged here. Written as you clean, not afterwards. -->

# Cleaning log — <CASE NAME>

**Input dataset:** `datos/crudos/<file>.csv` — <N> rows
**Output datasets:**
- `datos/limpios/<file>.csv` — <N> rows (1 row = <unit of observation>)

**Tool:** <Python (pandas) / SQL / spreadsheet>, justified in Phase 0: <why this one and not
another — volume, reproducibility, the kind of flaw found>.

Full script: `notebooks/procesar.py`.

## Transformations

<One entry per transformation, numbered T1, T2… Each answers the same five questions.
The "alternative discarded" line is the one that makes this log evidence rather than a
changelog: it shows the cleaning was reasoned, not reflexive.>

### T1 — <what was fixed, in a few words>
- **What:** <the observable problem in the data>
- **Why:** <what breaks downstream if it is not fixed>
- **How:** <the concrete operation, with the parameters that matter>
- **Rows affected:** <N, and out of how many>
- **Alternative discarded:** <what else could have been done, and why it wasn't>

## Integrity checks after cleaning

| Check | Expected | Result |
|---|---|---|
| Rows in vs rows out | <N in − N excluded> | |
| Duplicate keys | 0 | |
| Nulls in the key columns | 0 | |
| Values out of range | 0 | |
