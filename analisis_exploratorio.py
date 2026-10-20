from pathlib import Path
import sys
import pandas as pd

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATASET_FILENAME = "spotify_user_behavior_realistic_50000_rows.csv"
CSV_PATH = BASE_DIR / DATASET_FILENAME

# Crear carpeta para guardar tablas si no existe
DIR_RESULTADOS_TABLAS = BASE_DIR / "resultados" / "tablas"
DIR_RESULTADOS_TABLAS.mkdir(parents=True, exist_ok=True)


# CARGA E INSPECCIÓN DE DATOS
def cargar_e_inspeccionar_datos(
    ruta_archivo: Path, min_registros: int = 50000
) -> pd.DataFrame:
  print("--- Iniciando carga e inspeccion de datos ---")

  # Verificar si el archivo esta en la ruta
  if not ruta_archivo.exists():
    print(f"Error: no se encontro el archivo en {ruta_archivo}")
    sys.exit(1)

  # Cargar datos probando codificacion
  try:
    try:
      df = pd.read_csv(ruta_archivo, sep=None, engine="python", encoding="utf-8")
    except UnicodeDecodeError:
      print("Aviso: fallo utf-8, intentando con latin1...")
      df = pd.read_csv(
          ruta_archivo, sep=None, engine="python", encoding="latin1"
      )
  except Exception as e:
    print(f"Error al leer el csv: {e}")
    sys.exit(1)

  # Limpiar espacios en los nombres de columnas
  df.columns = df.columns.str.strip()

  filas, columnas = df.shape
  print(f"Dataset cargado: {ruta_archivo.name}")
  print(f"Filas: {filas} | Columnas: {columnas}")

  # Validar cantidad de filas requeridas
  if filas < min_registros:
    print(
        f"Error: el dataset tiene {filas} filas y el minimo pedido es"
        f" {min_registros}."
    )
    sys.exit(1)

  # Revisar si hay columnas de fecha para convertirlas
  columnas_fecha = [
      col
      for col in df.columns
      if any(
          palabra in col.lower() for palabra in ["date", "fecha", "time", "year"]
      )
  ]
  for col_f in columnas_fecha:
    try:
      df[col_f] = pd.to_datetime(df[col_f], errors="ignore")
      print(f"Columna convertida a datetime: {col_f}")
    except Exception:
      pass

  # Resumen de columnas
  tabla_inspeccion = pd.DataFrame({
      "Columna": df.columns,
      "Tipo": df.dtypes.astype(str).values,
      "No_Nulos": df.notnull().sum().values,
      "Completitud_%": ((df.notnull().sum().values / filas) * 100).round(2),
      "Valores_Unicos": df.nunique().values,
  })

  print("\nResumen inicial de columnas:")
  print(tabla_inspeccion.to_string(index=False))

  # Guardar tabla de inspeccion
  ruta_salida_tabla = DIR_RESULTADOS_TABLAS / "inspeccion_columnas_inicial.csv"
  tabla_inspeccion.to_csv(ruta_salida_tabla, index=False)
  print(f"\nTabla guardada en: {ruta_salida_tabla}")

  print("\nPrimeras filas:")
  print(df.head(3))
  print("---------------------------------------------\n")

  return df


# Carga inicial del dataframe
df = cargar_e_inspeccionar_datos(CSV_PATH)


# DIAGNÓSTICO DE CALIDAD (nadie aun)


# LIMPIEZA Y PREPARACIÓN (fernando)


# ESTADÍSTICA DESCRIPTIVA (joaquin)


# RELACIÓN ENTRE VARIABLES (nadie aun)


# VISUALIZACIÓN DE DATOS (claudio)


# EXPORTACIÓN (nadie aun)


# REPRODUCIBILIDAD (nadie aun)