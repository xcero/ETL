"""Parámetros globales y límites geográficos para validación."""
from dataclasses import dataclass

@dataclass(frozen=True)
class BoundsSV:
    """Rango aproximado de El Salvador para validar coordenadas."""
    LAT_MIN: float = 10.0
    LAT_MAX: float = 20.0
    LON_MIN: float = -90.5
    LON_MAX: float = -87.5
