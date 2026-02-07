## 1. How to Set Up a Python Virtual Environment and Install Requirements to use METApy locally

#### 1.1 Create the virtual environment (depends on your installation)
```bash
python3 -m venv myenv
# or
python -m venv myenv
# or
python3.10 -m venv myenv
```


#### 1.2 Activate the virtual environment  
```bash
 # On Linux or macOS
myenv\Scripts\activate    # On Windows
```


#### 1.3 Install required packages
```bash
pip install -r requirements.txt
```


#### 1.4 To deactivate the virtual environment
```bash
deactivate
```

## 2. Use pip-chill to manage your requirements.txt file  
  
#### 2.1 To install any packages or packages which are outside of requirements.txt
```bash
pip install your_package
```

#### 2.2 After installation, update the requirements.txt file
```bash
pip-chill > requirements.txt
```

## 3. Run streamlit
```bash
streamlit run app.py
```

## 4. Sharepoint in Google Drive
