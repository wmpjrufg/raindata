translations = {
    'pt': {
        'app_title': '🌧️ Explorador de Dados Pluviométricos',
        'language': 'Idioma',

        'home_title': '🗺️ Mapa das Estações Pluviométricas',
        'home_subtitle': 'Clique em um ponto para ver detalhes',
        'home_viewing': 'Visualizando **{count}** estações com coordenadas válidas.',
        'home_expand': 'Ver dados brutos das estações',
        'home_no_data': 'Nenhuma estação com coordenadas encontrada. Verifique se o arquivo `metadata_estacoes.parquet` existe e foi processado corretamente.',

        'rain_title': '🌧️ Explorador de Dados Pluviométricos',
        'rain_no_metadata': '⚠️ Arquivo de metadados (`metadata_estacoes.parquet`) não encontrado. Por favor, certifique-se de ter executado o notebook `convert.ipynb`.',
        'filters': 'Filtros',
        'operational_status': 'Situação Operacional',
        'stations_available': '**Estações disponíveis:** {count}',
        'select_station': 'Selecione uma Estação:',
        'station_details': '📍 {name}',
        'code': 'Código',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'status': 'Situação',
        'data_loaded': 'Dados carregados com sucesso: {count} registros.',
        'period_filter': '📅 Filtro de Período',
        'select_interval': 'Selecione o Intervalo',
        'view_data_table': 'Ver Tabela de Dados',
        'select_column_chart': 'Selecione a coluna para o gráfico:',
        'time_series': 'Série Temporal - {col}',
        'download_csv': '📥 Baixar dados (CSV)',
        'data_file_not_found': 'Arquivo de dados para a estação {id} não encontrado.',
        'error_loading': 'Erro ao abrir arquivo de dados: {error}',
        'no_stations': 'Nenhuma estação encontrada com os filtros atuais.',
    },
    'en': {
        'app_title': '🌧️ Precipitation Data Explorer',
        'language': 'Language',

        'home_title': '🗺️ Rain Gauge Stations Map',
        'home_subtitle': 'Click on a point to view details',
        'home_viewing': 'Viewing **{count}** stations with valid coordinates.',
        'home_expand': 'View raw station data',
        'home_no_data': 'No stations with coordinates found. Please check if the `metadata_estacoes.parquet` file exists and was processed correctly.',

        'rain_title': '🌧️ Precipitation Data Explorer',
        'rain_no_metadata': '⚠️ Metadata file (`metadata_estacoes.parquet`) not found. Please make sure you have run the `convert.ipynb` notebook.',
        'filters': 'Filters',
        'operational_status': 'Operational Status',
        'stations_available': '**Available stations:** {count}',
        'select_station': 'Select a Station:',
        'station_details': '📍 {name}',
        'code': 'Code',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'status': 'Status',
        'data_loaded': 'Data loaded successfully: {count} records.',
        'period_filter': '📅 Period Filter',
        'select_interval': 'Select Interval',
        'view_data_table': 'View Data Table',
        'select_column_chart': 'Select column for chart:',
        'time_series': 'Time Series - {col}',
        'download_csv': '📥 Download data (CSV)',
        'data_file_not_found': 'Data file for station {id} not found.',
        'error_loading': 'Error opening data file: {error}',
        'no_stations': 'No stations found with current filters.',
    }
}


def get_text(key, lang='pt', **kwargs):
    text = translations.get(lang, translations['pt']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
