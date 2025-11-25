"""
Configuration helpers for external services (Phase 3+ hardening).

Reads connection info from environment variables. In production, inject via
secret managers, not hardcoded defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class PostgresConfig:
    dsn: str


@dataclass
class VectorDBConfig:
    url: str
    api_key: str | None = None


@dataclass
class GraphDBConfig:
    uri: str
    user: str | None = None
    password: str | None = None


def load_postgres_config() -> PostgresConfig:
    dsn = os.getenv("POSTGRES_DSN", "postgresql://user:pass@localhost:5432/industriverse")
    return PostgresConfig(dsn=dsn)


def load_vector_config() -> VectorDBConfig:
    return VectorDBConfig(
        url=os.getenv("VECTOR_DB_URL", "http://localhost:6333"),
        api_key=os.getenv("VECTOR_DB_API_KEY"),
    )


def load_graph_config() -> GraphDBConfig:
    return GraphDBConfig(
        uri=os.getenv("GRAPH_DB_URI", "bolt://localhost:7687"),
        user=os.getenv("GRAPH_DB_USER"),
        password=os.getenv("GRAPH_DB_PASSWORD"),
    )
