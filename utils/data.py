import os
import glob

import pandas as pd
import streamlit as st

@st.cache_data
def load_metadata():
    if os.path.exists("./data/metadata_estacoes.parquet"):
        try:
            return pd.read_parquet("./data/metadata_estacoes.parquet")
        except Exception:
            return None
    return None

@st.cache_data
def load_station_data(file_path):
    return pd.read_parquet(file_path)