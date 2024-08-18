import pandas as pd
import folium
from folium import IFrame
import plotly.express as px
import os
import requests
from io import StringIO
import streamlit as st
from folium.plugins import MarkerCluster


url = 'https://raw.githubusercontent.com/luciabelengonzalez/time_series_map_streamlit/main/EVI_Puntos_250m%20(1).csv'
response = requests.get(url)
df = pd.read_csv(StringIO(response.text))


df['coordinates'] = df['coordinates'].str.replace("[", "")
df['coordinates'] = df['coordinates'].str.replace("]", "")


# Convertir la columna de coordenadas de texto a listas de flotantes (longitud, latitud)
df['coordinates'] = df['coordinates'].apply(lambda x: list(map(float, x.split(','))))
df[['longitude', 'latitude']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)

# Crear un mapa base usando Folium
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)

# Agregar un marcador por ID único
unique_ids = df['id'].unique()
for uid in unique_ids:
    # Obtener la primera coordenada para cada ID
    coord = df[df['id'] == uid].iloc[0]
    folium.Marker(
        location=[coord['latitude'], coord['longitude']],
        popup=f"ID: {uid}",
        icon=folium.Icon(color='blue')
    ).add_to(m)

# Mostrar el mapa en Streamlit
st.write("### Mapa de puntos")
folium_static(m)

# Seleccionar ID en el mapa
selected_id = st.selectbox('Selecciona un ID:', unique_ids)

# Filtrar los datos por ID seleccionado
selected_data = df[df['id'] == selected_id]

# Crear un gráfico de la serie temporal de EVI
fig = px.line(selected_data, x='date', y='EVI', title=f'Serie Temporal de EVI para ID: {selected_id}')

# Mostrar el gráfico en Streamlit
st.write(f"### Serie Temporal de EVI para ID: {selected_id}")

