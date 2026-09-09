"""Column-level diagnostics: run structured checks instead of scrolling through raw rows."""

import pandas as pd


def profile_column(df: pd.DataFrame, col: str, n_samples: int = 10) -> None:
    """Print a quick diagnostic for one column: missingness, cardinality,
    top values (if categorical-ish) or a random sample (if not), and dtype.
    """
    s = df[col]
    n = len(s)
    n_missing = s.isna().sum()
    n_unique = s.nunique(dropna=True)

    print(f"=== {col} ===")
    print(f"dtype: {s.dtype}")
    print(f"missing: {n_missing} ({n_missing / n:.1%})")
    print(f"unique values: {n_unique}")
    print()

    if pd.api.types.is_numeric_dtype(s):
        print(s.describe())
    elif n_unique <= 50:
        # low cardinality: show the whole distribution, not just the top few —
        # that's where near-duplicate categories and malformed outliers hide
        print(s.value_counts(dropna=False))
    else:
        # high cardinality / free text: a random sample beats .head(), which
        # only shows whatever happened to be first in the raw file
        print(f"(too many unique values to list — random sample of {n_samples})")
        print(s.dropna().sample(min(n_samples, n_unique), random_state=1).tolist())
