from fastapi import FastAPI
import pandas as pd

app = FastAPI()

URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

df_solo = pd.read_csv(URL_SOLO, sep=';')
df_meteo = pd.read_csv(URL_METEO, sep=';')

@app.get("/meteo")
def consultar_meteorologia(data: str, hora: str):
    hora_formatada = hora.zfill(4)  # Garante 4 dígitos
    filtro = df_meteo[
        (df_meteo['Data'].str.strip() == data) &
        (df_meteo['Hora (UTC)'].astype(str).str.strip().str.zfill(4) == hora_formatada)
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

@app.get("/analise_solo")
def consultar_analise_solo(ponto: int = 1):
    try:
        if df_solo.empty:
            return {"erro": "Sem dados de análise de solo disponíveis"}

        # Garantir que Ponto e Profundidade sejam strings para comparação
        df_solo['Ponto'] = df_solo['Ponto'].astype(str).str.strip()
        df_solo['Profundidade'] = df_solo['Profundidade'].astype(str).str.strip()

        # Filtra pelo ponto informado e profundidade padrão "0 a 20 cm"
        filtro = df_solo[
            (df_solo['Ponto'] == str(ponto)) & 
            (df_solo['Profundidade'] == "0 a 20 cm")
        ]

        if filtro.empty:
            return {"erro": f"Sem dados para o Ponto {ponto} na profundidade 0 a 20 cm"}

        row = filtro.iloc[0]

        return {
            "talhao": row.get('Talhão', 'N/A'),
            "ponto": row.get('Ponto', 'N/A'),
            "profundidade": row.get('Profundidade', 'N/A'),
            "pH": row.get('pH CaCl2', 'N/A'),
            "MO": row.get('M.O. [g/dm³]', 'N/A'),
            "P": row.get('P (r) [mg/dm³]', 'N/A'),
            "K": row.get('K [mmolc/dm³]', 'N/A')
        }
    except Exception as e:
        return {"erro": f"Erro ao processar análise de solo: {str(e)}"}

