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

#==============DIAGNÓSTICO_DE_CALIDAD==============#

# Variable que setea el formato de la id
COL_ID = "user_id"

# Tipos válidos según columna
TIPOS_VALIDOS = {
    "user_id": "entero",
    "country": "texto",
    "age": "entero",
    "signup_date": "fecha",
    "subscription_type": "texto",
    "subscription_status": "texto",
    "months_inactive": "entero",
    "inactive_3_months_flag": "entero",
    "ad_interaction": "texto",
    "ad_conversion_to_subscription": "texto",
    "music_suggestion_rating_1_to_5": "entero",
    "avg_listening_hours_per_week": "decimal",
    "favorite_genre": "texto",
    "most_liked_feature": "texto",
    "desired_future_feature": "texto",
    "primary_device": "texto",
    "playlists_created": "entero",
    "avg_skips_per_day": "entero",}

# Rangos válidos de datos numéricos
RANGOS_VALIDOS = {
    "age": (13, 100),
    "months_inactive": (0, 120),
    "inactive_3_months_flag": (0, 1),
    "music_suggestion_rating_1_to_5": (1, 5),
    "avg_listening_hours_per_week": (0, 168),  # horas que tiene una semana
    "playlists_created": (0, 1000),
    "avg_skips_per_day": (0, 500),}

# Fecha válida para registro: Desde el lanzamiento de la app hasta la actualidad
FECHA_MINIMA_VALIDA = pd.Timestamp("2008-10-07")
FECHA_MAXIMA_VALIDA = pd.Timestamp.today().normalize()

# Valores válidos en columnas binarias
VALORES_BINARIOS_VALIDOS = {
    "subscription_status": {"Active", "Inactive"},
    "ad_interaction": {"Yes", "No"},
    "ad_conversion_to_subscription": {"Yes", "No"},}

# Datos considerados como nulos/vacíos/faltantes
PLACEHOLDERS = {
    "", "na", "n/a", "nan", "null", "none", "?", "-", "--", "unknown",
    "desconocido",}

def _es_columna_texto(serie: pd.Series) -> bool:
  return serie.dtype == object or pd.api.types.is_string_dtype(serie)

# 1. Verificación de datos faltantes
def valores_faltantes(df: pd.DataFrame) -> pd.DataFrame:
  print("=== 1. Valores faltantes/columna ===")
  filas = len(df)
  registros = []

  for col in df.columns:
    nulos = int(df[col].isnull().sum())

    # Faltantes "falsos": Contienen un valor que no es un dato per se
    placeholders = 0
    if _es_columna_texto(df[col]):
      texto = df[col].dropna().astype(str).str.strip().str.lower()
      placeholders = int(texto.isin(PLACEHOLDERS).sum())

    total = nulos + placeholders
    registros.append({
        "Columna": col,
        "Nulos": nulos,
        "Nulos_%": round(nulos / filas * 100, 2),
        "Vacios_o_Placeholder": placeholders,
        "Total_Faltantes": total,
        "Faltantes_%": round(total / filas * 100, 2),})

  tabla = pd.DataFrame(registros)
  print(tabla.to_string(index=False))

  filas_con_nulos = int(df.isnull().any(axis=1).sum())
  print(f"\nFilas con al menos un nulo: {filas_con_nulos}"
      f" ({filas_con_nulos / filas * 100:.2f}%)")

  ruta = DIR_RESULTADOS_TABLAS / "resultado_valores_faltantes.csv"
  tabla.to_csv(ruta, index=False)
  print(f"Tabla guardada en: {ruta}\n")
  return tabla

