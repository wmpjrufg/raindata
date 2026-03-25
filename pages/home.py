import os
import glob

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from src.utils.i18n import get_text
from src.functions.data import BRAZIL_UF_COORDS, clean_commodity_data

lang = st.session_state.get("lang")

st.title(get_text('home_title', lang))


@st.cache_data
def load_data():
    if os.path.exists("./data/rain/metadata_estacoes.parquet"):
        try:
            df = pd.read_parquet("./data/rain/metadata_estacoes.parquet")

            for col in ['Latitude', 'Longitude']:
                if col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(
                            ',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.dropna(subset=['Latitude', 'Longitude'])
            return df
        except Exception as e:
            st.error(f"Erro ao ler metadados: {e}")
            return None
    return None


def get_available_commodities() -> list:
    """Fetch parquet files ignoring standard meteorological metadata."""
    files = glob.glob("data/*.parquet") + \
        glob.glob("data/commodities/*.parquet")
    return [f for f in files if 'metadata' not in f and 'dados_' not in f]


df = load_data()
commodity_files = get_available_commodities()

if df is not None and not df.empty:
    st.write(get_text('home_viewing', lang, count=len(df)))

    with st.expander(get_text('home_expand', lang)):
        st.dataframe(df)

    st.subheader(get_text('home_subtitle', lang))

    col1, col2 = st.columns(2)
    with col1:
        show_stations = st.checkbox(
            get_text('show_stations', lang), value=True)
    with col2:
        show_commodities = st.checkbox(
            get_text('show_commodities', lang), value=True)

    df_commodities = None
    current_emoji = '📍'

    if show_commodities and commodity_files:
        emoji_map = {'cafe': '☕', 'cana': '🎋', 'milho': '🌽', 'soja': '🌱'}

        def format_commodity_name(filepath):
            filename = os.path.basename(filepath).lower()
            for key in emoji_map.keys():
                if key in filename:
                    return get_text(f'commodity_{key}', lang), key

            clean_name = os.path.basename(filepath).split('.')[
                0].replace('_', ' ')
            return clean_name.title(), clean_name.lower()

        file_options = {}
        for f in commodity_files:
            translated_name, raw_key = format_commodity_name(f)
            file_options[translated_name] = (f, raw_key)

        selected_label = st.selectbox(
            get_text('select_commodity', lang), list(file_options.keys()))

        filepath, raw_key = file_options[selected_label]
        current_emoji = emoji_map.get(raw_key, '📦')

        try:
            raw_commodity_df = pd.read_parquet(filepath)
            df_commodities = clean_commodity_data(raw_commodity_df)
        except Exception as e:
            st.error(f"Error loading commodity data: {e}")

    m = folium.Map(location=[-15, -55], zoom_start=4, tiles="CartoDB positron")

    if show_stations:
        for idx, row in df.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=4,
                color="#1f77b4",
                fill=True,
                fill_color="#1f77b4",
                fill_opacity=0.7,
                tooltip=f'{row["Nome"]}<br>Cod: {row["Codigo Estacao"]}'
            ).add_to(m)

    if show_commodities and df_commodities is not None:
        available_ufs = [
            col for col in df_commodities.columns if col in BRAZIL_UF_COORDS.keys()]

        if not df_commodities.empty:
            avg_values = df_commodities[available_ufs].apply(
                pd.to_numeric, errors='coerce').mean().round(2)
        else:
            avg_values = pd.Series(dtype=float)

        for uf in available_ufs:
            coords = BRAZIL_UF_COORDS.get(uf)
            val = avg_values.get(uf, 0)

            icon_html = f'<div style="font-size: 30px; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">{current_emoji}</div>'

            folium.Marker(
                location=[coords['lat'], coords['lon']],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{uf}</b><br>{get_text('avg_historical_price', lang)} {val}"
            ).add_to(m)

    # Renderiza o mapa e captura interações (como o clique)
    map_data = st_folium(
        m,
        height=650,
        use_container_width=True,
        returned_objects=["last_object_clicked"]
    )

    # Lógica que substitui o evento de clique do Plotly para redirecionar de página
    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"].get("lat")
        lon = map_data["last_object_clicked"].get("lng")

        if lat is not None and lon is not None:
            # Tolerância para encontrar a estação exata baseada no clique
            tol = 1e-4
            mask = (df["Latitude"].between(lat - tol, lat + tol)
                    ) & (df["Longitude"].between(lon - tol, lon + tol))
            if mask.any():
                matched = df[mask].iloc[0]
                st.session_state['selected_station_code'] = matched["Codigo Estacao"]
                st.switch_page("pages/explorer_page.py")

else:
    st.info(get_text('home_no_data', lang))
