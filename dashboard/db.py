import pandas as pd
import streamlit as st
from sqlalchemy import URL, create_engine, text


@st.cache_resource
def get_engine():
    """Create and cache the PostgreSQL SQLAlchemy engine."""
    cfg = st.secrets["postgres"]

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=cfg["username"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["database"],
    )

    return create_engine(
        url,
        pool_pre_ping=True,
    )


@st.cache_data(ttl=60)
def query_df(sql: str) -> pd.DataFrame:
    """Run a read-only SQL query and return the result as a DataFrame."""
    engine = get_engine()

    with engine.connect() as connection:
        return pd.read_sql_query(text(sql), connection)