# 2. Duplicados e ID's repetidos
def diagnostico_duplicados(
    df: pd.DataFrame, col_id: str = COL_ID
) -> pd.DataFrame:
  print("=== 2. Duplicados vs ID's repetidos ===")
  filas = len(df)

  # 2.1 Duplicados
  mascara_exactos = df.duplicated(keep="first")
  n_exactos = int(mascara_exactos.sum())
  detalle_exactos = df[df.duplicated(keep=False)]

  # 2.2 ID repetido pero no duplicado
  n_ids_variantes = 0
  detalle_variantes = pd.DataFrame()
  if col_id in df.columns:
    repetidos = df[df[col_id].duplicated(keep=False)]
    # Mismo ID, distintos datos
    versiones = repetidos.drop_duplicates().groupby(col_id).size()
    ids_variantes = versiones[versiones > 1].index
    n_ids_variantes = len(ids_variantes)
    detalle_variantes = repetidos[repetidos[col_id].isin(ids_variantes)]
    detalle_variantes = detalle_variantes.sort_values(col_id)
  else:
    print(f"Aviso: no existe la columna '{col_id}', se omite el analisis por id")

  # 2.3 Distinto ID, datos iguales
  n_perfiles_iguales = 0
  detalle_perfiles = pd.DataFrame()
  cols_sin_id = [c for c in df.columns if c != col_id]
  if col_id in df.columns:
    mismo_perfil = df[df.duplicated(subset=cols_sin_id, keep=False)]
    if not mismo_perfil.empty:
      ids_por_perfil = mismo_perfil.groupby(cols_sin_id, dropna=False)[col_id].transform("nunique")
      detalle_perfiles = mismo_perfil[ids_por_perfil > 1]
      n_perfiles_iguales = len(detalle_perfiles)

  resumen = pd.DataFrame([
      {
          "Tipo_Repeticion": "Duplicado",
          "Filas_Afectadas": n_exactos,
          "Porcentaje_%": round(n_exactos / filas * 100, 2),
          "Clasificacion": "Dato inválido: Se debería eliminar",},
      {
          "Tipo_Repeticion": f"Mismo {col_id} con datos distintos",
          "Filas_Afectadas": len(detalle_variantes),
          "Porcentaje_%": round(len(detalle_variantes) / filas * 100, 2),
          "Clasificacion": "Repeticion válida: Revisar",},
      {
          "Tipo_Repeticion": f"Mismos datos, distinto {col_id}",
          "Filas_Afectadas": n_perfiles_iguales,
          "Porcentaje_%": round(n_perfiles_iguales / filas * 100, 2),
          "Clasificacion": "Repeticion válida: Distintos ID's",},])
  print(resumen.to_string(index=False))
  if col_id in df.columns:
    print(
        f"\nID's unicos: {df[col_id].nunique()} de {filas} filas"
        f" | ID's repetidos con distintos datos: {n_ids_variantes}")

  # Exportación de resultados: Duplicados e ID's repetidos
  ruta = DIR_RESULTADOS_TABLAS / "resultado_duplicados.csv"
  resumen.to_csv(ruta, index=False)
  print(f"La tabla se guardó en: {ruta}")

  for nombre, detalle in [
      ("duplicados", detalle_exactos),
      ("id_repetido", detalle_variantes),
      ("datos_repetidos_distinto_id", detalle_perfiles),
  ]:
    if not detalle.empty:
      ruta_detalle = DIR_RESULTADOS_TABLAS / f"detalle_{nombre}.csv"
      detalle.to_csv(ruta_detalle, index=False)
      print(f"La tabla se guardó en: {ruta_detalle}")
  print()
  return resumen

