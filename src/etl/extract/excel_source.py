"""Módulo de extracción desde Excel.

Lee todas las hojas de un archivo Excel y devuelve un DataFrame unificado
con nombres de columnas normalizados (lowercase, underscores).
"""
from pathlib import Path
import pandas as pd

def read_excel_all_sheets(xlsx_path: str | Path) -> pd.DataFrame:
    """Lee todas las hojas del Excel y concatena en un único DataFrame.

    Args:
        xlsx_path: Ruta al archivo XLSX.
    Returns:
        DataFrame unificado con columnas normalizadas.
    """
    xlsx_path = Path(xlsx_path)
    xls = pd.ExcelFile(xlsx_path)
    frames = [xls.parse(sheet) for sheet in xls.sheet_names]
    df_all = pd.concat(frames, ignore_index=True)
    df_all.columns = (
        df_all.columns
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.lower()
    )
    return df_all
