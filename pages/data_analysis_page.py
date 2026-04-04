import glob
import io
import os
import pandas as pd
import streamlit as st

from src.utils.i18n import get_text
from src.functions.data import clean_dataset, load_metadata, load_station_data, clean_commodity_data, BRAZIL_UF_COORDS
from src.functions.hydrology import compute_spi
from src.functions.charts import plot_spi_vs_commodities

lang = st.session_state.get("lang")

st.title(get_text('commodity_analysis', lang))

df_meta = load_metadata()

if df_meta is None:
    st.warning(get_text('rain_no_metadata', lang))
else:
    st.sidebar.header(get_text('filters', lang))

    # Identificar de forma segura a coluna que guarda o Estado
    col_uf = next((c for c in ['Estado', 'SG_ESTADO', 'UF',
                  'estado', 'uf'] if c in df_meta.columns), None)

    # Se a coluna não existir, inferimos o Estado mais próximo usando latitude e longitude
    if not col_uf and 'Latitude' in df_meta.columns and 'Longitude' in df_meta.columns:
        def get_closest_uf(lat, lon):
            try:
                lat, lon = float(lat), float(lon)
                # Calcula a distância euclidiana quadrada e pega ao estado (UF) mais próximo
                return min(BRAZIL_UF_COORDS.keys(), key=lambda uf: (lat - BRAZIL_UF_COORDS[uf]['lat'])**2 + (lon - BRAZIL_UF_COORDS[uf]['lon'])**2)
            except:
                return None

        df_meta['UF_inferred'] = df_meta.apply(
            lambda r: get_closest_uf(r['Latitude'], r['Longitude']), axis=1)
        col_uf = 'UF_inferred'

    if not col_uf:
        st.error(
            "A coluna de Estado (UF) não foi encontrada e não há coordenadas válidas para inferir. Não é possível agregar os dados.")
    else:
        # Prevenindo mostrar UFs vazios
        ufs_disponiveis = [uf for uf in sorted(
            df_meta[col_uf].dropna().unique()) if uf in BRAZIL_UF_COORDS.keys()]
        selected_uf = st.sidebar.selectbox(
            get_text('select_state', lang), ufs_disponiveis)

        commodity_files = glob.glob(
            "data/*.parquet") + glob.glob("data/commodities/*.parquet")
        commodity_files = [
            f for f in commodity_files if 'metadata' not in f and 'dados_' not in f]

        commodity_options = {}
        for f in commodity_files:
            name = os.path.basename(f).split('.')[0].replace('_', ' ').title()
            commodity_options[name] = f

        selected_commodities = st.sidebar.multiselect(
            get_text('select_commodities', lang),
            list(commodity_options.keys())
        )

        if not selected_uf or not selected_commodities:
            st.info(
                "Selecione um Estado (UF) e pelo menos uma Commodity na barra lateral para gerar o gráfico.")
        else:
            with st.spinner(get_text('computing_data', lang)):
                # Carregar e limpar as commodities selecionadas
                comm_dataframes = {}
                for comm in selected_commodities:
                    df_comm = pd.read_parquet(commodity_options[comm])
                    df_comm = clean_commodity_data(df_comm)
                    if selected_uf in df_comm.columns:
                        temp_df = df_comm[['data medicao', selected_uf]].copy()
                        temp_df.rename(
                            columns={selected_uf: comm}, inplace=True)
                        temp_df['data medicao'] = pd.to_datetime(
                            temp_df['data medicao'], errors='coerce')
                        comm_dataframes[comm] = temp_df.dropna()

                if not comm_dataframes:
                    st.warning(get_text('no_commodity_data', lang))
                else:
                    st.info(get_text('normalization_info', lang))

                    # Resgatar as estações do Estado e agregar a precipitação média
                    estacoes_uf = df_meta[df_meta[col_uf] == selected_uf]
                    spi_uf_list = []
                    col_codigo = 'Codigo Estacao' if 'Codigo Estacao' in df_meta.columns else 'id_arquivo'

                    for _, row in estacoes_uf.iterrows():
                        station_id = row.get(col_codigo)
                        if not station_id:
                            continue

                        patterns = [f"data/rain/dados_{station_id}_*.parquet",
                                    f"rain_datasets/dados_{station_id}_*.parquet", f"data/dados_{station_id}_*.parquet"]
                        for pattern in patterns:
                            match = glob.glob(pattern)
                            if match:
                                try:
                                    estacao_data = load_station_data(match[0])
                                    _, _, spi_df = clean_dataset(estacao_data)
                                    if not spi_df.empty:
                                        spi_uf_list.append(spi_df)
                                except Exception:
                                    pass
                                break

                    if not spi_uf_list:
                        st.warning(
                            "Não foi possível processar volume suficiente de dados de chuva para calcular o SPI deste Estado.")
                    else:
                        # Agrupar dados de todas as estações do estado formando a precipitação histórica estadual mensal
                        spi_uf_concat = pd.concat(spi_uf_list)
                        spi_uf_mensal = spi_uf_concat.groupby(['ano civil', 'mes'])[
                            'precipitacao mensal (mm)'].mean().reset_index()

                        # Calcular o SPI do Estado e criar coluna de datas para o eixo X
                        spi_state = compute_spi(spi_uf_mensal)
                        spi_state['data medicao'] = pd.to_datetime(
                            spi_state['ano civil'].astype(
                                str) + '-' + spi_state['mes'].astype(str) + '-01'
                        )
                        spi_state = spi_state.sort_values('data medicao')

                        # Normalização do SPI (escala 0 a 1)
                        min_spi = spi_state['SPI_1'].min()
                        max_spi = spi_state['SPI_1'].max()
                        if max_spi != min_spi:
                            spi_state['SPI_1_norm'] = (
                                spi_state['SPI_1'] - min_spi) / (max_spi - min_spi)
                        else:
                            spi_state['SPI_1_norm'] = 0.5

                        # Normalização das Commodities (escala 0 a 1)
                        for comm_name, df_comm in comm_dataframes.items():
                            min_comm = df_comm[comm_name].min()
                            max_comm = df_comm[comm_name].max()
                            if max_comm != min_comm:
                                df_comm[f'{comm_name}_norm'] = (
                                    df_comm[comm_name] - min_comm) / (max_comm - min_comm)
                            else:
                                df_comm[f'{comm_name}_norm'] = 0.5

                        # Plotar em formato robusto via Matplotlib para ser compatível com artigos/LaTeX
                        fig = plot_spi_vs_commodities(
                            output_folder=None,
                            name=f"uf_{selected_uf}",
                            lang=lang,
                            spi_df=spi_state,
                            comm_dataframes=comm_dataframes,
                            selected_uf=selected_uf
                        )

                        st.pyplot(fig, use_container_width=True)

                        # Preparar imagem para Download
                        buf_fig = io.BytesIO()
                        fig.savefig(buf_fig, format="png",
                                    dpi=600, bbox_inches='tight')
                        buf_fig.seek(0)

                        # Preparar exportação do Dataset Único
                        export_df = spi_state[['data medicao', 'SPI_1']].copy()
                        export_df.rename(
                            columns={'SPI_1': f'SPI_1_Media_{selected_uf}'}, inplace=True)
                        for comm_name, df_comm in comm_dataframes.items():
                            temp_df = df_comm[[
                                'data medicao', comm_name]].copy()
                            export_df = pd.merge(
                                export_df, temp_df, on='data medicao', how='outer')

                        export_df = export_df.sort_values('data medicao')
                        csv_data = export_df.to_csv(
                            index=False).encode('utf-8')

                        # Botões unificados com espaçamento
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            st.download_button(
                                label=get_text('download_chart', lang),
                                data=buf_fig,
                                file_name=f"spi_vs_commodities_{selected_uf}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        with btn_col2:
                            st.download_button(
                                label="📥 Baixar dados extraídos (.csv)" if lang == "pt" else "📥 Download dataset (.csv)",
                                data=csv_data,
                                file_name=f"dataset_spi_vs_commodities_{selected_uf}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
