"""Prueba local del ETL sin dependencia de PostgreSQL.

Uso:
    python -m tests.test_local_run --excel ./data/Productores_2022_2023_2024.xlsx --export ./export/fincas.geojson
"""
from pathlib import Path
import argparse
from loguru import logger
from etl.extract.excel_source import read_excel_all_sheets
from etl.transform.cleaning import fix_coordinates
from etl.transform.text_normalize import clean_text
from etl.validate.rules import basic as validate_basic
from etl.load.geojson_export import export_geojson

def main() -> None:
    parser = argparse.ArgumentParser(description="Test local ETL (sin DB)")
    parser.add_argument("--excel", required=True)
    parser.add_argument("--export", required=True)
    args = parser.parse_args()
    excel_path = Path(args.excel)
    out_geojson = Path(args.export)
    out_geojson.parent.mkdir(parents=True, exist_ok=True)

    df = read_excel_all_sheets(excel_path)
    # Mapear columnas canónicas
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
    # Selección
    keep = ["latitud","longitud","altitud","Arboles x mz",
            "Observaciones_sobre_plagas","Observaciones_control_plagas",
            "Observaciones_Finales","Fecha_Realizacion_del_Diagnostico","Municipio"]
    df = df[[c for c in keep if c in df.columns]].copy()
    # Limpieza
    df = clean_text(df, [c for c in ["Observaciones_sobre_plagas","Observaciones_control_plagas",
                                     "Observaciones_Finales","Municipio"] if c in df.columns])
    df = fix_coordinates(df)
    # Validación
    df = validate_basic(df)
    # Export
    export_geojson(df, out_geojson)
    logger.info(f"OK - GeoJSON exportado a {out_geojson}")

if __name__ == "__main__":
    main()
