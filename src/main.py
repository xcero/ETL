"""Punto de entrada del ETL Fincas.

Flujo:
  1) Extract: Excel → DataFrame unificado.
  2) Transform: limpieza de texto/UTF-8 y reparación de coordenadas.
  3) Validate: rango geográfico de El Salvador.
  4) Load: inserta catálogo y fincas/observaciones en PostgreSQL.
  5) Export: GeoJSON de puntos para mapa.
"""
from pathlib import Path
import argparse
import pandas as pd
from loguru import logger

from etl.extract.excel_source import read_excel_all_sheets
from etl.transform.cleaning import fix_coordinates
from etl.transform.text_normalize import clean_text
from etl.validate.rules import basic as validate_basic
from etl.load.postgres_loader import upsert_catalogo_municipio, insert_fincas
from etl.load.geojson_export import export_geojson
from utils.logging_conf import logger as _  # activa logging

def main() -> None:
    """Orquesta el pipeline ETL end-to-end."""
    parser = argparse.ArgumentParser(description="ETL Fincas (Excel → PostgreSQL + GeoJSON)")
    parser.add_argument("--excel", required=True, help="Ruta al archivo Excel fuente.")
    parser.add_argument("--export", required=True, help="Ruta destino del GeoJSON.")
    args = parser.parse_args()

    excel_path = Path(args.excel)
    out_geojson = Path(args.export)
    out_geojson.parent.mkdir(parents=True, exist_ok=True)

    # 1) Extract
    df = read_excel_all_sheets(excel_path)

    # 2) Mapear columnas a nombres canónicos si vienen en underscore
    rename_map = {
        "arboles_x_mz": "Arboles x mz",
        "observaciones_sobre_plagas": "Observaciones_sobre_plagas",
        "observaciones_control_plagas": "Observaciones_control_plagas",
        "observaciones_finales": "Observaciones_Finales",
        "fecha_realizacion_del_diagnostico": "Fecha_Realizacion_del_Diagnostico",
    }
    for src, dst in rename_map.items():
        if src in df.columns and dst not in df.columns:
            df[dst] = df[src]
    if "municipio" in df.columns and "Municipio" not in df.columns:
        df["Municipio"] = df["municipio"]

    # 3) Selección de columnas objetivo si existen
    keep = [
        "latitud", "longitud", "altitud", "Arboles x mz",
        "Observaciones_sobre_plagas", "Observaciones_control_plagas",
        "Observaciones_Finales", "Fecha_Realizacion_del_Diagnostico", "Municipio"
    ]
    df = df[[c for c in keep if c in df.columns]].copy()

    # 4) Transform: limpieza de texto + coordenadas
    df = clean_text(df, [c for c in [
        "Observaciones_sobre_plagas","Observaciones_control_plagas",
        "Observaciones_Finales","Municipio"
    ] if c in df.columns])
    df = fix_coordinates(df)

    # 5) Validate
    df = validate_basic(df)

    # 6) Load → PostgreSQL
    try:
        upsert_catalogo_municipio(df)
        insert_fincas(df)
    except Exception as e:
        logger.error(f"Error de carga a PostgreSQL: {e}")
        logger.warning("Continuando con exportación de GeoJSON...")

    # 7) Export GeoJSON
    export_geojson(df, out_geojson)
    logger.info(f"GeoJSON exportado a {out_geojson}")

if __name__ == "__main__":
    main()
