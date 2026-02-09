import glob
import streamlit as st

from src.utils.i18n import get_text
from src.functions.data import clean_dataset, get_monthly_mean_precipitation, load_metadata, load_station_data


lang = st.session_state.get("lang")


st.title(get_text('hydrologic_year', lang))

df_meta = load_metadata()

if df_meta is None:
    st.warning(get_text('rain_no_metadata', lang))
else:
    st.sidebar.header(get_text('filters', lang))

    if 'Situacao' in df_meta.columns:
        st.sidebar.markdown(f"**{get_text('operational_status', lang)}**")
        situacoes = sorted(df_meta['Situacao'].dropna().unique())
        selected_situacao = []
        for situacao in situacoes:
            if st.sidebar.checkbox(situacao, value=True):
                selected_situacao.append(situacao)

        if selected_situacao:
            df_filtered = df_meta[df_meta['Situacao'].isin(selected_situacao)]
        else:
            df_filtered = df_meta[df_meta['Situacao'].isin([])]
    else:
        df_filtered = df_meta

    if 'Codigo Estacao' in df_filtered.columns:
        df_filtered = df_filtered.sort_values(by='Codigo Estacao')

    st.sidebar.markdown(get_text('stations_available',
                        lang, count=len(df_filtered)))

    if not df_filtered.empty:
        col_codigo = 'Codigo Estacao' if 'Codigo Estacao' in df_filtered.columns else 'id_arquivo'
        col_nome = 'Nome' if 'Nome' in df_filtered.columns else 'id_arquivo'

        df_filtered['display_label'] = df_filtered[col_codigo].astype(
            str) + " - " + df_filtered[col_nome].astype(str)

        default_index = 0
        options = df_filtered['display_label'].unique()

        if 'selected_station_code' in st.session_state:
            pre_selected_code = st.session_state['selected_station_code']
            match = df_filtered[df_filtered[col_codigo] == pre_selected_code]

            if not match.empty:
                label_to_select = match.iloc[0]['display_label']
                if label_to_select in options:
                    default_index = list(options).index(label_to_select)
            del st.session_state['selected_station_code']

        station_option = st.selectbox(
            get_text('select_station', lang),
            options=options,
            index=default_index
        )

        station_meta = df_filtered[df_filtered['display_label']
                                   == station_option].iloc[0]
        station_id = station_meta['id_arquivo']

        patterns = [
            f"rain_datasets/dados_{station_id}_*.parquet",
            f"data/dados_{station_id}_*.parquet"
        ]

        parquet_file = None
        for p in patterns:
            files = glob.glob(p)
            if files:
                parquet_file = files[0]
                break
        
        if parquet_file:
            try:
                raw_data = load_station_data(parquet_file)
                
                metadata, dataset = clean_dataset(raw_data)
            
                if not dataset.empty:
                    st.success(f"Dados carregados para estação: {station_meta.get('Nome', station_id)}")

                    monthly_dataset = get_monthly_mean_precipitation(dataset)
                    
                    st.subheader("Médias Mensais")
                    st.dataframe(monthly_dataset, use_container_width=True)
                    
                    # Aqui você pode chamar as funções de cálculo hidrológico
                    # Ex: compute_max_daily_preciptation(dataset)
                    
                else:
                    st.warning("O arquivo foi encontrado, mas não contém dados válidos após a limpeza.")

            except Exception as e:
                st.error(f"Erro ao processar o arquivo da estação: {e}")
        else:
            st.error(f"Arquivo de dados não encontrado para a estação ID: {station_id}")