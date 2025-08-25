"""Exportación de DataFrame a GeoJSON de puntos (WGS84)."""
import json
import pandas as pd

PROPS = [
    "Municipio", "altitud", "Arboles x mz",
    "Observaciones_sobre_plagas", "Observaciones_control_plagas",
    "Observaciones_Finales", "Fecha_Realizacion_del_Diagnostico"
]

def df_to_geojson_points(df: pd.DataFrame) -> dict:
    """Convierte un DataFrame a FeatureCollection de puntos.

    Serializa fechas a texto ISO si es necesario.
    """
    feats = []
    for _, r in df.iterrows():
        lat, lon = r.get("latitud"), r.get("longitud")
        if pd.isna(lat) or pd.isna(lon):
            continue
        props = {k: r.get(k) for k in PROPS if k in df.columns}
        # Fechas a ISO
        if "Fecha_Realizacion_del_Diagnostico" in props:
            props["Fecha_Realizacion_del_Diagnostico"] = str(props["Fecha_Realizacion_del_Diagnostico"])
        feat = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": props,
        }
        feats.append(feat)
    return {"type": "FeatureCollection", "features": feats}

def export_geojson(df: pd.DataFrame, path: str) -> None:
    """Escribe un GeoJSON a disco con `ensure_ascii=False` para UTF-8."""
    gj = df_to_geojson_points(df)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gj, f, ensure_ascii=False)
