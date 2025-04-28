from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse

app = FastAPI()

# URLs dos dados
URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

# Carregar os dados com tratamento de erros
try:
    df_solo = pd.read_csv(URL_SOLO, sep=';', decimal=',', encoding='utf-8')
    # Remover aspas extras e limpar os dados
    df_solo = df_solo.apply(lambda x: x.str.strip('"') if x.dtype == 'object' else x)
    df_solo['Ponto'] = df_solo['Ponto'].astype(str).str.strip()
    df_solo['Profundidade'] = df_solo['Profundidade'].astype(str).str.strip()
except Exception as e:
    df_solo = pd.DataFrame()
    print(f"Erro ao carregar dados de solo: {str(e)}")

try:
    df_meteo = pd.read_csv(URL_METEO, sep=';')
except Exception as e:
    df_meteo = pd.DataFrame()
    print(f"Erro ao carregar dados meteorológicos: {str(e)}")

@app.get("/solo")
def consultar_analise_solo(ponto: int = 1, profundidade: str = "0 a 20 cm"):
    try:
        if df_solo.empty:
            return JSONResponse(
                status_code=503,
                content={"erro": "Dados de solo não disponíveis no momento"}
            )

        # Verificar se o ponto existe
        pontos_disponiveis = df_solo['Ponto'].unique()
        if str(ponto) not in pontos_disponiveis:
            return JSONResponse(
                status_code=404,
                content={"erro": f"Ponto {ponto} não encontrado. Pontos disponíveis: {list(pontos_disponiveis)}"}
            )

        # Verificar se a profundidade existe
        profundidades_disponiveis = df_solo['Profundidade'].unique()
        if profundidade not in profundidades_disponiveis:
            return JSONResponse(
                status_code=400,
                content={"erro": f"Profundidade '{profundidade}' inválida. Opções disponíveis: {list(profundidades_disponiveis)}"}
            )

        # Filtrar os dados
        filtro = df_solo[
            (df_solo['Ponto'] == str(ponto)) & 
            (df_solo['Profundidade'] == profundidade)
        ]

        if filtro.empty:
            return JSONResponse(
                status_code=404,
                content={"erro": f"Nenhum dado encontrado para Ponto {ponto} e Profundidade {profundidade}"}
            )

        row = filtro.iloc[0].to_dict()

        # Converter valores numéricos
        def convert_value(value):
            if isinstance(value, str):
                return float(value.replace(',', '.')) if ',' in value else value
            return value

        response_data = {
            "talhao": row.get('Talhão', 'N/A'),
            "ponto": row.get('Ponto', 'N/A'),
            "profundidade": row.get('Profundidade', 'N/A'),
            "pH_CaCl2": convert_value(row.get('pH CaCl2', 'N/A')),
            "materia_organica": convert_value(row.get('M.O. [g/dm³]', 'N/A')),
            "fosforo": convert_value(row.get('P (r) [mg/dm³]', 'N/A')),
            "potassio": convert_value(row.get('K [mmolc/dm³]', 'N/A')),
            "calcio": convert_value(row.get('Ca [mmolc/dm³]', 'N/A')),
            "magnesio": convert_value(row.get('Mg [mmolc/dm³]', 'N/A')),
            "ctc": convert_value(row.get('C.T.C. [mmolc/dm³]', 'N/A')),
            "saturacao_bases": convert_value(row.get('V% [%]', 'N/A')),
            "enxofre": convert_value(row.get('S [mg/dm³]', 'N/A')),
            "boro": convert_value(row.get('B [mg/dm³]', 'N/A')),
            "k_ctc": convert_value(row.get('K na CTC [%]', 'N/A')),
            "ca_ctc": convert_value(row.get('Ca na CTC [%]', 'N/A')),
            "mg_ctc": convert_value(row.get('Mg na CTC [%]', 'N/A')),
            "argila": convert_value(row.get('Argila [g/kg]', 'N/A'))
        }

        return response_data

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": f"Erro interno ao processar análise de solo: {str(e)}"}
        )

@app.get("/meteo")
def consultar_meteorologia(data: str, hora: str):
    try:
        if df_meteo.empty:
            return JSONResponse(
                status_code=503,
                content={"erro": "Dados meteorológicos não disponíveis no momento"}
            )

        hora_formatada = str(int(hora)).zfill(4)
        df_meteo['Hora (UTC)'] = df_meteo['Hora (UTC)'].astype(str).str.zfill(4)
        
        filtro = df_meteo[
            (df_meteo['Data'].str.strip() == data) &
            (df_meteo['Hora (UTC)'] == hora_formatada)
        ]
        
        if filtro.empty:
            return JSONResponse(
                status_code=404,
                content={"erro": f"Sem dados para {data} às {hora_formatada}h"}
            )
            
        row = filtro.iloc[0]
        return {
            "data": data,
            "hora": hora_formatada,
            "temperatura": row['Temp. Ins. (C)'],
            "umidade": row['Umi. Ins. (%)'],
            "chuva": row['Chuva (mm)']
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": f"Erro interno ao processar dados meteorológicos: {str(e)}"}
        )
