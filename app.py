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

 import pandas as pd
import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
import requests
from io import StringIO

# URL de tiles satelitales de ESRI
ESRI_SATELLITE_TILES = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

# Descargar el archivo CSV
url = 'https://raw.githubusercontent.com/luciabelengonzalez/time_series_map_streamlit/main/EVI_Puntos_250m%20(1).csv'
response = requests.get(url)
df = pd.read_csv(StringIO(response.text))

# Limpiar y procesar las coordenadas
df['coordinates'] = df['coordinates'].str.replace("[", "")
df['coordinates'] = df['coordinates'].str.replace("]", "")
df['coordinates'] = df['coordinates'].apply(lambda x: list(map(float, x.split(','))))
df[['longitude', 'latitude']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)
df['date'] = pd.to_datetime(df['date'])

# Crear un mapa base usando Folium con fondo de ESRI
def create_map():
    m = folium.Map(
        location=[df['latitude'].mean(), df['longitude'].mean()],
        zoom_start=10,
        tiles=ESRI_SATELLITE_TILES,
        attr="ESRI"
    )
    
    unique_ids = df['id'].unique()
    for uid in unique_ids:
        coord = df[df['id'] == uid].iloc[0]
        folium.Marker(
            location=[coord['latitude'], coord['longitude']],
            popup=f"ID: {uid}",
            icon=folium.Icon(color='blue')
        ).add_to(m)
    
    return m

# Usar st.session_state para almacenar el mapa
if 'map' not in st.session_state:
    st.session_state.map = create_map()

# Mostrar el mapa en Streamlit
st.write("### Mapa de puntos")
folium_static(st.session_state.map)

# Crear un gráfico de la serie temporal de EVI
def create_time_series_plot(id):
    selected_df = df[df['id'] == id]
    fig = px.line(selected_df, x='date', y='EVI', title=f'Serie Temporal de EVI para ID: {id}', markers=True)
    return fig

# Seleccionar ID para mostrar la serie temporal
selected_id = st.selectbox('Selecciona un ID:', df['id'].unique())

# Filtrar los datos por ID seleccionado
selected_df = df[df['id'] == selected_id]

# Comprobar si hay datos seleccionados
if not selected_df.empty:
    # Crear el gráfico de la serie temporal de EVI
    fig = create_time_series_plot(selected_id)
    # Mostrar el gráfico en Streamlit
    st.write(f"### Serie Temporal de EVI para ID: {selected_id}")
    st.plotly_chart(fig)
else:
    st.write("No hay datos disponibles para el ID seleccionado.")

