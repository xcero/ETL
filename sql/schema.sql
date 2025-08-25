CREATE SCHEMA IF NOT EXISTS fincas;

CREATE TABLE IF NOT EXISTS fincas.cat_municipio (
  municipio_id SERIAL PRIMARY KEY,
  nombre VARCHAR(80) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS fincas.finca (
  finca_id BIGSERIAL PRIMARY KEY,
  municipio_id INT NULL REFERENCES fincas.cat_municipio(municipio_id),
  latitud DOUBLE PRECISION NOT NULL,
  longitud DOUBLE PRECISION NOT NULL,
  altitud DOUBLE PRECISION NULL,
  arboles_x_mz INTEGER NULL,
  fecha_diagnostico DATE NULL
);

CREATE TABLE IF NOT EXISTS fincas.finca_obs (
  finca_id BIGINT REFERENCES fincas.finca(finca_id),
  obs_plagas TEXT NULL,
  obs_control_plagas TEXT NULL,
  obs_finales TEXT NULL
);