# 3. Valores inválidos
def tipos(df: pd.DataFrame) -> pd.DataFrame:
  print("=== 3. Dato inválido según tipo ===")
  registros = []

  for col in df.columns:
    serie = df[col]
    no_nulos = serie.dropna()
    esperado = TIPOS_VALIDOS.get(col, "sin_regla")
    no_convertibles = 0
    decimales_en_entero = 0
    variantes_texto = 0
    if esperado in ("entero", "decimal"):
      numeros = pd.to_numeric(no_nulos, errors="coerce")
      no_convertibles = int(numeros.isnull().sum())
      if esperado == "entero":
        decimales_en_entero = int((numeros.dropna() % 1 != 0).sum())
      tipo_correcto = pd.api.types.is_numeric_dtype(serie)
    elif esperado == "fecha":
      fechas = pd.to_datetime(no_nulos, errors="coerce")
      no_convertibles = int(fechas.isnull().sum())
      tipo_correcto = pd.api.types.is_datetime64_any_dtype(serie)
    elif esperado == "texto":
      tipo_correcto = _es_columna_texto(serie)
      # Variantes de un mismo valor: "Pop", "pop ", "POP"
      texto = no_nulos.astype(str)
      variantes_texto = int(
          texto.nunique() - texto.str.strip().str.lower().nunique())
    else:
      tipo_correcto = True

    # Datos con más de un tipo
    tipos_mezclados = int(no_nulos.map(type).nunique())
    observaciones = []
    if not tipo_correcto:
      observaciones.append(f"dtype {serie.dtype} no es {esperado}")
    if no_convertibles:
      observaciones.append(f"{no_convertibles} no se pueden convertit")
    if decimales_en_entero:
      observaciones.append(f"{decimales_en_entero} float en integer")
    if tipos_mezclados > 1:
      observaciones.append(f"{tipos_mezclados} más de un tipo")
    if variantes_texto:
      observaciones.append(f"{variantes_texto} variantes de mayúcula o espacio")
    registros.append({
        "Columna": col,
        "Tipo_Actual": str(serie.dtype),
        "Tipo_Esperado": esperado,
        "No_Convertibles": no_convertibles,
        "Decimales_En_Entero": decimales_en_entero,
        "Tipos_Mezclados": tipos_mezclados,
        "Variantes_Texto": variantes_texto,
        "Estado": "REVISAR" if observaciones else "OK",
        "Observacion": "; ".join(observaciones),})

  tabla = pd.DataFrame(registros)
  print(tabla.to_string(index=False))

  ruta = DIR_RESULTADOS_TABLAS / "resultado_tipos.csv"
  tabla.to_csv(ruta, index=False)
  print(f"\nLa tabla se guardó en: {ruta}\n")
  return tabla

# 4. Datos fuera de los rangos establecidos
def diagnostico_rangos(df: pd.DataFrame) -> pd.DataFrame:
  print("=== 4. Valores fuera del rango según dato ===")
  filas = len(df)
  registros = []

  # 4.1 Validación de rangos numéricos 
  for col, (minimo, maximo) in RANGOS_VALIDOS.items():
    if col not in df.columns:
      continue
    numeros = pd.to_numeric(df[col], errors="coerce")
    fuera = int(((numeros < minimo) | (numeros > maximo)).sum())
    lim_sup = numeros.mean() + 2 * numeros.std()
    lim_inf = numeros.mean() - 2 * numeros.std()
    atipicos = int(((numeros > lim_sup) | (numeros < lim_inf)).sum())
    registros.append({
        "Columna": col,
        "Regla": f"[{minimo}, {maximo}]",
        "Fuera_Rango": fuera,
        "Fuera_Rango_%": round(fuera / filas * 100, 2),
        "Min_Observado": numeros.min(),
        "Max_Observado": numeros.max(),
        "Atipicos_2std": atipicos,})

  # 4.2 Validación de fechas límite establecidas
  for col, tipo in TIPOS_VALIDOS.items():
    if tipo != "fecha" or col not in df.columns:
      continue
    fechas = pd.to_datetime(df[col], errors="coerce")
    fuera = int(((fechas < FECHA_MINIMA_VALIDA) | (fechas > FECHA_MAXIMA_VALIDA)).sum())
    registros.append({
        "Columna": col,
        "Regla": (f"[{FECHA_MINIMA_VALIDA.date()},"
            f" {FECHA_MAXIMA_VALIDA.date()}]"),
        "Fuera_Rango": fuera,
        "Fuera_Rango_%": round(fuera / filas * 100, 2),
        "Min_Observado": fechas.min(),
        "Max_Observado": fechas.max(),
        "Atipicos_2std": None,})

  # 4.3 Validación de datos binarios
  for col, validos in VALORES_BINARIOS_VALIDOS.items():
    if col not in df.columns:
      continue
    fuera = int((df[col].notnull() & ~df[col].isin(validos)).sum())
    registros.append({
        "Columna": col,
        "Regla": "{" + ", ".join(sorted(validos)) + "}",
        "Fuera_Rango": fuera,
        "Fuera_Rango_%": round(fuera / filas * 100, 2),
        "Min_Observado": None,
        "Max_Observado": None,
        "Atipicos_2std": None,})

  tabla = pd.DataFrame(registros)
  print(tabla.to_string(index=False))

  ruta = DIR_RESULTADOS_TABLAS / "resultado_rangos.csv"
  tabla.to_csv(ruta, index=False)
  print(f"\nLa tabla se guardó en: {ruta}\n")
  return tabla

