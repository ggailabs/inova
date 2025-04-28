from fastapi import FastAPI
import pandas as pd

app = FastAPI()

URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

df_solo = pd.read_csv(URL_SOLO, sep=';')
df_meteo = pd.read_csv(URL_METEO, sep=';')

@app.get("/consultar_meteorologia")
def consultar_meteorologia(data: str, hora: str):
    hora_formatada = hora.zfill(4)  # Garante 4 dígitos
    filtro = df_meteo[
        (df_meteo['Data'].str.strip() == data) &
        (df_meteo['Hora (UTC)'].astype(str).str.zfill(4) == hora_formatada)
    ]
    if filtro.empty:
        return {"erro": f"Sem dados para {data} às {hora_formatada}h"}
    row = filtro.iloc[0]
    return {
        "data": data,
        "hora": hora_formatada,
        "temperatura": row['Temp. Ins. (C)'],
        "umidade": row['Umi. Ins. (%)'],
        "chuva": row['Chuva (mm)']
    }

@app.get("/consultar_analise_solo")
def consultar_analise_solo():
    if df_solo.empty:
        return {"erro": "Sem dados de análise de solo disponíveis"}
    # Pega sempre o Ponto 1, 0 a 20 cm
    filtro = df_solo[(df_solo['Ponto'] == 1) & (df_solo['Profundidade'] == "0 a 20 cm")]
    if filtro.empty:
        filtro = df_solo.iloc[0]  # Se não achar, pega o primeiro disponível
    else:
        filtro = filtro.iloc[0]
    return {
        "talhao": filtro['Talhão'],
        "ponto": filtro['Ponto'],
        "profundidade": filtro['Profundidade'],
        "pH": filtro['pH CaCl2'],
        "MO": filtro['M.O. [g/dm³]'],
        "P": filtro['P (r) [mg/dm³]'],
        "K": filtro['K [mmolc/dm³]']
    }
