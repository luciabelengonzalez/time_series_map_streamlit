import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
import os
import requests
from io import StringIO
import streamlit as st
import streamlit.components.v1 as components


# URL de tiles satelitales de ESRI
ESRI_SATELLITE_TILES = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

url = 'https://raw.githubusercontent.com/luciabelengonzalez/time_series_map_streamlit/main/EVI_Puntos_250m%20(1).csv'
response = requests.get(url)
df = pd.read_csv(StringIO(response.text))


df['coordinates'] = df['coordinates'].str.replace("[", "")
df['coordinates'] = df['coordinates'].str.replace("]", "")


# Convertir la columna de coordenadas de texto a listas de flotantes (longitud, latitud)
df['coordinates'] = df['coordinates'].apply(lambda x: list(map(float, x.split(','))))
df[['longitude', 'latitude']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)
df['date'] = pd.to_datetime(df['date'])


# Crear un mapa base usando Folium con fondo de ESRI
m = folium.Map(
    location=[df['latitude'].mean(), df['longitude'].mean()],
    zoom_start=10,
    tiles=ESRI_SATELLITE_TILES,
    attr="ESRI"
)

# Crear un contenedor de JavaScript para enviar el ID al frontend de Streamlit
script = """
<script>
function sendID(id) {
    const streamlitMessage = {
        type: 'message',
        df: { id: id }
    };
    window.parent.postMessage(streamlitMessage, '*');
}
</script>
"""

# Agregar puntos con CircleMarker y JavaScript para enviar el ID
unique_ids = df['id'].unique()
for uid in unique_ids:
    coord = df[df['id'] == uid].iloc[0]
    folium.CircleMarker(
        location=[coord['latitude'], coord['longitude']],
        radius=8,  # Tamaño del punto
        color='blue',  # Color del borde
        fill=True,
        fill_color='blue',  # Color de relleno
        fill_opacity=0.6,  # Opacidad del relleno
        popup=f"ID: {uid}"
    ).add_to(m)

# Mostrar el mapa en Streamlit
st.write("### Mapa de puntos")

# Obtener el ID desde el mensaje enviado
selected_id = st.text_input('ID seleccionado')

# Filtrar los datos por ID seleccionado
selected_df = df[df['id'] == selected_id]

# Comprobar si hay datos seleccionados
if not selected_df.empty:
    # Crear un gráfico de la serie temporal de EVI
    fig = px.line(selected_df, x='date', y='EVI', title=f'Serie Temporal de EVI para ID: {selected_id}', markers=True)
    # Mostrar el gráfico en Streamlit
    st.write(f"### Serie Temporal de EVI para ID: {selected_id}")
    st.plotly_chart(fig)
else:
    st.write("No hay datos disponibles para el ID seleccionado.")
