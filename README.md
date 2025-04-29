# 🧠 Projeto AgroCultivia - Grupo 8 - Mútua Inova+

O **AgroCultivia** é um projeto desenvolvido pelo Grupo 8 com foco em soluções inovadoras utilizando inteligência artificial.

## 🚀 Visão Geral

Este repositório contém a base de um servidor Python, configurado para ser executado em um ambiente Docker, facilitando a implantação e escalabilidade de aplicações de IA.

## 🧰 Tecnologias Utilizadas

- Python
- Flask (ou outro framework web, conforme especificado em `server.py`)
- Docker
- Bibliotecas listadas em `requirements.txt`

## ⚙️ Instalação e Execução

### Pré-requisitos

- [Docker](https://www.docker.com/) instalado na máquina

### Passos

1. Clone o repositório:
   ```bash
   git clone https://github.com/ggailabs/inova.git
   cd inova
   ```
2. Construa a imagem Docker:
   ```bash
   docker build -t inova-app .
   ```
3. Execute o container:
   ```bash
   docker run -p 5000:5000 inova-app
   ```

O aplicativo estará acessível em `http://localhost:5000/` (ou na porta definida no `server.py`).

## 📂 Estrutura do Projeto

```bash
inova/
├── Dockerfile
├── requirements.txt
└── server.py
```

O **AgroCultivia** é uma API RESTful desenvolvida com FastAPI para fornecer dados de análise de solo e meteorológicos para agricultura de precisão.

### Endpoints Disponíveis

#### Análise de Solo
- `GET /solo/opcoes` - Lista pontos e profundidades disponíveis
- `GET /solo` - Retorna análise completa do solo

#### Dados Meteorológicos
- `GET /meteo` - Consulta condições climáticas

## 🔍 Detalhes dos Endpoints

### Análise de Solo

#### `GET /solo/opcoes`
**Descrição:** Lista todos os pontos e profundidades disponíveis para consulta.

**Exemplo de Resposta:**
```json
{
  "pontos_disponiveis": ["1", "2", "3"],
  "profundidades_disponiveis": ["0-20cm", "20-40cm"],
  "exemplo_uso": "/solo?ponto=1&profundidade=0-20cm"
}

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
