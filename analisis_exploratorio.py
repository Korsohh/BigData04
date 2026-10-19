from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

base_dir = Path(__file__).resolve().parent
csv_path = base_dir / 'TV Series.csv'

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()  # Eliminar espacios en los nombres de las columnas


#carga y inspección de datos (benjamin diaz)


#diagnostico de calidad (nadie aun)


#limpieza y preparacion (fernando)


#estadistica descriptiva (joaquin)


#relacion entre variables (nadie aun)


#visualizacion de datos (claudio)

fig, ax = plt.subplots(figsize=(10, 6))
#Crear un gráfico de barras para la columna 'Rating'
df['Rating'].value_counts().plot(kind='bar', ax=ax)
    

#exportacion (nadie aun)


#reproducibilidad (nadie aun)