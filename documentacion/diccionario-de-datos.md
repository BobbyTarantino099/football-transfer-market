<!-- Phase 2 deliverable. Mark with ★ the columns the analysis actually uses: it is what
     lets a reader tell the working set apart from the noise in a 40-column table. -->

# Data dictionary — <SOURCE NAME>

**File:** `datos/crudos/<file>.csv` — <N> rows × <N> columns
**Unit of observation:** 1 row = <what exactly>

★ = column used by the analysis.

| Column | Type | Unit | Allowed values | Meaning | Nulls |
|---|---|---|---|---|---|
| <name> ★ | <integer/decimal/text/date/categorical> | <unit or —> | <range or set> | <what it measures> | <%> |

## Derived columns

<Columns that do not exist in the raw data and are created in `procesar.py`. Each one states
the formula, so the reader can reproduce it without opening the script.>

| Column | Formula | Unit | Created in |
|---|---|---|---|
| <name> | `<formula>` | <unit> | `notebooks/procesar.py` |
