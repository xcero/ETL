"""Conexión a PostgreSQL con SQLAlchemy.

Lee credenciales desde `.env` y expone `get_engine()`
para obtener un engine reutilizable con pool pre_ping.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "fincas")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")

def pg_url() -> str:
    """Construye la URL de conexión de PostgreSQL (psycopg2)."""
    return f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

def get_engine():
    """Devuelve un engine con pool_pre_ping para conexiones saludables."""
    return create_engine(pg_url(), pool_pre_ping=True)
