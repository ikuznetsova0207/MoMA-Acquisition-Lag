"""Load the raw MoMA CSV with the settings its known encoding/dtype quirks require."""

import pandas as pd


def load_raw(path: str = "data/raw/Artworks.csv") -> pd.DataFrame:
    """Read Artworks.csv, handling its UTF-8 BOM and mixed-dtype columns.

    Older pandas versions mangle the first column name without encoding='utf-8-sig'
    (the file starts with a BOM) and raise a DtypeWarning without low_memory=False.
    """
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
