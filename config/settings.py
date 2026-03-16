"""Configuration settings for the data pipeline.

Organized by concern: database, pipeline execution, storage, monitoring.
"""

# -- Database Configuration --
DATABASE = {
    "host": "localhost",
    "port": 5432,
    "database_name": "analytics_db",
    "schema": "public",
    "connection_timeout": 30,
}

# -- Pipeline Execution --
PIPELINE = {
    "batch_size": 2000,
    "max_retries": 3,
    "timeout_seconds": 300,
    "log_level": "INFO",
    "parallel_workers": 4,
}

# -- Storage Paths --
STORAGE = {
    "output_dir": "/data/output",
    "temp_dir": "/tmp/pipeline",
    "archive_dir": "/data/archive",
    "retention_days": 90,
}

# -- Monitoring --
MONITORING = {
    "enabled": True,
    "metrics_port": 9090,
    "health_check_interval": 30,
    "export_format": "prometheus",
}

# -- Alerting --
ALERTING = {
    "enabled": True,
    "channels": ["slack", "email"],
    "error_threshold": 5,
    "latency_threshold_ms": 5000,
}
