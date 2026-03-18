"""Data transformation: cleaning, enrichment, and feature engineering."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Callable, Optional

from src.models import BatchResult

logger = logging.getLogger(__name__)


def clean_dataframe(df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
    """Remove nulls and duplicates from a DataFrame."""
    initial = len(df)
    df = df.dropna(how="all")
    if drop_duplicates:
        df = df.drop_duplicates()
    logger.info(f"Cleaning: {initial} -> {len(df)} rows")
    return df.reset_index(drop=True)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and snake_case all column names."""
    import re
    new_names = {}
    for col in df.columns:
        name = re.sub(r"[^a-zA-Z0-9]", "_", col.strip()).lower()
        name = re.sub(r"_+", "_", name).strip("_")
        new_names[col] = name
    return df.rename(columns=new_names)


def apply_transformations(df: pd.DataFrame, transforms: Dict[str, Callable]) -> pd.DataFrame:
    """Apply a dict of {column: function} transformations."""
    result = df.copy()
    for col, func in transforms.items():
        if col in result.columns:
            result[col] = result[col].apply(func)
            logger.info(f"Applied transform to column '{col}'")
    return result


def add_features(df: pd.DataFrame, feature_specs: Dict[str, str]) -> pd.DataFrame:
    """Add computed columns using pandas eval expressions."""
    result = df.copy()
    for name, expr in feature_specs.items():
        result[name] = result.eval(expr)
    return result


class TransformChain:
    """Chain of transformations applied sequentially to a DataFrame."""

    def __init__(self):
        self._steps: List[tuple] = []
        self._results: List[BatchResult] = []

    def add(self, name: str, func: Callable, **kwargs):
        self._steps.append((name, func, kwargs))
        return self

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        current = df
        for name, func, kwargs in self._steps:
            try:
                current = func(current, **kwargs)
                self._results.append(BatchResult(
                    batch_id=name, total=len(df), success=len(current),
                    failed=len(df) - len(current)
                ))
            except Exception as e:
                logger.error(f"Transform '{name}' failed: {e}")
                self._results.append(BatchResult(
                    batch_id=name, total=len(df), success=0,
                    failed=len(df), errors=[str(e)]
                ))
                raise
        return current

    def get_results(self) -> List[BatchResult]:
        return self._results
