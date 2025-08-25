"""Configuración de logging (loguru) para el proyecto ETL Fincas."""
from loguru import logger
from pathlib import Path

# Directorio de logs
Path("logs").mkdir(exist_ok=True)
# Archivo rotativo por día
logger.add("logs/etl_{time:YYYYMMDD}.log", rotation="1 day", retention="14 days", enqueue=True)
