import streamlit as st

st.set_page_config(page_title="Rain Data", layout="wide")

home_page = st.Page("pages/home.py", title="Início", icon="🏠", default=True)
raindata_page = st.Page("pages/raindata.py", title="Explorador de Chuva", icon="🌧️")

pg = st.navigation([home_page, raindata_page])
pg.run()
