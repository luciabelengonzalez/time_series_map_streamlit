import pandas as pd
import folium
from folium import IFrame
import base64
import plotly.express as px
import os

# Construir la ruta del archivo de manera flexible
base_path = os.path.dirname(__file__)  # Obtiene el directorio del script
file_path = os.path.join(base_path, 'EVI_Puntos_250m.csv')

# Cargar el archivo CSV (ajusta la ruta al archivo subido)
df = pd.read_csv(file_path)
df['coordinates'] = df['coordinates'].str.replace("[", "")
df['coordinates'] = df['coordinates'].str.replace("]", "")


# Convertir la columna de coordenadas de texto a listas de flotantes (longitud, latitud)
df['coordinates'] = df['coordinates'].apply(lambda x: list(map(float, x.split(','))))

# Convertir la columna de fecha a tipo datetime
df['date'] = pd.to_datetime(df['date'])

# Extraer año y mes de la fecha como Periodo y luego convertir a string
df['year_month'] = df['date'].dt.to_period('M').astype(str)

import streamlit as st
import folium
from folium import IFrame
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt

# Crear una función para generar el mapa
def create_map(df):
    m = folium.Map(location=[df['coordinates'].str.split(',', expand=True)[0].astype(float).mean(),
                              df['coordinates'].str.split(',', expand=True)[1].astype(float).mean()],
                   zoom_start=10)

    # Agrupar los puntos en un MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df.iterrows():
        coord = row['coordinates'].split(',')
        lat, lon = float(coord[0]), float(coord[1])
        popup_content = f"""
        <b>ID:</b> {row['id']}<br>
        <b>Date:</b> {row['date'].strftime('%Y-%m-%d')}<br>
        <b>EVI:</b> {row['EVI']}<br>
        <a href="#" onclick="fetch_data({row['id']}); return false;">View Time Series</a>
        """
        popup = IFrame(popup_content, width=200, height=100)
        folium.Marker(location=[lat, lon], popup=folium.Popup(popup)).add_to(marker_cluster)
    
    return m

# Crear la serie temporal
def plot_time_series(df, point_id):
    data = df[df['id'] == point_id]
    if not data.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(data['date'], data['EVI'], marker='o')
        plt.title(f"Time Series for ID {point_id}")
        plt.xlabel('Date')
        plt.ylabel('EVI')
        plt.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(plt)
    else:
        st.write("No data available for this ID")

# Crear la aplicación Streamlit
st.title("Interactive Map with Time Series")

# Mostrar el mapa interactivo
map = create_map(df)
st.components.v1.html(map._repr_html_(), height=600)

# Obtener la lista única de IDs
ids = df['id'].unique()

# Crear un selector de ID
selected_id = st.selectbox("Select an ID to view its time series:", ids)

# Mostrar la serie temporal correspondiente al ID seleccionado
plot_time_series(df, selected_id)