def diagnostico_validez_rango_columna(df: pd.DataFrame) -> pd.DataFrame:
  print("=== 4.1 Rango mínimo/máximo establecido por la columna ===")
  filas = len(df)

  # Validación para valores mínimos/máximos según dato
  reglas = {
      "inactive_3_months_flag no coincide con months_inactive >= 3": (
          lambda d: (d["months_inactive"] >= 3).astype(int)
          != d["inactive_3_months_flag"]),
      "subscription_status Inactive con months_inactive < 3": (
          lambda d: (d["subscription_status"] == "Inactive")
          & (d["months_inactive"] < 3)),
      "Conversión a suscripción sin interacción con anuncios": (
          lambda d: (d["ad_conversion_to_subscription"] == "Yes")
          & (d["ad_interaction"] == "No")),
      "Plan Free con conversión a suscripción": (
          lambda d: (d["subscription_type"] == "Free")
          & (d["ad_conversion_to_subscription"] == "Yes")),}

  registros = []
  for nombre, regla in reglas.items():
    try:
      incumplen = int(regla(df).sum())
    except KeyError as e:
      print(f"Ojito: falta la columna {e}, falta '{nombre}'")
      continue
    registros.append({
        "Regla": nombre,
        "Filas_Incumplen": incumplen,
        "Porcentaje_%": round(incumplen / filas * 100, 2),})

  tabla = pd.DataFrame(registros)
  print(tabla.to_string(index=False))

  ruta = DIR_RESULTADOS_TABLAS / "resultado_validez_rango_columna.csv"
  tabla.to_csv(ruta, index=False)
  print(f"\na tabla se guardó en: {ruta}\n")
  return tabla

# Rsultados y exportación de csv's
def diagnostico_calidad(df: pd.DataFrame) -> dict:
  print("=== Diagnostico de Calidad ===")
  t_faltantes = valores_faltantes(df)
  t_duplicados = diagnostico_duplicados(df)
  t_tipos = tipos(df)
  t_rangos = diagnostico_rangos(df)
  t_consistencia = diagnostico_validez_rango_columna(df)

  resumen = pd.DataFrame({
      "Index": [
          "Filas",
          "Columnas",
          "Columnas con datos faltantes",
          "Celdas faltantes (nulos y placeholders)",
          "Duplicado exactos",
          "Filas mismo ID, distintos datos",
          "Mismos datos, distinto ID",
          "Columnas con tipo erróneo",
          "Datos fuera de rango",
          "Datos fuera del rango de la columna",],
      "Valor": [
          len(df),
          df.shape[1],
          int((t_faltantes["Total_Faltantes"] > 0).sum()),
          int(t_faltantes["Total_Faltantes"].sum()),
          int(t_duplicados["Filas_Afectadas"].iloc[0]),
          int(t_duplicados["Filas_Afectadas"].iloc[1]),
          int(t_duplicados["Filas_Afectadas"].iloc[2]),
          int((t_tipos["Estado"] == "Posible Error").sum()),
          int(t_rangos["Fuera_Rango"].sum()),
          int(t_consistencia["Filas_Incumplen"].sum()),],})

  print("Resultados del Diagnóstico:")
  print(resumen.to_string(index=False))
  ruta = DIR_RESULTADOS_TABLAS / "resultados_diagnostico.csv"
  resumen.to_csv(ruta, index=False)
  print(f"\nLa tabla se guardó en: {ruta}")
  print("=======================================\n")
  return {
      "faltantes": t_faltantes,
      "duplicados": t_duplicados,
      "tipos": t_tipos,
      "rangos": t_rangos,
      "consistencia": t_consistencia,
      "resumen": resumen,}

resultados_calidad = diagnostico_calidad(df)


# LIMPIEZA Y PREPARACIÓN (fernando)


# ESTADÍSTICA DESCRIPTIVA (joaquin)


# RELACIÓN ENTRE VARIABLES (nadie aun)


# VISUALIZACIÓN DE DATOS (claudio)


# EXPORTACIÓN (nadie aun)


# REPRODUCIBILIDAD (nadie aun)
