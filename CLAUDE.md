# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup (once)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Place the raw MoMA CSV (not committed — see Data below) at:
#   data/raw/Artworks.csv

# Run a notebook interactively
jupyter notebook

# Execute a notebook headlessly and save its outputs in place (the pattern used
# throughout this project instead of manual "Run All")
jupyter nbconvert --to notebook --execute notebooks/<name>.ipynb --output <name>.ipynb
```

There is no test suite, linter, or build step — this is an exploratory data analysis project; correctness is established by executing notebooks end-to-end and inspecting the printed/verification cells.

## Data

Source: [MoMA/collection](https://github.com/MuseumofModernArt/collection) `Artworks.csv` (~157–160k artworks, 30 raw columns: title, artist, nationality, gender, date, medium, dimensions, classification, department, acquisition info, image URLs).

`data/raw/` and `data/processed/` are gitignored (the raw file is 70MB+). **`data/raw/Artworks.csv` must never be modified or overwritten by any script or notebook** — every notebook reads from `data/raw/` and writes cleaned output only to `data/processed/`. This is the one hard architectural rule in this repo; don't add a script that writes into `data/raw/`.

## Architecture: notebooks as the record of cleaning decisions

The core pattern here is that **notebooks are numbered and build on each other sequentially**, and the markdown cells are not commentary — they are the actual documentation of *why* each cleaning rule was chosen. When extending cleaning logic, follow the same loop already established in `02_data_cleaning.ipynb`: look at real raw examples → state the decision as prose in a markdown cell → implement the smallest function for it → verify against the *full* column (`.unique()`/`.value_counts()`/range check), not just the handful of examples used to write the function. Several real bugs in this dataset were only caught by that verification step (see the notebook's recap table) — don't skip it when adding new columns.

- `notebooks/01_initial_exploration.ipynb` — first-pass profiling of the untouched raw CSV (shape, dtypes, missingness, value counts). No cleaning happens here.
- `notebooks/02_data_cleaning.ipynb` — the cleaning pipeline, step by step, ending by writing `data/processed/artworks_clean.csv`. Each "Step" section documents one column's problem, decision, and verification. Known raw-data quirks already handled here (read before re-deriving them elsewhere):
  - `Gender`, `Nationality`, `BeginDate`, `EndDate` concatenate one `(value)` per artist for multi-artist works, but a few `Gender` entries also contain a *literal* parenthesis inside the description (e.g. `(male (trans? ftm?))`) — the parser splits on `") ("` between artists, not on every `(...)`, to avoid truncating those.
  - `BeginDate`/`EndDate` use `(0)` as a placeholder for missing, not year zero.
  - `Date` (creation date) is free text with three different dash characters for ranges and qualifiers like `"c. 1920"` or `"c. 3000 B.C."`; `extract_year()` takes the first year found in a range and negates B.C. dates.
  - `Classification` uses the string `'(not assigned)'` as a disguised missing value — `.isna()` alone will not catch it.
  - Physical dimension columns (`Weight (kg)`, `Circumference (cm)`, etc.) are 88–100% missing structurally (most works are flat/2D) — this is not a data quality issue and should not be imputed or dropped.
- `src/profiling.py` — `profile_column(df, col)`, the shared diagnostic used before deciding how to clean any column: prints missingness/cardinality, then either the full `value_counts()` (low-cardinality columns) or a random sample (high-cardinality/free-text columns), since `.head()` on this dataset is unrepresentative (the first rows happen to all be Architecture).

Derived columns produced by the cleaning notebook that later analysis should reuse rather than recompute inconsistently: `Gender_primary`, `Nationality_primary`, `BeginYear`, `EndYear`, `Year` (creation year), `AcquisitionYear` (from `DateAcquired`).
