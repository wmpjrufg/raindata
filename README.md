# 🌧️ RainData - Historical Precipitation Data Explorer

Web application for accessing and downloading historical precipitation data in Brazil.

## 🚀 Key Features

- **🗺️ Interactive Map:**
  - Geospatial visualization of monitoring stations across Brazil.
  - Intuitive navigation: click on a map point to view station details.
  - Zoom and pan controls (Plotly).

- **📊 Detailed Dashboard:**
  - **Dynamic Filters:** Filter by year, month, date range, and operational status.
  - **Interactive Charts:** Time-series precipitation analysis.
  - **Metadata Display:** Station code, coordinates, and status.

- **⚡ High Performance:**
  - Uses **Parquet** format for ultra-fast data loading.
  - Optimized data pipeline (CSV to Parquet conversion).

- **📥 Export:** Download filtered data in CSV format.

## 📡 Data Source

The meteorological data used in this project is extracted from **BDMEP** (Banco de Dados Meteorológicos para Ensino e Pesquisa), provided by **INMET** (National Institute of Meteorology - Brazil).

## 🛠️ Tech Stack

- **Language:** Python 3.12
- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, PyArrow
- **Visualization:** Plotly Express

## 📂 Project Structure

```text
raindata/
├── app.py                # Application entry point (Navigation)
├── convert.ipynb         # ETL Notebook (Metadata extraction & Parquet conversion)
├── pages/
│   ├── home.py           # Home Page (Map)
│   └── raindata.py       # Analysis Page (Charts & Filters)
├── rain_datasets/        # Raw input CSV files
├── metadata_estacoes.parquet # Generated metadata file
└── requirements.txt      # Project dependencies
```

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/raindata.git
   cd raindata
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Data (ETL):**
   - Place your raw `.csv` files from BDMEP in the `rain_datasets` folder.
   - Run the `convert.ipynb` notebook to generate `metadata_estacoes.parquet` and convert data to Parquet.

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 🎨 Theme

The application uses a custom dark theme with blue accents for better data visualization. Configuration is located in `.streamlit/config.toml`.
