# BigData04

Proyecto de análisis exploratorio y preparación de datos sobre el comportamiento de usuarios de Spotify. El objetivo principal es revisar, limpiar y transformar un dataset de usuarios para detectar inconsistencias, analizar patrones de uso, comparar segmentos de suscripción y generar visualizaciones y tablas de resultados reproducibles.

## Descripción general

Este repositorio contiene un pipeline de análisis en Python para:

- cargar un dataset de comportamiento de usuarios de Spotify
- inspeccionar columnas, tipos y datos faltantes
- detectar duplicados, valores fuera de rango y inconsistencias
- limpiar y preparar los datos para análisis posterior
- calcular estadísticos descriptivos
- estudiar relaciones entre variables
- generar gráficos y exportar resultados

El proyecto está orientado a práctica de Big Data y ciencia de datos aplicada, con foco en la calidad de los datos antes de cualquier modelado o análisis más avanzado.

## Requisitos

- Python 3.10 o superior
- pip
- Git

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/Korsohh/BigData04.git
cd BigData04
```

2. Verifica la versión de Python:

```bash
python --version
```

3. Crea y activa un entorno virtual (opcional, pero recomendado):

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Instala las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Dataset

El proyecto usa el archivo siguiente:

- `spotify_user_behavior_realistic_50000_rows.csv`

Ubicación esperada dentro del repositorio:

```text
BigData04/
└── spotify_user_behavior_realistic_50000_rows.csv
```

Si el archivo no está disponible localmente, puedes descargarlo con la siguiente instrucción:

```bash
curl -L "https://raw.githubusercontent.com/Korsohh/BigData04/main/spotify_user_behavior_realistic_50000_rows.csv" -o spotify_user_behavior_realistic_50000_rows.csv
```

También puedes accederlo desde la interfaz de GitHub:

```text
https://github.com/Korsohh/BigData04/blob/main/spotify_user_behavior_realistic_50000_rows.csv
```

## Estructura del repositorio

```text
BigData04/
├── analisis_exploratorio.py
├── requirements.txt
├── spotify_user_behavior_realistic_50000_rows.csv
├── README.md
├── datos/
│   └── procesados/
│       └── spotify_procesado.csv
├── resultados/
│   ├── figuras/
│   └── tablas/
└── .gitignore
```

## Ejecución

Desde la raíz del proyecto, ejecuta:

```bash
python analisis_exploratorio.py
```

Este script realiza las siguientes etapas:

1. carga e inspección del dataset
2. diagnóstico de calidad de datos
3. limpieza y preparación de registros
4. análisis estadístico descriptivo
5. cálculo de relaciones entre variables
6. generación de gráficos
7. exportación del dataset procesado

## Salidas esperadas

Durante la ejecución del proyecto se generan archivos en las carpetas:

- `resultados/tablas/`: CSV con diagnósticos, estadísticos y resúmenes
- `resultados/figuras/`: gráficos generados en formato PNG
- `datos/procesados/spotify_procesado.csv`: dataset limpio y preparado

## Dependencias

El archivo `requirements.txt` contiene las librerías necesarias para correr el proyecto:

```txt
pandas
matplotlib
numpy
```

## Entregables

Los entregables principales del proyecto son:

- script principal: `analisis_exploratorio.py`
- dataset base: `spotify_user_behavior_realistic_50000_rows.csv`
- dataset procesado: `datos/procesados/spotify_procesado.csv`
- tablas de diagnóstico y análisis: `resultados/tablas/`
- visualizaciones: `resultados/figuras/`
- documentación técnica: `README.md`

## Tecnologías utilizadas

- Python
- Pandas
- Matplotlib
- NumPy

## Nota

Este proyecto está diseñado para ejecutarse de manera reproducible en cualquier entorno con Python 3.10+ y las dependencias indicadas. La descarga del dataset se puede reproducir siguiendo las instrucciones anteriores.

## Autor

Proyecto desarrollado por Joaquin Orellana.
