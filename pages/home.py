import os
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.i18n import get_text

lang = st.session_state.get("lang")

st.title(get_text('home_title', lang))


@st.cache_data
def load_data():
    if os.path.exists("./data/metadata_estacoes.parquet"):
        try:
            df = pd.read_parquet("./data/metadata_estacoes.parquet")

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


df = load_data()

if df is not None and not df.empty:
    st.write(get_text('home_viewing', lang, count=len(df)))

    with st.expander(get_text('home_expand', lang)):
        st.dataframe(df)

    st.subheader(get_text('home_subtitle', lang))

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Nome",
        hover_data=["Codigo Estacao", "Situacao"],
        height=600,
        color_discrete_sequence=["#1f77b4"]
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode='event+select',
        mapbox=dict(
            center=dict(lat=-15, lon=-55),
            zoom=3
        )
    )

    event = st.plotly_chart(
        fig,
        on_select="rerun",
        selection_mode="points",
        use_container_width=True,
        config={'scrollZoom': True, 'displayModeBar': True}
    )

    if event and event['selection']['points']:
        point_index = event['selection']['points'][0]['point_index']
        selected_row = df.iloc[point_index]
        code = selected_row.get('Codigo Estacao')

        if code:
            st.session_state['selected_station_code'] = code
            st.switch_page("pages/raindata.py")

else:
    st.info(get_text('home_no_data', lang))
