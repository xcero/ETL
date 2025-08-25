"""Normalización de texto de campos de observaciones y municipio."""
import pandas as pd
from .cleaning import strip_columns, collapse_spaces, normalize_utf8

TEXT_COLS_DEFAULT = [
    "Observaciones_sobre_plagas",
    "Observaciones_control_plagas",
    "Observaciones_Finales",
    "Municipio",
]

def clean_text(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    """Limpia y normaliza columnas de texto usando helpers.

    Args:
        df: DataFrame de entrada.
        cols: Columnas a limpiar; si None, usa `TEXT_COLS_DEFAULT`.
    Returns:
        DataFrame actualizado.
    """
    cols = cols or TEXT_COLS_DEFAULT
    df = strip_columns(df, cols)
    df = collapse_spaces(df, cols)
    df = normalize_utf8(df, cols)
    return df
