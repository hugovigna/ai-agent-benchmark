import pandas as pd
import json
import os
import logging

logger = logging.getLogger(__name__)


def load_csv(filepath, separator=",", encoding="utf-8"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    df = pd.read_csv(filepath, sep=separator, encoding=encoding)
    logger.info(f"Loaded {len(df)} rows from {filepath}")
    return df


def load_json(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        return pd.DataFrame(data)
    return data


def merge_datasets(left, right, key, how="inner"):
    result = pd.merge(left, right, on=key, how=how)
    dropped = len(left) + len(right) - len(result)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} rows during merge on '{key}'")
    return result


def filter_by_date(df, column, start_date, end_date):
    df[column] = pd.to_datetime(df[column])
    mask = (df[column] >= start_date) & (df[column] <= end_date)
    filtered = df.loc[mask].copy()
    logger.info(f"Filtered {len(df)} -> {len(filtered)} rows by date range")
    return filtered


class DataValidator:
    def __init__(self, df, rules=None):
        self.df = df
        self.rules = rules or {}
        self.errors = []

    def check_nulls(self, columns=None):
        cols = columns or self.df.columns.tolist()
        for col in cols:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                self.errors.append({"column": col, "issue": "nulls", "count": int(null_count)})
        return self

    def check_duplicates(self, subset=None):
        dupes = self.df.duplicated(subset=subset).sum()
        if dupes > 0:
            self.errors.append({"issue": "duplicates", "count": int(dupes), "subset": subset})
        return self

    def check_range(self, column, min_val, max_val):
        out_of_range = ((self.df[column] < min_val) | (self.df[column] > max_val)).sum()
        if out_of_range > 0:
            self.errors.append({
                "column": column,
                "issue": "out_of_range",
                "count": int(out_of_range),
                "expected": f"[{min_val}, {max_val}]"
            })
        return self

    def get_report(self):
        return {
            "total_rows": len(self.df),
            "total_errors": len(self.errors),
            "details": self.errors
        }
