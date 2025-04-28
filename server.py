# server.py
import re
import pandas as pd
from mcp.server.fastmcp import FastMCP, Context

# Inicializa o MCP
mcp = FastMCP("MVP_INOVA_MCP")
print(f"Servidor MCP '{mcp.name}' inicializado.")

# URLs dos CSVs hospedados
URL_SOLO = 'https://inova.ggailabs.com/dados/CA01.csv'
URL_METEO = 'https://inova.ggailabs.com/dados/dados.csv'

# Carregar os dados direto da URL
df_solo = pd.read_csv(URL_SOLO, sep=';')
df_meteo = pd.read_csv(URL_METEO, sep=';')

# --- TOOL: Consulta Meteorológica ---
@mcp.tool()
def consultar_meteorologia(data: str, hora: str) -> str:
    """Consulta dados climáticos por data e hora."""
    filtro = df_meteo[(df_meteo['Data'] == data) & (df_meteo['Hora (UTC)'] == hora)]
    if filtro.empty:
        return f"Sem dados para {data} às {hora}h."
    row = filtro.iloc[0]
    return (
        f"🌤️ Clima em {data} às {hora}h:\n"
        f"Temperatura: {row['Temp. Ins. (C)']}°C\n"
        f"Umidade: {row['Umi. Ins. (%)']}%\n"
        f"Chuva: {row['Chuva (mm)']} mm\n"
        f"Vento: {row['Vel. Vento (m/s)']} m/s"
    )

# --- TOOL: Consulta Análise de Solo ---
@mcp.tool()
def consultar_analise_solo(talhao: str) -> str:
    """Consulta análise de solo pelo talhão."""
    if 'Talhão' not in df_solo.columns:
        return "Arquivo de solo não possui coluna 'Talhão'."
    filtro = df_solo[df_solo['Talhão'] == talhao]
    if filtro.empty:
        return f"Sem análise encontrada para o talhão {talhao}."
    row = filtro.iloc[0]
    return (
        f"🌱 Análise do Talhão {talhao}:\n"
        f"pH: {row.get('pH', 'N/A')}\n"
        f"Matéria Orgânica: {row.get('MO', 'N/A')}\n"
        f"P: {row.get('P', 'N/A')} mg/dm³\n"
        f"K: {row.get('K', 'N/A')} cmolc/dm³"
    )

# --- TOOL: Recomendação de Adubação ---
@mcp.tool()
def recomendar_adubacao_basica(talhao: str) -> str:
    """Sugere adubação simples com base no pH."""
    if 'Talhão' not in df_solo.columns:
        return "Arquivo de solo não possui coluna 'Talhão'."
    filtro = df_solo[df_solo['Talhão'] == talhao]
    if filtro.empty:
        return f"Nenhuma análise para o talhão {talhao}."
    row = filtro.iloc[0]
    ph = float(str(row.get('pH', '0')).replace(',', '.'))
    if ph < 5.5:
        return f"Recomenda-se calagem no talhão {talhao}, pH atual: {ph}."
    return f"pH do talhão {talhao} está adequado ({ph}). Adubação nitrogenada leve recomendada."

# --- Roda o servidor ---
if __name__ == "__main__":
    mcp.run()
