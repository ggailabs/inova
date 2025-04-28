from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.responses import JSONResponse
from typing import Dict, List, Union

app = FastAPI()

# Configurações
URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

# Helper function para limpeza de dados
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e prepara o dataframe"""
    df = df.copy()
    # Remover aspas extras e espaços
    df = df.apply(lambda x: x.str.strip('"').str.strip() if x.dtype == 'object' else x)
    
    # Colunas específicas para limpeza
    if 'Ponto' in df.columns:
        df['Ponto'] = df['Ponto'].astype(str).str.strip()
    if 'Profundidade' in df.columns:
        df['Profundidade'] = df['Profundidade'].astype(str).str.strip()
    
    return df

# Carregar dados de solo com tratamento robusto
try:
    df_solo = pd.read_csv(URL_SOLO, sep=';', decimal=',', encoding='utf-8')
    df_solo = clean_data(df_solo)
    
    # Converter colunas numéricas
    numeric_cols = ['P (r) [mg/dm³]', 'M.O. [g/dm³]', 'K [mmolc/dm³]', 
                   'Ca [mmolc/dm³]', 'Mg [mmolc/dm³]', 'C.T.C. [mmolc/dm³]', 
                   'V% [%]', 'S [mg/dm³]', 'B [mg/dm³]', 'K na CTC [%]', 
                   'Ca na CTC [%]', 'Mg na CTC [%]', 'Argila [g/kg]']
    
    for col in numeric_cols:
        if col in df_solo.columns:
            # Converter para string, substituir vírgula por ponto, depois para float
            df_solo[col] = pd.to_numeric(
                df_solo[col].astype(str).str.replace(',', '.'), 
                errors='coerce'
            )
    
    # Converter pH separadamente (pode ter valores como "5,3")
    if 'pH CaCl2' in df_solo.columns:
        df_solo['pH CaCl2'] = pd.to_numeric(
            df_solo['pH CaCl2'].astype(str).str.replace(',', '.'), 
            errors='coerce'
        )

except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Erro ao carregar dados de solo: {str(e)}"
    )

@app.get("/solo/opcoes", response_model=Dict[str, Union[List[str], str]])
def listar_opcoes_solo():
    """Retorna os pontos e profundidades disponíveis para consulta"""
    try:
        if df_solo.empty:
            raise HTTPException(
                status_code=503,
                detail="Dados de solo não disponíveis no momento"
            )
        
        pontos = sorted(df_solo['Ponto'].unique().tolist())
        profundidades = sorted(df_solo['Profundidade'].unique().tolist())
        
        return {
            "pontos_disponiveis": pontos,
            "profundidades_disponiveis": profundidades,
            "exemplo_uso": "/solo?ponto=1&profundidade=0 a 20 cm"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar opções: {str(e)}"
        )

@app.get("/solo", response_model=Dict[str, Union[str, Dict[str, float]]])
def consultar_analise_solo(ponto: int, profundidade: str = "0 a 20 cm"):
    """Consulta os dados de análise de solo para um ponto e profundidade específicos"""
    try:
        ponto_str = str(ponto)
        
        filtro = df_solo[
            (df_solo['Ponto'] == ponto_str) & 
            (df_solo['Profundidade'] == profundidade.strip())
        ]
        
        if filtro.empty:
            opcoes = listar_opcoes_solo()
            raise HTTPException(
                status_code=404,
                detail={
                    "erro": f"Nenhum dado encontrado para Ponto {ponto} e Profundidade '{profundidade}'",
                    "opcoes_disponiveis": opcoes
                }
            )

        row = filtro.iloc[0].to_dict()

        # Construir resposta
        response = {
            "talhao": row.get('Talhão', 'N/A'),
            "ponto": row.get('Ponto', 'N/A'),
            "profundidade": row.get('Profundidade', 'N/A'),
            "parametros": {
                "pH_CaCl2": float(row.get('pH CaCl2', 0)),
                "materia_organica": float(row.get('M.O. [g/dm³]', 0)),
                "fosforo": float(row.get('P (r) [mg/dm³]', 0)),
                "potassio": float(row.get('K [mmolc/dm³]', 0)),
                "calcio": float(row.get('Ca [mmolc/dm³]', 0)),
                "magnesio": float(row.get('Mg [mmolc/dm³]', 0)),
                "ctc": float(row.get('C.T.C. [mmolc/dm³]', 0)),
                "saturacao_bases": float(row.get('V% [%]', 0)),
                "enxofre": float(row.get('S [mg/dm³]', 0)),
                "boro": float(row.get('B [mg/dm³]', 0)),
                "k_ctc": float(row.get('K na CTC [%]', 0)),
                "ca_ctc": float(row.get('Ca na CTC [%]', 0)),
                "mg_ctc": float(row.get('Mg na CTC [%]', 0)),
                "argila": float(row.get('Argila [g/kg]', 0))
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

        # Remover parâmetros com valor 0 (que podem ser valores padrão)
        response["parametros"] = {k: v for k, v in response["parametros"].items() if v != 0}

        return response

    except HTTPException:
        raise  # Re-lança exceções HTTP que já foram tratadas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar análise de solo: {str(e)}"
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
