from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
from typing import Dict, List, Union

app = FastAPI()

# URLs dos dados
URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

# Carregar os dados com tratamento de erros
try:
    df_solo = pd.read_csv(URL_SOLO, sep=';', decimal=',', encoding='utf-8')
    # Limpeza e preparação dos dados
    df_solo = df_solo.apply(lambda x: x.str.strip('"') if x.dtype == 'object' else x)
    df_solo['Ponto'] = df_solo['Ponto'].astype(str).str.strip()
    df_solo['Profundidade'] = df_solo['Profundidade'].astype(str).str.strip()
    # Converter colunas numéricas
    numeric_cols = ['P (r) [mg/dm³]', 'M.O. [g/dm³]', 'pH CaCl2', 'K [mmolc/dm³]', 
                   'Ca [mmolc/dm³]', 'Mg [mmolc/dm³]', 'C.T.C. [mmolc/dm³]', 'V% [%]',
                   'S [mg/dm³]', 'B [mg/dm³]', 'K na CTC [%]', 'Ca na CTC [%]', 
                   'Mg na CTC [%]', 'Argila [g/kg]']
    for col in numeric_cols:
        if col in df_solo.columns:
            df_solo[col] = pd.to_numeric(df_solo[col].astype(str).str.replace(',', '.'), errors='coerce')
except Exception as e:
    df_solo = pd.DataFrame()
    print(f"Erro ao carregar dados de solo: {str(e)}")

try:
    df_meteo = pd.read_csv(URL_METEO, sep=';')
except Exception as e:
    df_meteo = pd.DataFrame()
    print(f"Erro ao carregar dados meteorológicos: {str(e)}")

@app.get("/solo/opcoes")
def listar_opcoes_solo() -> Dict[str, List[Union[str, int]]]:
    """Retorna os pontos e profundidades disponíveis para consulta"""
    try:
        if df_solo.empty:
            return JSONResponse(
                status_code=503,
                content={"erro": "Dados de solo não disponíveis no momento"}
            )
        
        pontos = sorted(df_solo['Ponto'].unique().tolist())
        profundidades = sorted(df_solo['Profundidade'].unique().tolist())
        
        return {
            "pontos_disponiveis": pontos,
            "profundidades_disponiveis": profundidades,
            "exemplo_uso": "/solo?ponto=1&profundidade=0 a 20 cm"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": f"Erro ao listar opções: {str(e)}"}
        )

@app.get("/solo")
def consultar_analise_solo(ponto: int, profundidade: str = "0 a 20 cm") -> Dict[str, Union[str, float]]:
    """Consulta os dados de análise de solo para um ponto e profundidade específicos"""
    try:
        if df_solo.empty:
            return JSONResponse(
                status_code=503,
                content={"erro": "Dados de solo não disponíveis no momento"}
            )

        # Converter para string para comparação
        ponto_str = str(ponto)
        
        # Filtrar os dados
        filtro = df_solo[
            (df_solo['Ponto'] == ponto_str) & 
            (df_solo['Profundidade'] == profundidade.strip())
        ]

        if filtro.empty:
            # Sugerir opções disponíveis
            opcoes = listar_opcoes_solo()
            return JSONResponse(
                status_code=404,
                content={
                    "erro": f"Nenhum dado encontrado para Ponto {ponto} e Profundidade '{profundidade}'",
                    "opcoes_disponiveis": opcoes
                }
            )

        row = filtro.iloc[0].to_dict()

        # Preparar resposta
        response_data = {
            "talhao": row.get('Talhão', 'N/A'),
            "ponto": row.get('Ponto', 'N/A'),
            "profundidade": row.get('Profundidade', 'N/A'),
            "parametros": {
                "pH_CaCl2": row.get('pH CaCl2'),
                "materia_organica": row.get('M.O. [g/dm³]'),
                "fosforo": row.get('P (r) [mg/dm³]'),
                "potassio": row.get('K [mmolc/dm³]'),
                "calcio": row.get('Ca [mmolc/dm³]'),
                "magnesio": row.get('Mg [mmolc/dm³]'),
                "ctc": row.get('C.T.C. [mmolc/dm³]'),
                "saturacao_bases": row.get('V% [%]'),
                "enxofre": row.get('S [mg/dm³]'),
                "boro": row.get('B [mg/dm³]'),
                "k_ctc": row.get('K na CTC [%]'),
                "ca_ctc": row.get('Ca na CTC [%]'),
                "mg_ctc": row.get('Mg na CTC [%]'),
                "argila": row.get('Argila [g/kg]')
            },
            "unidades": {
                "pH_CaCl2": "pH",
                "materia_organica": "g/dm³",
                "fosforo": "mg/dm³",
                "potassio": "mmolc/dm³",
                "calcio": "mmolc/dm³",
                "magnesio": "mmolc/dm³",
                "ctc": "mmolc/dm³",
                "saturacao_bases": "%",
                "enxofre": "mg/dm³",
                "boro": "mg/dm³",
                "k_ctc": "%",
                "ca_ctc": "%",
                "mg_ctc": "%",
                "argila": "g/kg"
            }
        }

        # Remover valores nulos
        response_data["parametros"] = {k: v for k, v in response_data["parametros"].items() if pd.notnull(v)}
        
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
