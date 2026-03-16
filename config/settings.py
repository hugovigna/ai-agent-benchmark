"""Configuration settings for the data pipeline."""

DATABASE = {
    "host": "localhost",
    "port": 5432,
    "name": "analytics_db",
    "schema": "public",
}

PIPELINE = {
    "batch_size": 1000,
    "max_retries": 3,
    "timeout": 300,
    "log_level": "INFO",
}

STORAGE = {
    "output_dir": "/data/output",
    "temp_dir": "/tmp/pipeline",
    "archive_dir": "/data/archive",
}
