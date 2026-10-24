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

#Estadistica descriptiva
def estadistica_descriptiva(datos: pd.DataFrame) -> dict:
  """Etapa completa de estadistica descriptiva.
 
  Calcula resumenes numericos, frecuencias categoricas, comparaciones por
  grupos y conversion tras anuncios. Guarda cada tabla en resultados/tablas."""
  
  print("--- Iniciando estadistica descriptiva ---")
  datos = datos.copy()
  resultados = {}
 
  # Configuracion de variables
  vars_numericas = [
      "age",
      "months_inactive",
      "music_suggestion_rating_1_to_5",
      "avg_listening_hours_per_week",
      "playlists_created",
      "avg_skips_per_day",
  ]
  vars_categoricas = [
      "country",
      "subscription_type",
      "subscription_status",
      "inactive_3_months_flag",
      "ad_interaction",
      "ad_conversion_to_subscription",
      "favorite_genre",
      "most_liked_feature",
      "desired_future_feature",
      "primary_device",
      "music_suggestion_rating_1_to_5",
      "signup_year",
  ]
  vars_grupo = ["subscription_type", "subscription_status", "primary_device"]
 
  # Variable derivada: año de registro
  fechas = pd.to_datetime(datos["signup_date"], errors="coerce")
  datos["signup_year"] = fechas.dt.year.astype("Int64")
  print(f"Fechas de registro no convertibles: {int(fechas.isna().sum())}")
 
  # 1) Variables numericas: n valido, media, mediana, desv., rango y cuartiles
  filas_num = []
  for col in vars_numericas:
    serie = pd.to_numeric(datos[col], errors="coerce").dropna()
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    n_fuera = int(((serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)).sum())
    filas_num.append({
        "Variable": col,
        "N_validos": int(serie.count()),
        "N_faltantes": int(len(datos) - serie.count()),
        "Media": serie.mean(),
        "Mediana": serie.median(),
        "Desv_Est": serie.std(), 
        "Minimo": serie.min(),
        "Q1": q1,
        "Q3": q3,
        "Maximo": serie.max(),
        "IQR": iqr,
        "N_fuera_Tukey": n_fuera,
        "Pct_fuera_Tukey": round(n_fuera / len(serie) * 100, 2),
    })
  tabla_num = pd.DataFrame(filas_num).round(3)
  print("\nDescriptivos de variables numericas:")
  print(tabla_num.to_string(index=False))
  tabla_num.to_csv(DIR_RESULTADOS_TABLAS / "desc_numericas.csv", index=False)
  resultados["numericas"] = tabla_num
 
  # 2) Variables categoricas: frecuencias y porcentajes
  tablas_cat = []
  for col in vars_categoricas:
    conteo = datos[col].value_counts(dropna=True)
    tablas_cat.append(pd.DataFrame({
        "Variable": col,
        "Categoria": conteo.index.astype(str),
        "Frecuencia": conteo.values,
        "Porcentaje": (conteo.values / conteo.sum() * 100).round(2),
    }))
  tabla_cat = pd.concat(tablas_cat, ignore_index=True)
  print("\nFrecuencias de variables categoricas (se muestran las principales):")
  for var in ["subscription_type", "subscription_status", "primary_device"]:
    print(tabla_cat[tabla_cat["Variable"] == var].to_string(index=False))
  tabla_cat.to_csv(
      DIR_RESULTADOS_TABLAS / "desc_categoricas_frecuencias.csv", index=False
  )
  resultados["categoricas"] = tabla_cat
 
  # 3) Comparacion entre grupos: media, mediana y desv. estandar por grupo
  for grupo in vars_grupo:
    filas_grupo = []
    for categoria, sub in datos.groupby(grupo, observed=True):
      for col in vars_numericas:
        serie = sub[col].dropna()
        filas_grupo.append({
            "Grupo": grupo,
            "Categoria": categoria,
            "Variable": col,
            "N_validos": int(serie.count()),
            "Media": serie.mean(),
            "Mediana": serie.median(),
            "Desv_Est": serie.std(),
        })
    tabla_grupo = pd.DataFrame(filas_grupo).round(3)
    print(f"\nMedias por {grupo}:")
    print(
        tabla_grupo.pivot(index="Categoria", columns="Variable", values="Media")
        .round(2)
        .to_string()
    )
    tabla_grupo.to_csv(
        DIR_RESULTADOS_TABLAS / f"desc_por_{grupo}.csv", index=False
    )
    resultados[f"grupo_{grupo}"] = tabla_grupo
 
  # 4) Conversion a suscripcion tras anuncios, segun tipo de suscripcion
  convirtio = datos["ad_conversion_to_subscription"] == "Yes"
  tabla_conv = (
      convirtio.groupby(datos["subscription_type"])
      .agg(N_usuarios="count", N_convertidos="sum")
      .reset_index()
      .rename(columns={"subscription_type": "Categoria"})
  )
  tabla_conv.insert(0, "Grupo", "subscription_type")
  tabla_conv["Pct_conversion"] = (
      tabla_conv["N_convertidos"] / tabla_conv["N_usuarios"] * 100
  ).round(2)
  print("\nConversion a suscripcion por tipo de suscripcion:")
  print(tabla_conv.to_string(index=False))
  tabla_conv.to_csv(
      DIR_RESULTADOS_TABLAS / "desc_conversion_por_suscripcion.csv", index=False
  )
  resultados["conversion"] = tabla_conv
 
  print("---------------------------------------------\n")
  return resultados

# Carga inicial del dataframe
df = cargar_e_inspeccionar_datos(CSV_PATH)


# DIAGNÓSTICO DE CALIDAD (nadie aun)


# LIMPIEZA Y PREPARACIÓN (fernando)


# ESTADÍSTICA DESCRIPTIVA (joaquin)
resultados_descriptivos = estadistica_descriptiva(df)

# RELACIÓN ENTRE VARIABLES (nadie aun)


# VISUALIZACIÓN DE DATOS (claudio)


# EXPORTACIÓN (nadie aun)


# REPRODUCIBILIDAD (nadie aun)