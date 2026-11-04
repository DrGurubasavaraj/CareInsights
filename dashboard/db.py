import pandas as pd
import streamlit as st
from sqlalchemy import URL, create_engine, text


def _force_psycopg2(database_url: str) -> str:
    """Normalize PostgreSQL URLs so SQLAlchemy always uses psycopg2."""
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace(
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            1,
        )

    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1,
        )

    if database_url.startswith("postgres://"):
        return database_url.replace(
            "postgres://",
            "postgresql+psycopg2://",
            1,
        )

    return database_url


@st.cache_resource
def get_engine():
    """Create and cache the PostgreSQL SQLAlchemy engine."""
    cfg = st.secrets["postgres"]

    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
        "connect_args": {"connect_timeout": 10},
    }

    # Cloud deployments can use a complete provider connection string.
    # Force psycopg2 so deployment does not depend on psycopg v3.
    if "url" in cfg:
        database_url = _force_psycopg2(cfg["url"])
        return create_engine(
            database_url,
            **engine_kwargs,
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=cfg["username"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["database"],
        query={"sslmode": cfg.get("sslmode", "prefer")},
    )

    return create_engine(
        url,
        **engine_kwargs,
    )


@st.cache_data(ttl=60)
def query_df(sql: str) -> pd.DataFrame:
    """Run a read-only SQL query and return the result as a DataFrame."""
    engine = get_engine()

    with engine.connect() as connection:
        return pd.read_sql_query(text(sql), connection)
