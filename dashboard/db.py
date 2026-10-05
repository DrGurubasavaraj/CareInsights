import pandas as pd
import streamlit as st
from sqlalchemy import URL, create_engine, text


@st.cache_resource
def get_engine():
    """Create and cache the PostgreSQL SQLAlchemy engine."""
    cfg = st.secrets["postgres"]

    # Cloud deployments can use a complete provider connection string.
    # Local development can continue using the individual fields below.
    if "url" in cfg:
        database_url = cfg["url"]
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
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
        pool_pre_ping=True,
        pool_recycle=300,
    )


@st.cache_data(ttl=60)
def query_df(sql: str) -> pd.DataFrame:
    """Run a read-only SQL query and return the result as a DataFrame."""
    engine = get_engine()

    with engine.connect() as connection:
        return pd.read_sql_query(text(sql), connection)
