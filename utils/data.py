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

def is_continuous(months: list) -> tuple[bool, list]:
    """Verify is the the selected six monts are a continuous calendar window. 
    
    Verifica se os 6 meses representam um bloco contínuo no calendário. Considera circularidade: exemplo (9,10,11,12,1,2)

    :param months: Months list (1 to 12)

    :return: [0] = Boolean seting if the list is continuous, [1] = Month list (empty if they are not continuous)
    """

    months = sorted(months)

    # Testing all the possible combinations since the time is a continuous measure
    for month in months:
        window = [(month + i - 1) % 12 + 1 for i in range(6)]
        if set(window) == set(months):
            return True, window

    return False, []

def get_monthly_mean_precipitation(dataset_metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Function to calculate the mensal mean precipitation
    
    :param dataset: Dataset from the BDMEP file data (city, lat, long, alt, etc.)
    :type dataset: pd.DataFrame
    """
    monthly_sum = dataset_metadata.groupby(['ano civil', 'mes'])['precipitacao total diaria (mm)'].sum().reset_index()

    monthly = monthly_sum.groupby('mês')['precipitacao total diaria (mm)'].mean().reset_index()
    monthly.rename(columns={'precipitacao total diaria (mm)': 'precipitacao media mensal (mm)'}, inplace=True)

    return monthly

def get_dry_season(monthly_dataset: pd.DataFrame) -> pd.DataFrame:     

    return monthly_dataset.sort_values(by='precipitacao media mensal (mm)').head(6)

def get_hydrological_year_init(dataset: pd.DataFrame) -> tuple[str, int]:
        
    # Verify if the dry season is continuous
    year_tupe, months_window = is_continuous(dataset['mês'].tolist())
    
    if year_tupe:
        method = "Ano hidrológico"
        hydrological_year_init = months_window[-1] % 12 + 1
    else:
        method = "Ano civil"
        hydrological_year_init = 1

    return method, hydrological_year_init