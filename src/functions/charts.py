import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'axes.unicode_minus': False
})

_PLOT_CONFIG = {
    'width_cm': 12,
    'height_cm': 10,
    'inches_per_cm': 1 / 2.54,
    'label_size': 14,
    'axis_size': 14,
    'legend_size': 10,
    'alpha': 0.4,
}


def _get_fig_size() -> tuple[float, float]:
    cfg = _PLOT_CONFIG
    width_in = cfg['width_cm'] * cfg['inches_per_cm']
    height_in = cfg['height_cm'] * cfg['inches_per_cm']
    return width_in, height_in


def plot_monthly_average_precipitation(output_folder: str, name: str, monthly: pd.DataFrame, rainy_season_start: int = 1, lang: str = 'pt'):
    labels = {
        'pt': {
            'xlabel': 'Mês',
            'ylabel': 'Precipitação média mensal (mm)',
            'driest': 'Mês mais seco',
            'wettest': 'Mês mais chuvoso',
            'rainy_start': 'Início do período chuvoso',
            'filename': f'z_monthly_avg_precipitation_{name}_pt.png'
        },
        'en': {
            'xlabel': 'Month',
            'ylabel': 'Average precipitation (mm)',
            'driest': 'Driest month',
            'wettest': 'Wettest month',
            'rainy_start': 'Start of rainy season',
            'filename': f'z_monthly_avg_precipitation_{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.plot(monthly['mes'], monthly['precipitacao media mensal (mm)'],
            marker='o', color='red')

    driest_idx = monthly['precipitacao media mensal (mm)'].idxmin()
    driest_month = driest_idx + 1
    ax.scatter(driest_month, monthly['precipitacao media mensal (mm)'][driest_idx],
               s=140, label=f"{labels[lang]['driest']} = {driest_month}", color='blue')

    wettest_idx = monthly['precipitacao media mensal (mm)'].idxmax()
    wettest_month = wettest_idx + 1
    ax.scatter(wettest_month, monthly['precipitacao media mensal (mm)'][wettest_idx],
               s=140, label=f"{labels[lang]['wettest']} = {wettest_month}", color='green')

    ax.axvline(x=rainy_season_start, color='purple', linestyle='--', linewidth=2.0,
               alpha=0.7, label=f"{labels[lang]['rainy_start']} = {rainy_season_start}")
    ax.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['ylabel'], fontsize=cfg['label_size'])
    ax.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax.grid(True, alpha=cfg['alpha'])
    ax.legend(fontsize=cfg['legend_size'], loc='lower center',
              bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600)

    return fig


