"""Módulo para manipulação de dados da plataforma Banco de Dados Meteorológicos do INMET"""
from datetime import datetime

import pandas as pd
import numpy as np
import scipy as sc


def eh_continuo(lista_meses: list) -> tuple[bool, list]:
    """Verifica se os 6 meses representam um bloco contínuo no calendário. Considera circularidade: exemplo (9,10,11,12,1,2)

    :param lista_meses: Lista com os meses (1 a 12)

    :return: [0] = Booleano indicando se os meses são contínuos, [1] = Lista com os meses em ordem contínua (vazia se não forem contínuos)
    """

    lista_meses = sorted(lista_meses)

    # Testar todas as rotações possíveis, pois o ano é circular
    for inicio in lista_meses:
        bloco = [(inicio + i - 1) % 12 + 1 for i in range(6)]
        if set(bloco) == set(lista_meses):
            return True, bloco

    return False, []


def definicao_ano_hidrologico(df_final: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str, int]:
    """Define se a preciptação deverá ser verificada via ano civil ou ano hidrológico

    :param cabecalho: Metadados do arquivo de dados BDMEP (cidade, lat, long, alt, ..., etc)

    :return: df_final: Dados meteorológicos base BDMEP ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês')
    """
    # Agrupamos por Ano e Mês e fazemos a SOMA (sum)
    totais_mensais = df_final.groupby(['ano civil', 'mês'])['precipitacao total diaria (mm)'].sum().reset_index()

    # Médias mensais de precipitação
    # mensal = df_final.groupby(
    #     'mês')['precipitacao total diaria (mm)'].mean().reset_index()
    mensal = totais_mensais.groupby('mês')['precipitacao total diaria (mm)'].mean().reset_index()
    mensal.rename(columns={'precipitacao total diaria (mm)': 'precipitacao media mensal (mm)'}, inplace=True)

    # Meses mais secos
    meses_secos = mensal.sort_values(
        by='precipitacao media mensal (mm)').head(6)

    # Verifica se os meses secos são contínuos
    ano_tipo, bloco_meses = eh_continuo(meses_secos['mês'].tolist())
    if ano_tipo:
        metodologia = "Ano hidrológico"
        inicio_hidrologico = bloco_meses[-1] % 12 + 1
    else:
        metodologia = "Ano civil"
        inicio_hidrologico = 1

    return mensal, meses_secos, metodologia, inicio_hidrologico


