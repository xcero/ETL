"""Carga a PostgreSQL: catálogo de municipios, fincas y observaciones.

Nota: requiere `sql/schema.sql` ejecutado previamente.
"""
import pandas as pd
from sqlalchemy import text
from loguru import logger
from config.db import get_engine

def upsert_catalogo_municipio(df: pd.DataFrame) -> None:
    """Inserta municipios únicos en `fincas.cat_municipio` (ON CONFLICT DO NOTHING).

    Args:
        df: DataFrame que contiene la columna opcional 'Municipio'.
    """
    if "Municipio" not in df.columns:
        return
    dfm = df[["Municipio"]].dropna().drop_duplicates().rename(columns={"Municipio": "nombre"})
    if dfm.empty:
        return
    sql = text("""
        INSERT INTO fincas.cat_municipio (nombre)
        VALUES (:nombre)
        ON CONFLICT (nombre) DO NOTHING;
    """)
    with get_engine().begin() as con:
        con.execute(sql, dfm.to_dict(orient="records"))

def insert_fincas(df: pd.DataFrame) -> None:
    """Inserta registros de fincas y observaciones relacionadas.

    - Resuelve FK de municipio por nombre.
    - Inserta en `fincas.finca` y `fincas.finca_obs`.
    """
    with get_engine().begin() as con:
        # Resolver FK municipio
        map_muni = {}
        if "Municipio" in df.columns:
            res = con.execute(text("SELECT municipio_id, nombre FROM fincas.cat_municipio"))
            map_muni = {r.nombre: r.municipio_id for r in res}
            df["municipio_id"] = df["Municipio"].map(map_muni)
        rows_finca = df[[
            "municipio_id", "latitud", "longitud", "altitud",
            "Arboles x mz", "Fecha_Realizacion_del_Diagnostico"
        ]].rename(columns={
            "Arboles x mz": "arboles_x_mz",
            "Fecha_Realizacion_del_Diagnostico": "fecha_diagnostico",
        })
        sql_finca = text("""
            INSERT INTO fincas.finca (municipio_id, latitud, longitud, altitud, arboles_x_mz, fecha_diagnostico)
            VALUES (:municipio_id, :latitud, :longitud, :altitud, :arboles_x_mz, :fecha_diagnostico)
            RETURNING finca_id
        """)
        finca_ids = []
        for rec in rows_finca.to_dict(orient="records"):
            rid = con.execute(sql_finca, rec).scalar()
            finca_ids.append(rid)
        # Observaciones
        obs_cols = [
            "Observaciones_sobre_plagas", "Observaciones_control_plagas", "Observaciones_Finales"
        ]
        if any(c in df.columns for c in obs_cols):
            df_obs = df[obs_cols].copy()
            df_obs["finca_id"] = finca_ids
            sql_obs = text("""
                INSERT INTO fincas.finca_obs (finca_id, obs_plagas, obs_control_plagas, obs_finales)
                VALUES (:finca_id, :Observaciones_sobre_plagas, :Observaciones_control_plagas, :Observaciones_Finales)
            """)
            con.execute(sql_obs, df_obs.to_dict(orient="records"))
        logger.info(f"Insertadas {len(finca_ids)} fincas.")
