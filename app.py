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

# Convertir la columna de fecha a tipo datetime
df['date'] = pd.to_datetime(df['date'])

# Extraer año y mes de la fecha como Periodo y luego convertir a string
df['year_month'] = df['date'].dt.to_period('M').astype(str)
print(df.head())  # Print the first few rows to see if 'coordinates' is present and correctly formatted
# Crear una función para generar el mapa

def create_map(df):
    used_ids = []
    df[['longitude', 'latitude']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)
    lon_mean = df['longitude'].astype(float).mean()
    lat_mean = df['latitude'].astype(float).mean()
    m = folium.Map(location=[lon_mean,
                              lat_mean],
                   zoom_start=10)

    # Agrupar los puntos en un MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df.iterrows():
        if row['id'] not in used_ids:
            popup_content = f"""
            <b>ID:</b> {row['id']}<br>
            <b>Date:</b> {row['date'].strftime('%Y-%m-%d')}<br>
            <b>EVI:</b> {row['EVI']}<br>
            <a href="#" onclick="fetch_data({row['id']}); return false;">View Time Series</a>
            """
            popup = IFrame(popup_content, width=200, height=100)
            folium.Marker(location=[row['latitude'], row['longitude']], popup=folium.Popup(popup)).add_to(marker_cluster)
    
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
