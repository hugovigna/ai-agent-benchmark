"""Configuration settings for the data pipeline."""

DATABASE = {
    "host": "prod-db.company.internal",
    "port": 5432,
    "name": "analytics_prod",
    "schema": "public",
    "pool_size": 10,
    "max_overflow": 20,
}

PIPELINE = {
    "batch_size": 5000,
    "max_retries": 5,
    "timeout": 600,
    "log_level": "WARNING",
    "enable_profiling": True,
}

STORAGE = {
    "output_dir": "/data/output",
    "temp_dir": "/tmp/pipeline",
    "archive_dir": "/data/archive",
}
