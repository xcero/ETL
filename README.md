# ETL Fincas (Excel → PostgreSQL + GeoJSON)

Proyecto modular de ETL para cargar información de fincas desde Excel a PostgreSQL
y generar un GeoJSON de puntos para visualización (GitHub Pages / Google Sites).

## Objetivo
- **Fuente**: Excel del Plan de FINCA con las columnas:
  `latitud`, `longitud`, `altitud`, `Arboles x mz`, 
  `Observaciones_sobre_plagas`, `Observaciones_control_plagas`, 
  `Observaciones_Finales`, `Fecha_Realizacion_del_Diagnostico`, (opcional `Municipio`).
- **Destino**: PostgreSQL (esquema `fincas`) con tablas normalizadas.
- **Salida**: GeoJSON de puntos `export/fincas.geojson` para un mapa ligero (Leaflet).

## Estructura
```
etl_fincas_project/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ sql/
│  └─ schema.sql
├─ config/
│  ├─ db.py
│  └─ settings.py
├─ src/
│  ├─ main.py
│  ├─ etl/
│  │  ├─ extract/excel_source.py
│  │  ├─ transform/cleaning.py
│  │  ├─ transform/text_normalize.py
│  │  ├─ validate/rules.py
│  │  └─ load/{postgres_loader.py, geojson_export.py}
│  └─ utils/{logging_conf.py}
├─ dashboards/
│  └─ map_stub.html
├─ data/ (colocar Excel aquí)
└─ export/ (salidas GeoJSON/CSV)
```

## Requisitos
- Python 3.10+
- PostgreSQL 14+ (o compatible)
- Paquetes: ver `requirements.txt`

## Instalación rápida
```bash
pip install -r requirements.txt
cp .env.example .env  # Ajusta credenciales
psql -h $PG_HOST -U $PG_USER -d $PG_DB -f sql/schema.sql
```

## Ejecución del ETL
```bash
# Copia tu Excel a data/ con nombre Productores_2022_2023_2024.xlsx
python -m src.main --excel ./data/Productores_2022_2023_2024.xlsx --export ./export/fincas.geojson
```

- El script:
  1) **Extract**: lee todas las hojas y unifica.
  2) **Transform**: limpia espacios, normaliza UTF-8 (ej. *Cabañas*), repara coordenadas (coma decimal, signo, swap).
  3) **Validate**: asegura coordenadas en rango de El Salvador.
  4) **Load**: upsert de catálogo de municipios + inserciones en `finca` y `finca_obs`.
  5) **Export**: genera `GeoJSON` de puntos.

## Visualización rápida (Leaflet)
- Abre `dashboards/map_stub.html` y ajusta la ruta del GeoJSON si es necesario.
- Publica `export/fincas.geojson` en tu repo (GitHub Pages) o embébelo en Google Sites.

## Pruebas locales (sin DB)
```bash
python -m tests.test_local_run --excel ./data/Productores_2022_2023_2024.xlsx --export ./export/fincas.geojson
```

## Notas de diseño
- Campos de texto con `strip` + colapso de espacios + mapeos UTF‑8 comunes.
- Coordenadas robustas: soporta `,` como decimal, asegura longitudes negativas y auto-swap lat/lon cuando aplica.
- Si activas PostGIS, puedes generar `geom` en DB; por ahora el proyecto exporta GeoJSON.
