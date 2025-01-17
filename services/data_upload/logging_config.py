"""
Configuration for Python logging to Elasticsearch.
"""

import logging
import os
from typing import Dict
from datetime import datetime
from pythonjsonlogger import jsonlogger
import requests

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "elasticsearch")
ELASTIC_PORT = os.getenv("ELASTIC_PORT", "9200")

class ElasticsearchLogHandler(logging.Handler):
    """
    A simple log handler that sends logs to Elasticsearch via the REST API.
    TODO: handle exceptions, buffering, and async?
    """

    def __init__(self, index_name: str = "python-logs"):
        super().__init__()
        self.index_name = index_name
        self.url = f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        doc = {
            "@timestamp": datetime.utcnow().isoformat(),
            "message": log_entry,
            "logger": record.name,
            "level": record.levelname,
        }

        try:
            requests.post(
                f"{self.url}/{self.index_name}/_doc",
                json=doc,
                timeout=2
            )
        except Exception as e:
            # TODO: Add proper error handling for production
            print(f"Failed to send log to Elasticsearch: {e}")

def get_logger(service_name: str) -> logging.Logger:
    """
    Returns a logger configured to send JSON logs to Elasticsearch.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if get_logger is called more than once
    if not logger.handlers:
        handler = ElasticsearchLogHandler(index_name="python-logs")
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
