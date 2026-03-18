"""Configuration settings for the data pipeline."""

import os

DATABASE = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "name": os.getenv("DB_NAME", "analytics"),
}

PIPELINE = {
    "batch_size": 5000,
    "max_retries": 3,
    "timeout_seconds": 300,
    "output_dir": "data/output",
    "checkpoint_dir": "data/checkpoints",
}

LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
}
