import glob
import io
import matplotlib as mpl
from matplotlib import pyplot as plt
import streamlit as st

from src.utils.i18n import get_text
from src.functions.data import clean_dataset, get_dry_season, get_hydrological_year_init, get_monthly_mean_precipitation, load_metadata, load_station_data


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
                    st.subheader(get_text('station_details', lang,
                     name=station_meta.get('Nome', station_id)))

                    monthly_dataset = get_monthly_mean_precipitation(dataset)
                    dry_season_df = get_dry_season(monthly_dataset)
                    
                    _, mes_inicio_ano_hidro = get_hydrological_year_init(dry_season_df)

                    chart_column, data_column = st.columns([1, 1])

                    with chart_column:
                        st.markdown(get_text('monthly_average_precipitation', lang))
                        
                        mpl.rcParams.update({
                            'font.family': 'serif',
                            'mathtext.fontset': 'cm',
                            'axes.unicode_minus': False
                        })

                        if lang == 'en':
                            label_mean = 'Monthly Average'
                            label_dry_prefix = 'Driest month'
                            label_wet_prefix = 'Wettest month'
                            label_start_prefix = 'Onset of rainy season'
                            label_x_axis = 'Month'
                            label_y_axis = 'Average Precipitation (mm)'
                        else:
                            label_mean = 'Média Mensal'
                            label_dry_prefix = 'Mês mais seco'
                            label_wet_prefix = 'Mês mais chuvoso'
                            label_start_prefix = 'Início do período chuvoso'
                            label_x_axis = 'Mês'
                            label_y_axis = 'Precipitação Média (mm)'
                        
                        label_size = 14
                        axis_size = 14
                        legend_size = 10
                        
                        fig, ax = plt.subplots(figsize=(10, 8))
                        
                        ax.plot(
                            monthly_dataset['mes'], 
                            monthly_dataset['precipitacao media mensal (mm)'], 
                            marker='o', 
                            color='red', 
                            linewidth=1.5,
                            label=label_mean 
                        )

                        idx_min = monthly_dataset['precipitacao media mensal (mm)'].idxmin()
                        row_min = monthly_dataset.loc[idx_min]
                        
                        idx_max = monthly_dataset['precipitacao media mensal (mm)'].idxmax()
                        row_max = monthly_dataset.loc[idx_max]
                        
                        ax.scatter(row_min['mes'], row_min['precipitacao media mensal (mm)'], 
                                   s=140, color='blue', label=f"Mês mais seco = {int(row_min['mes'])}")
                        
                        ax.scatter(row_max['mes'], row_max['precipitacao media mensal (mm)'], 
                                   s=140, color='green', label=f"Mês mais chuvoso = {int(row_max['mes'])}")

                        plt.axvline(x=mes_inicio_ano_hidro, color='purple', linestyle='--', 
                            linewidth=2.0, alpha=0.7, 
                            label=f'{label_start_prefix} = {mes_inicio_ano_hidro}')

                        ax.set_xlabel(label_x_axis, fontsize=label_size)
                        ax.set_ylabel(label_y_axis, fontsize=label_size)
                        ax.set_xticks(range(1, 13)) 
                        ax.set_xlim(0.5, 12.5)       
                        
                        ax.tick_params(axis='both', which='major', labelsize=axis_size)
                        ax.grid(True, alpha=0.3)
                        ax.legend(fontsize=legend_size)
                        
                        st.pyplot(fig)

                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                        buf.seek(0)

                        st.download_button(
                            label=get_text('download_chart', lang),
                            data=buf,
                            file_name=f"media_mensal_{station_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )


                    with data_column:
                        st.markdown(get_text('dry_season_table', lang))
                        display_dry = dry_season_df.copy()
                        display_dry['precipitacao media mensal (mm)'] = display_dry['precipitacao media mensal (mm)'].apply(lambda x: f"{x:.1f}")
                        
                        st.dataframe(
                            display_dry[['mes', 'precipitacao media mensal (mm)']], 
                            hide_index=True, 
                            use_container_width=True,
                            height=220
                        )
                        
                        st.divider()

                        st.markdown(get_text('monthly_mean_table', lang))
                        display_monthly = monthly_dataset[['mes', 'precipitacao media mensal (mm)']].copy()
                        display_monthly['precipitacao media mensal (mm)'] = display_monthly['precipitacao media mensal (mm)'].apply(lambda x: f"{x:.1f}")

                        st.dataframe(
                            display_monthly, 
                            hide_index=True, 
                            use_container_width=True,
                            height=220
                        )

                    
                else:
                    st.warning("O arquivo foi encontrado, mas não contém dados válidos após a limpeza.")

            except Exception as e:
                st.error(f"Erro ao processar o arquivo da estação: {e}")
        else:
            st.error(f"Arquivo de dados não encontrado para a estação ID: {station_id}")