def plot_pdf_daily_max_precipitation(output_folder: str, name: str, data: pd.DataFrame, lang: str = 'pt'):
    import scipy.stats as stats

    labels = {
        'pt': {
            'ylabel': 'Densidade',
            'xlabel': r'$i_{max,anual}$ (mm)',
            'legend': ['dados', 'melhor distribuição'],
            'filename': f'{name}_pt.png'
        },
        'en': {
            'ylabel': 'Density',
            'xlabel': r'$i_{max,annual}$ (mm)',
            'legend': ['data', 'best distribution'],
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    colors = ['blue', 'red']

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.tick_params(axis='both', which='major',
                   labelsize=cfg['axis_size'], colors='black')
    ax.set_xlabel(labels[lang]['xlabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.set_ylabel(labels[lang]['ylabel'],
                  fontsize=cfg['label_size'], color='black')
    plt.grid(True, which='both', linestyle='-',
             linewidth=0.2, alpha=cfg['alpha'])

    for col, color, label in [
        ('real', colors[0], labels[lang]['legend'][0]),
        ('numerica', colors[1], labels[lang]['legend'][1])
    ]:
        values = data[col].dropna().values
        kde = stats.gaussian_kde(values)
        x_range = np.linspace(values.min(), values.max(), 500)
        y_kde = kde(x_range)
        ax.plot(x_range, y_kde, color=color, label=label)
        ax.fill_between(x_range, y_kde, alpha=cfg['alpha'], color=color)

    plt.legend(fontsize=cfg['legend_size'], loc='lower center',
               bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig


def plot_cdf_daily_max_precipitation(output_folder: str, name: str, data: dict, lang: str = 'pt'):
    labels = {
        'pt': {
            'xlabel': r'$i_{max,anual}$ (mm)',
            'ylabel': 'Probabilidade acumulada',
            'legend': ['dados', 'melhor distribuição'],
            'filename': f'{name}_pt.png'
        },
        'en': {
            'xlabel': r'$i_{max,annual}$ (mm)',
            'ylabel': 'Cumulative probability',
            'legend': ['data', 'best distribution'],
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    colors = ['blue', 'red']

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.scatter(data['real']['x'], data['real']['y'],
               label=labels[lang]['legend'][0], color=colors[0], s=30)
    ax.plot(data['numerica']['x'], data['numerica']['y'],
            label=labels[lang]['legend'][1], color=colors[1], linewidth=2)
    ax.set_xlabel(labels[lang]['xlabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.set_ylabel(labels[lang]['ylabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.tick_params(axis='both', which='major',
                   labelsize=cfg['axis_size'], colors='black')
    plt.grid(True, linestyle='-', linewidth=0.2, alpha=cfg['alpha'])
    plt.legend(fontsize=cfg['legend_size'], loc='lower center',
               bbox_to_anchor=(0.5, 1.02), frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig


def plot_idf_curves(output_folder: str, name: str, lang: str, rainfall_matrix: pd.DataFrame):
    labels = {
        'pt': {
            'x_label': 'Tempo de Duração (min)',
            'y_label': 'Intensidade (mm/h)',
            'title': 'Tempo de Retorno (anos)',
            'filename': f'{name}_pt.png'
        },
        'en': {
            'x_label': 'Duration Time (min)',
            'y_label': 'Intensity (mm/h)',
            'title': 'Return Period (years)',
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    return_periods = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    for period in return_periods:
        filtered = rainfall_matrix[rainfall_matrix['t_r (anos)'] == period]
        ax.plot(filtered['t_c (min)'], filtered['y_obs (mm/h)'],
                linewidth=2.8, marker='o', label=period)
    ax.set_xlabel(labels[lang]['x_label'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['y_label'], fontsize=cfg['label_size'])
    ax.grid(True, which="both", linestyle="--", alpha=cfg['alpha'])
    ax.legend(ncol=2, title=labels[lang]['title'], fontsize=cfg['legend_size'])
    plt.tight_layout()

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig


def plot_spi(output_folder: str, name: str, dataset: pd.DataFrame, lang: str = 'pt'):
    """Plot SPI-1 time series with color bands by drought/wet category.

    :param output_folder: Folder to save the chart (None to skip saving)
    :param name: Station name/id for file naming
    :param dataset: DataFrame with 'ano civil', 'mes' and 'SPI_1' columns
    :param lang: 'pt' or 'en'
    """

    labels = {
        'pt': {
            'ylabel': 'SPI-1',
            'xlabel': 'Data',
            'filename': f'{name}_spi_pt.png',
            'seco_extremo': 'Seco extremo',
            'seco_severo': 'Seco severo',
            'seco_moderado': 'Seco moderado',
            'umido_moderado': 'Úmido moderado',
            'umido_severo': 'Úmido severo',
            'umido_extremo': 'Úmido extremo',
        },
        'en': {
            'ylabel': 'SPI-1',
            'xlabel': 'Date',
            'filename': f'{name}_spi_en.png',
            'seco_extremo': 'Extreme dry',
            'seco_severo': 'Severe dry',
            'seco_moderado': 'Moderate dry',
            'umido_moderado': 'Moderate wet',
            'umido_severo': 'Severe wet',
            'umido_extremo': 'Extreme wet',
        }
    }

    cfg = _PLOT_CONFIG
    width_in = 28 * cfg['inches_per_cm']
    height_in = 10 * cfg['inches_per_cm']

    df = dataset.copy()
    df['date'] = pd.to_datetime(
        df['ano civil'].astype(str) + '-' + df['mes'].astype(str) + '-01'
    )
    df = df.sort_values('date').dropna(subset=['SPI_1'])

    fig, ax = plt.subplots(figsize=(width_in, height_in))

    # Color bands
    ax.axhspan(-4, -2.0, alpha=0.08, color='darkred',
               label=labels[lang]['seco_extremo'])
    ax.axhspan(-2.0, -1.5, alpha=0.08, color='red',
               label=labels[lang]['seco_severo'])
    ax.axhspan(-1.5, -1.0, alpha=0.08, color='orange',
               label=labels[lang]['seco_moderado'])
    ax.axhspan(1.0,  1.5,  alpha=0.08, color='lightblue',
               label=labels[lang]['umido_moderado'])
    ax.axhspan(1.5,  2.0,  alpha=0.08, color='blue',
               label=labels[lang]['umido_severo'])
    ax.axhspan(2.0,  4.0,  alpha=0.08, color='darkblue',
               label=labels[lang]['umido_extremo'])

    # Zero line
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)

    # Fill positive/negative areas
    ax.fill_between(df['date'], df['SPI_1'], 0,
                    where=df['SPI_1'] >= 0, interpolate=True,
                    color='steelblue', alpha=0.6)
    ax.fill_between(df['date'], df['SPI_1'], 0,
                    where=df['SPI_1'] < 0, interpolate=True,
                    color='sienna', alpha=0.6)

    ax.plot(df['date'], df['SPI_1'], color='black', linewidth=0.6)

    ax.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['ylabel'], fontsize=cfg['label_size'])
    ax.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax.grid(True, alpha=cfg['alpha'])
    ax.legend(fontsize=cfg['legend_size'], loc='lower center',
              bbox_to_anchor=(0.5, 1.02), ncol=6, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.92])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder, labels[lang]['filename']),
                    dpi=600, bbox_inches='tight')

    return fig


def plot_spi_vs_commodities(output_folder: str, name: str, lang: str, spi_df: pd.DataFrame, comm_dataframes: dict, selected_uf: str):
    labels = {
        'pt': {
            'xlabel': 'Data',
            'ylabel1': 'SPI-1 (Normalizado)',
            'ylabel2': 'Preço Histórico (Normalizado)',
            'filename': f'{name}_spi_commodities_pt.png'
        },
        'en': {
            'xlabel': 'Date',
            'ylabel1': 'SPI-1 (Normalized)',
            'ylabel2': 'Historical Price (Normalized)',
            'filename': f'{name}_spi_commodities_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in = 22 * cfg['inches_per_cm']
    height_in = 10 * cfg['inches_per_cm']

    fig, ax1 = plt.subplots(figsize=(width_in, height_in))

    # Eixo 1: SPI
    ax1.plot(spi_df['data medicao'], spi_df['SPI_1_norm'], color='#003366',
             linewidth=2, linestyle='--', label='SPI-1 (Estação)')

    ax1.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax1.set_ylabel(labels[lang]['ylabel1'],
                   fontsize=cfg['label_size'], color='#003366')
    ax1.tick_params(axis='y', labelcolor='#003366', labelsize=cfg['axis_size'])
    ax1.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax1.grid(True, linestyle="--", alpha=cfg['alpha'])

    # Eixo 2: Commodities
    ax2 = ax1.twinx()
    ax2.set_ylabel(labels[lang]['ylabel2'],
                   fontsize=cfg['label_size'], color='black')

    cores = ['#d62728', '#2ca02c', '#ff7f0e', '#9467bd', '#e377c2', '#8c564b']
    for idx, (comm_name, df_comm) in enumerate(comm_dataframes.items()):
        cor = cores[idx % len(cores)]
        ax2.plot(df_comm['data medicao'], df_comm[f'{comm_name}_norm'],
                 color=cor, linewidth=2, label=f'{comm_name}')

    ax2.tick_params(axis='y', labelsize=cfg['axis_size'])

    # Legenda Superior Unificada
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower center',
               bbox_to_anchor=(0.5, 1.02), ncol=len(lines_1 + lines_2), frameon=True, fontsize=cfg['legend_size'])

    fig.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig
