"""Funciones de limpieza y tratamiento de coordenadas.

- Limpieza de espacios en blanco y colapso de espacios múltiples.
- Normalización UTF-8 para valores comunes mal codificados.
- Conversión robusta de números (coma decimal) y reparación de lat/long.
"""
import pandas as pd

def strip_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Aplica `str.strip()` a columnas de texto.

    Args:
        df: DataFrame de entrada.
        cols: Columnas a procesar.
    Returns:
        DataFrame con columnas recortadas.
    """
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

def collapse_spaces(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Colapsa espacios múltiples en un único espacio en columnas de texto.

    Args:
        df: DataFrame de entrada.
        cols: Columnas a procesar.
    Returns:
        DataFrame actualizado.
    """
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.replace(r"\s+", " ", regex=True)
    return df

def normalize_utf8(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Corrige valores UTF-8 comunes mal decodificados (ej. 'CabaÃ±as').

    Args:
        df: DataFrame de entrada.
        cols: Columnas a procesar.
    Returns:
        DataFrame con valores normalizados.
    """
    mapping = {
        "CabaÃ±as": "Cabañas",
        "MERCEDES UMA�A": "MERCEDES UMAÑA",
        "AhuachapÃ¡n": "Ahuachapán",
    }
    for c in cols:
        if c in df.columns:
            df[c] = df[c].replace(mapping)
    return df

def parse_numeric(v):
    """Convierte un valor cualquiera a float, manejando coma decimal y vacíos."""
    if pd.isna(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s == "":
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def fix_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Repara y estandariza coordenadas geográficas.

    - Convierte latitud/longitud a float con `parse_numeric`.
    - Fuerza longitudes negativas (hemisferio occidental) si llegan positivas.
    - Detecta y corrige swaps lat/lon por heurística.

    Returns:
        DataFrame con columnas de coordenadas reparadas.
    """
    if "latitud" in df.columns:
        df["latitud"] = df["latitud"].apply(parse_numeric)
    if "longitud" in df.columns:
        df["longitud"] = df["longitud"].apply(parse_numeric)
    # longitudes positivas → negativas (Oeste)
    if "longitud" in df.columns:
        mask_pos = df["longitud"].notna() & (df["longitud"] > 0)
        df.loc[mask_pos, "longitud"] = -df.loc[mask_pos, "longitud"].astype(float)
    # swap lat/lon si lat fuera de rango y lon plausible (<0)
    if "latitud" in df.columns and "longitud" in df.columns:
        lat, lon = df["latitud"], df["longitud"]
        swap_mask = (
            lat.notna() & lon.notna() &
            ((lat < 10) | (lat > 20)) &
            (lon < 0) & (lon > -100)
        )
        df.loc[swap_mask, ["latitud", "longitud"]] = df.loc[swap_mask, ["longitud", "latitud"]].values
    return df
