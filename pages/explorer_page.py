import glob
import os
import pandas as pd
import streamlit as st
import plotly.express as px

from src.utils.i18n import get_text
from src.functions.data import clean_commodity_data


lang = st.session_state.get("lang")


st.title(get_text('commodity_explorer', lang))

# Buscar arquivos de commodities
commodity_files = glob.glob("data/*.parquet") + \
    glob.glob("data/commodities/*.parquet")
commodity_files = [
    f for f in commodity_files if 'metadata' not in f and 'dados_' not in f]

if not commodity_files:
    st.warning("Nenhum arquivo de commodity encontrado.")
else:
    st.sidebar.header(get_text('filters', lang))

    commodity_options = {}
    for f in commodity_files:
        name = os.path.basename(f).split('.')[0].replace('_', ' ').title()
        commodity_options[name] = f

    selected_commodity_name = st.selectbox(
        get_text('select_commodity_file', lang),
        list(commodity_options.keys())
    )

    if selected_commodity_name:
        file_path = commodity_options[selected_commodity_name]
        try:
            raw_df = pd.read_parquet(file_path)
            df_comm = clean_commodity_data(raw_df)

            date_col = 'data medicao' if 'data medicao' in df_comm.columns else None

            if date_col:
                df_comm[date_col] = pd.to_datetime(
                    df_comm[date_col], errors='coerce')
                df_comm = df_comm.sort_values(by=date_col)

                st.sidebar.divider()
                st.sidebar.markdown(f"### {get_text('period_filter', lang)}")

                min_date = df_comm[date_col].min().date()
                max_date = df_comm[date_col].max().date()

                periodo = st.sidebar.date_input(
                    get_text('select_interval', lang),
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD/MM/YYYY"
                )

                if isinstance(periodo, tuple) and len(periodo) == 2:
                    start_date, end_date = periodo
                    mask = (df_comm[date_col].dt.date >= start_date) & (
                        df_comm[date_col].dt.date <= end_date)
                    df_comm = df_comm.loc[mask]

            with st.expander(get_text('view_data_table', lang)):
                st.dataframe(df_comm, use_container_width=True)

            # Selecionar coluna (UF) para plotar o eixo Y
            numeric_cols = df_comm.select_dtypes(
                include=['number']).columns.tolist()
            if numeric_cols:
                uf_to_plot = st.selectbox(
                    get_text('select_uf_col', lang), numeric_cols)

                if date_col and uf_to_plot:
                    fig = px.line(
                        df_comm,
                        x=date_col,
                        y=uf_to_plot,
                        title=get_text('commodity_time_series',
                                       lang, uf=uf_to_plot),
                        color_discrete_sequence=["#2ca02c"],
                        labels={
                            date_col: get_text('date_label', lang),
                            uf_to_plot: get_text('price_label_brl', lang)
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)

            csv_data = df_comm.to_csv(index=False).encode('utf-8')
            st.download_button(
                get_text('download_commodity_csv', lang),
                data=csv_data,
                file_name=f"{selected_commodity_name.replace(' ', '_').lower()}_dados.csv",
                mime="text/csv",
                use_container_width=True
            )

        except Exception as e:
            st.error(get_text('error_loading', lang, error=str(e)))
