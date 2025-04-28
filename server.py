from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# URLs dos CSVs
URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

df_solo = pd.read_csv(URL_SOLO, sep=';')
df_meteo = pd.read_csv(URL_METEO, sep=';')

@app.get("/consultar_meteorologia")
def consultar_meteorologia(data: str, hora: str):
    filtro = df_meteo[(df_meteo['Data'] == data) & (df_meteo['Hora (UTC)'] == hora)]
    if filtro.empty:
        return {"erro": f"Sem dados para {data} às {hora}h"}
    row = filtro.iloc[0]
    return {
        "data": data,
        "hora": hora,
        "temperatura": row['Temp. Ins. (C)'],
        "umidade": row['Umi. Ins. (%)'],
        "chuva": row['Chuva (mm)']
    }

@app.get("/consultar_analise_solo")
def consultar_analise_solo(talhao: str):
    if 'Talhão' not in df_solo.columns:
        return {"erro": "Coluna 'Talhão' não encontrada"}
    filtro = df_solo[df_solo['Talhão'] == talhao]
    if filtro.empty:
        return {"erro": f"Sem análise para o talhão {talhao}"}
    row = filtro.iloc[0]
    return {
        "talhao": talhao,
        "pH": row.get('pH', 'N/A'),
        "MO": row.get('MO', 'N/A'),
        "P": row.get('P', 'N/A'),
        "K": row.get('K', 'N/A')
    }
