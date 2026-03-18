import pandas as pd
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)


def normalize_column_names(df):
    new_cols = {}
    for col in df.columns:
        cleaned = re.sub(r'[^a-zA-Z0-9]', '_', col.strip())
        cleaned = re.sub(r'_+', '_', cleaned).lower().strip('_')
        new_cols[col] = cleaned
    return df.rename(columns=new_cols)


def fill_missing_values(df, strategy="mean", columns=None):
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    df_filled = df.copy()
    for col in cols:
        if strategy == "mean":
            df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
        elif strategy == "median":
            df_filled[col] = df_filled[col].fillna(df_filled[col].median())
        elif strategy == "zero":
            df_filled[col] = df_filled[col].fillna(0)
        elif strategy == "forward":
            df_filled[col] = df_filled[col].ffill()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    return df_filled


def add_computed_columns(df, computations):
    df_out = df.copy()
    for col_name, formula in computations.items():
        try:
            df_out[col_name] = df_out.eval(formula)
            logger.info(f"Added column '{col_name}' = {formula}")
        except Exception as e:
            logger.error(f"Failed to compute '{col_name}': {e}")
            raise
    return df_out


def bin_column(df, column, bins, labels=None):
    new_col = f"{column}_bin"
    df_out = df.copy()
    df_out[new_col] = pd.cut(df_out[column], bins=bins, labels=labels, include_lowest=True)
    return df_out


class AggregationEngine:
    def __init__(self, df):
        self.df = df
        self._operations = []

    def group_and_agg(self, group_cols, agg_dict):
        result = self.df.groupby(group_cols).agg(agg_dict).reset_index()
        result.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col
                          for col in result.columns]
        self._operations.append({"type": "group_agg", "groups": group_cols})
        return result

    def pivot_table(self, index, columns, values, aggfunc="mean"):
        result = pd.pivot_table(
            self.df, index=index, columns=columns,
            values=values, aggfunc=aggfunc
        ).reset_index()
        self._operations.append({"type": "pivot", "index": index, "columns": columns})
        return result

    def rolling_window(self, column, window_size, func="mean"):
        series = self.df[column]
        if func == "mean":
            result = series.rolling(window=window_size).mean()
        elif func == "sum":
            result = series.rolling(window=window_size).sum()
        elif func == "std":
            result = series.rolling(window=window_size).std()
        else:
            raise ValueError(f"Unsupported rolling function: {func}")
        self._operations.append({"type": "rolling", "column": column, "window": window_size})
        return result

    def get_operations_log(self):
        return self._operations
