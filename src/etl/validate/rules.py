"""Reglas de validación para garantizar integridad mínima del dataset."""
import pandas as pd
from loguru import logger
from config.settings import BoundsSV

def basic(df: pd.DataFrame) -> pd.DataFrame:
    """Valida existencia y rango de coordenadas para El Salvador.

    - Exige columnas 'latitud' y 'longitud'.
    - Filtra registros fuera de rango aproximado del país.

    Args:
        df: DataFrame a validar.
    Returns:
        DataFrame filtrado a registros válidos.
    Raises:
        ValueError: si faltan columnas críticas o el DF está vacío.
    """
    if df.empty:
        raise ValueError("DataFrame vacío después de extracción.")
    required = {"latitud", "longitud"}
    if not required.issubset(df.columns):
        raise ValueError("Faltan columnas 'latitud' y/o 'longitud'.")
    mask = (
        df["latitud"].between(BoundsSV.LAT_MIN, BoundsSV.LAT_MAX, inclusive="both") &
        df["longitud"].between(BoundsSV.LON_MIN, BoundsSV.LON_MAX, inclusive="both")
    )
    dropped = (~mask).sum()
    if dropped:
        logger.warning(f"Se descartan {dropped} filas fuera de El Salvador.")
    return df.loc[mask].copy()