def ler_dados(dados: str) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Leitura de dados do arquivo CSV do BDMEP e extração do cabeçalho.

    :param dados: Caminho para o arquivo CSV da da base de dados BDMEP

    :return: [0] = Metadados do arquivo de dados BDMEP (cidade, lat, long, alt, ..., etc), [1] = Médias mensais de precipitação, [2] = Meses mais secos, [3] = Dados meteorológicos base BDMEP ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico') 
    """

    # Organização colunas
    with open(dados, 'r', encoding='utf-8') as f:
        linhas = [next(f).strip() for _ in range(9)]
        cabecalho = {}
        for linha in linhas:
            if ':' in linha:
                chave, valor = linha.split(':', 1)
                chave_formatada = chave.strip().lower().replace(' ', '_')
                valor = valor.strip()
                if chave_formatada in ['latitude', 'longitude', 'altitude']:
                    valor = float(valor)
                elif chave_formatada in ['data_inicial', 'data_final']:
                    valor = datetime.strptime(valor, '%Y-%m-%d').date()
                cabecalho[chave_formatada] = valor
    df = pd.read_csv(dados, sep=";", encoding="utf-8", skiprows=9)
    df.drop(columns=['Unnamed: 5'], inplace=True, errors='ignore')
    df.columns = ['data medicao', 'precipitacao total diaria (mm)', 'temperatura media diaria (°C)',
                  'umidade relativa ar media diaria (%)', 'velocidade vento media diaria (m/s)']
    df['data medicao'] = pd.to_datetime(df['data medicao'], errors='coerce')
    df.drop(columns=['temperatura media diaria (°C)', 'umidade relativa ar media diaria (%)',
            'velocidade vento media diaria (m/s)'], inplace=True)
    df['ano civil'] = df['data medicao'].dt.year
    df['mês'] = df['data medicao'].dt.month

    # Filtragem para eliminação de dados incompletos que prejudicam a análise estatística
    df_final = []
    ano_inicial = cabecalho['data_inicial'].year
    ano_final = cabecalho['data_final'].year
    anos_existentes = list(range(ano_inicial, ano_final + 1))
    for ano in anos_existentes:
        df_ano = df[df['ano civil'] == ano]
        mes_unicos = df_ano['mês'].unique().tolist()
        for mes in mes_unicos:
            df_filtrado = df_ano[df_ano['mês'] == mes]
            tem_nan = df_filtrado['precipitacao total diaria (mm)'].isna(
            ).any()
            if tem_nan:
                pass
            else:
                df_final.append(df_filtrado)

    df_final = pd.concat(df_final)
    df_final.reset_index(drop=True, inplace=True)
    print(df_final)
    # Definição dos anos hidrológicos ou civis
    mensal, meses_secos, metodologia, inicio_hidrologico = definicao_ano_hidrologico(df_final)
    cabecalho['metodologia_ano'] = metodologia
    cabecalho['mes_inicio_ano_hidrologico'] = inicio_hidrologico

    print(metodologia)
    # Marcação do ano hidrológico no DataFrame final
    if metodologia != "Ano hidrológico":
        anos = df_final['ano civil'].unique().tolist()
        for i, ano in enumerate(anos):
            mask = df_final['ano civil'] == ano
            df_final.loc[mask, 'ano hidrologico'] = int(i+1)
    else:
        df_final['ano hidrologico'] = np.where(
            df_final['mês'] >= inicio_hidrologico,
            df_final['ano civil'] + 1,
            df_final['ano civil']
        )

    anos = df_final['ano hidrologico'].unique().tolist()
    total_anos = len(anos)
    cabecalho['total_anos_em_dados'] = total_anos

    return cabecalho, mensal, meses_secos, df_final


def calcular_precipitacao_maxima_diaria(df_final: pd.DataFrame) -> pd.DataFrame:
    """Preciptação máxima diária em função do ano hidrológico ou civil.

    :param df_final: Dados meteorológicos base BDMEP ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico')

    :return: Maiores precipitações diárias por ano hidrológico ou civil
    """

    # Limpeza e formatação dos dados
    df_final['precipitacao total diaria (mm)'] = pd.to_numeric(
        df_final['precipitacao total diaria (mm)'], errors='coerce')

    # Extração da média e desvio padrão das maiores precipitações anuais
    maiores_precipitacoes_por_ano = df_final.groupby(
        'ano hidrologico')['precipitacao total diaria (mm)'].max().reset_index()
    maiores_precipitacoes_por_ano.rename(columns={
                                         'precipitacao total diaria (mm)': 'precipitacao máxima anual (mm)'}, inplace=True)

    # Retirando valores zerados
    maiores_precipitacoes_por_ano = maiores_precipitacoes_por_ano[
        maiores_precipitacoes_por_ano['precipitacao máxima anual (mm)'] > 0]
    maiores_precipitacoes_por_ano.reset_index(drop=True, inplace=True)

    return maiores_precipitacoes_por_ano


def checar_gev_adequada(maiores_precipitacoes_por_ano: pd.DataFrame) -> tuple[float, float, float, list]:
    """Checa os parâmetros da distribuição GEV para as maiores precipitações anuais.

    :param maiores_precipitacoes_por_ano: Maiores precipitações diárias por ano hidrológico ou civil

    :return: [0] = Parâmetro de forma c, [1] = Parâmetro de localização loc, [2] = Parâmetro de escala scale, [3] = Dados GEV para plotagem
    """

    x = pd.to_numeric(maiores_precipitacoes_por_ano['precipitacao máxima anual (mm)'], errors="coerce").dropna(
    ).to_numpy(dtype=float)
    x = x[x > 0.0]
    c, loc, scale = sc.stats.genextreme.fit(x)
    dist = sc.stats.genextreme(c, loc=loc, scale=scale)
    gev_amostras = dist.rvs(size=100)
    gev_amostras = np.maximum(gev_amostras, 0.0)

    return float(c), float(loc), float(scale), gev_amostras


def calcular_hmax_gev(c: float, loc: float, scale: float) -> pd.DataFrame:
    """Cálculo da preciptação máxima diária em função do período de retorno usando uma distribuição GEV.

    :param c: Parâmetro de forma da distribuição GEV
    :param loc: Parâmetro de localização da distribuição GEV
    :param scale: Parâmetro de escala da distribuição GEV

    :return: Precipitação máxima diária (mm) em função do período de retorno (anos)
    """

    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    p = 1 - 1/np.array(Tr_list, dtype=float)
    x_Tr = sc.stats.genextreme.ppf(p, c, loc=loc, scale=scale)
    p_exec = 1/np.array(Tr_list, dtype=float)
    df_hmax1 = pd.DataFrame(
        {"t_r (anos)": Tr_list, "1/Tr": p_exec, "h_max,1 (mm)": x_Tr})

    return df_hmax1


def calcular_hmax(params: tuple, dist_tipo) -> pd.DataFrame:
    """
    """
    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    p = 1 - 1/np.array(Tr_list, dtype=float)
    p_exec = 1/np.array(Tr_list, dtype=float)
    if dist_tipo == 'genextreme':
        c, loc, scale = params
        x_Tr = sc.stats.genextreme.ppf(p, c, loc=loc, scale=scale)
    elif dist_tipo == 'gumbel_r':
        c, loc, scale = params
        x_Tr = sc.stats.gumbel_r.ppf(p, loc=loc, scale=scale)
    elif dist_tipo == 'gumbel_l':
        c, loc, scale = params
    elif dist_tipo == 'norm':
        c, loc, scale = params
    elif dist_tipo == 'lognorm':
        c, loc, scale = params
    elif dist_tipo == 'weibull_min':
        c, loc, scale = params
    else:
        raise ValueError("Distribuição não suportada.")

    return pd.DataFrame({"t_r (anos)": Tr_list, "1/Tr": p_exec, "h_max,1 (mm)": x_Tr})


def calcular_hmax_gumbel_erivan(mu, sigma, tr):
    """Cálculo da preciptação máxima diária em função do período de retorno usando uma distribuição GEV

    :param mu Média das máximas precipitações anuais (mm).
    :param sigma: Desvio padrão das máximas precipitações anuais (mm).
    :param tr: Período de retorno (anos).

    :return: Precipitação máxima diária (mm) em função do período de retorno (anos).
    """

    return mu - sigma * (0.45 + 0.7797 * np.log(np.log(tr / (tr - 1))))


def desagragacao_preciptacao_maxima_diaria_matriz_intensidade_chuva(h_max1):
    """
    Desagregação da precipitação máxima diária (mm) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos para matriz de intensidade de chuva (mm/h)

    :param h_max1: Precipitação máxima diária (mm) em função do período de retorno (anos).

    :return: Matriz de intensidade de chuva (mm/h) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos.
    """

    tc_list = [1440, 720, 600, 480, 360, 180, 60, 30, 25, 20, 15, 10, 5]
    tc_convert = [1.14, 0.85, 0.78, 0.72, 0.54, 0.48,
                  0.42, 0.74, 0.91, 0.81, 0.70, 0.54, 0.34]
    i_convert = [1/24, 1/12, 1/8, 1/6, 1/3, 1/2, 1, 1 /
                 (30/60), 1/(25/60), 1/(20/60), 1/(15/60), 1/(10/60), 1/(5/60)]
    tr = []
    tc = []
    y = []
    for index, row in h_max1.iterrows():
        y_aux = []
        for i, value in enumerate(tc_convert):
            tr.append(row['t_r (anos)'])
            tc.append(tc_list[i])
            if i == 0:
                y_aux.append(row['h_max,1 (mm)'] * value)
            elif i > 0 and i <= 6:
                y_aux.append(y_aux[0] * value)
            elif i == 7:
                y_aux.append(y_aux[6] * value)
            else:
                y_aux.append(y_aux[7] * value)
        y_aux = [a * b for a, b in zip(y_aux, i_convert)]
        y += y_aux
    matriz_intensidade = {'t_c (min)': tc, 't_r (anos)': tr, 'y_obs (mm/h)': y}

    return pd.DataFrame(matriz_intensidade)


def calculo_precipitacoes(df: pd.DataFrame, metadados: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processa dados de precipitação bruta para gerar preciptação máxima diária e precipitações em mm/h em diferentes períodos de retorno e tempos de concentração.

    :param df: Dados meteorológicos base BDMEP ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico') 
    :param metadados: Metadados do arquivo de dados BDMEP (cidade, lat, long, alt, ..., etc)

    :return: saida[0] = Precipitação máxima diária (mm) em função do período de retorno (anos), saida[1] = Matriz de intensidade de chuva (mm/h) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos.
    """

    # Limpeza e formatação dos dados
    df['precipitacao total diaria (mm)'] = pd.to_numeric(
        df['precipitacao total diaria (mm)'], errors='coerce')

    # Extração da média e desvio padrão das maiores precipitações anuais
    hmax1d = calcular_precipitacao_maxima_diaria(df)
    c, loc, scale, _ = checar_gev_adequada(hmax1d)

    # Altura máxima em 1 dia para diferentes períodos de retorno
    df_hmax1 = calcular_hmax_gev(c, loc, scale)

    # Desagregação da precipitação máxima diária em matriz de intensidade de chuva (mm/h)
    matriz_chuva = desagragacao_preciptacao_maxima_diaria_matriz_intensidade_chuva(
        df_hmax1)
    matriz_chuva['latitude'] = metadados['latitude']
    matriz_chuva['longitude'] = metadados['longitude']
    matriz_chuva['altitude'] = metadados['altitude']
    matriz_chuva['cidade'] = metadados['nome']

    return df_hmax1, matriz_chuva
