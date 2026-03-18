import pandas as pd
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def export_csv(df, filepath, index=False):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=index)
    logger.info(f"Exported {len(df)} rows to {filepath}")
    return filepath


def export_json(data, filepath, orient="records"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if isinstance(data, pd.DataFrame):
        data.to_json(filepath, orient=orient, indent=2)
    else:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
    logger.info(f"Exported JSON to {filepath}")
    return filepath


def export_parquet(df, filepath, compression="snappy"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath, compression=compression, index=False)
    logger.info(f"Exported {len(df)} rows to parquet: {filepath}")
    return filepath


def generate_summary_report(df, output_path):
    report = {
        "generated_at": datetime.now().isoformat(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": {},
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }
    for col in df.columns:
        col_info = {"dtype": str(df[col].dtype), "null_count": int(df[col].isnull().sum())}
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                "mean": round(float(df[col].mean()), 4),
                "std": round(float(df[col].std()), 4),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            })
        elif pd.api.types.is_string_dtype(df[col]):
            col_info["unique_count"] = int(df[col].nunique())
            col_info["top_values"] = df[col].value_counts().head(5).to_dict()
        report["columns"][col] = col_info
    return export_json(report, output_path)


class BatchExporter:
    def __init__(self, base_dir, batch_size=10000):
        self.base_dir = base_dir
        self.batch_size = batch_size
        self.exported_files = []

    def export_in_batches(self, df, prefix="batch"):
        total_batches = (len(df) + self.batch_size - 1) // self.batch_size
        for i in range(total_batches):
            start = i * self.batch_size
            end = min(start + self.batch_size, len(df))
            batch_df = df.iloc[start:end]
            filepath = os.path.join(self.base_dir, f"{prefix}_{i:04d}.csv")
            export_csv(batch_df, filepath)
            self.exported_files.append(filepath)
            logger.info(f"Batch {i+1}/{total_batches}: {len(batch_df)} rows -> {filepath}")
        return self.exported_files

    def get_manifest(self):
        return {
            "base_dir": self.base_dir,
            "batch_size": self.batch_size,
            "total_files": len(self.exported_files),
            "files": self.exported_files
        }
