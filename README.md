# 🌱 Weedle API

API para análise de KPIs e métricas de negócio com algoritmos de Machine Learning para segmentação de clientes.

## 🚀 Link de Produção

**API em Produção:** [https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/](https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/)

**Documentação Interativa:** [https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/docs](https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/docs)

## 📋 Visão Geral

A Weedle API é uma solução completa para análise de dados de negócio, oferecendo:

- **Dashboard de KPIs** em tempo real
- **Segmentação de clientes** usando algoritmos de Machine Learning
- **Simulação de leads** com predição automática de clusters
- **Análise de NPS** e métricas de satisfação
- **Gestão de contratos** e análise de performance

## 🤖 Algoritmos de Machine Learning

### K-Nearest Neighbors (KNN) para Clustering

A API utiliza o algoritmo **K-Nearest Neighbors (KNN)** para segmentação automática de clientes baseada no valor total contratado.

#### Características do Modelo:
- **Algoritmo:** K-Nearest Neighbors Classifier
- **K vizinhos:** 5 (configurável)
- **Pesos:** Por distância (distance-weighted)
- **Divisão dos dados:** 80% treino, 20% teste
- **Normalização:** StandardScaler para features
- **Métrica de distância:** Euclidiana

#### Funcionalidades:
- **Predição de cluster** para novos leads
- **Score de confiança** para cada predição
- **Probabilidades** por cluster
- **Retreinamento** automático com novos dados

#### Arquivos do Modelo:
```
models/
├── knn_model.pkl                    # Modelo padrão
├── knn_model_20250924_003149.pkl    # Modelo com timestamp
└── model_info_20250924_003149.txt   # Informações do treinamento
```

#### Treinamento do Modelo:
```bash
python scripts/train_knn_model.py
```

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **Oracle Database** - Banco de dados principal
- **scikit-learn** - Biblioteca de Machine Learning
- **pandas** - Manipulação de dados
- **NumPy** - Computação numérica
- **PyArrow** - Formato Parquet para dados
- **Uvicorn** - Servidor ASGI

## 📊 Endpoints Principais

### Dashboard KPIs
- `GET /dashboard/ltv-medio` - Lifetime Value médio dos clientes
- `GET /dashboard/ticket-medio` - Valor médio por transação
- `GET /dashboard/taxa-cross-sell` - Taxa de cross-sell
- `GET /dashboard/nps` - Médias de NPS por categoria
- `GET /dashboard/tempo-medio-resolucao` - TMR (Tempo Médio de Resolução)

### Clusters
- `GET /clusters/` - Lista todos os clusters
- `GET /clusters/{cluster_id}` - Detalhes de um cluster específico

### Leads e Simulação
- `GET /leads/` - Lista todos os leads
- `POST /leads/simular` - Simula um novo lead com predição de cluster

### Parâmetros de Filtro
Todos os endpoints de dashboard suportam filtros opcionais:
- `data_inicio` - Data de início (YYYY-MM-DD)
- `data_fim` - Data de fim (YYYY-MM-DD)
- `cluster_id` - ID do cluster específico
- `segmento` - Segmento de mercado

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- Oracle Database
- Dependências listadas em `requirements.txt`

### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd weedle-api

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente do banco
export DATABASE_URL="oracle://user:password@host:port/service"

# Treine o modelo KNN
python scripts/train_knn_model.py
```

### Execução Local
```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📈 Exemplos de Uso

### Simular um Lead
```bash
curl -X POST "https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/leads/simular" \
  -H "Content-Type: application/json" \
  -d '{
    "cnpj": "12.345.678/0001-90",
    "nome_empresa": "Empresa Exemplo",
    "segmento": "Tecnologia",
    "capital_social": 100000.00,
    "email": "contato@empresa.com",
    "produto": "Sistema ERP",
    "valor_contrato": 50000.00
  }'
```

### Buscar KPIs do Dashboard
```bash
# LTV médio geral
curl "https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/dashboard/ltv-medio"

# LTV médio por cluster
curl "https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/dashboard/ltv-medio?cluster_id=1"

# NPS com filtro de data
curl "https://weedle-gja8huezc8fwf2gg.eastus2-01.azurewebsites.net/dashboard/nps?data_inicio=2024-01-01&data_fim=2024-12-31"
```

## 🏗️ Arquitetura

```
weedle-api/
├── app/
│   ├── main.py              # Aplicação principal FastAPI
│   ├── database.py          # Configuração do banco de dados
│   └── routers/             # Endpoints da API
│       ├── dashboard.py     # KPIs e métricas
│       ├── clusters.py      # Gestão de clusters
│       ├── leads.py         # Simulação de leads
│       └── ...
├── services/
│   └── knn.py              # Serviço de Machine Learning
├── scripts/
│   └── train_knn_model.py  # Treinamento do modelo
├── models/                 # Modelos treinados
├── data_exports/          # Dados para treinamento
└── requirements.txt       # Dependências
```

## 🔧 Configuração

### Variáveis de Ambiente
```bash
DATABASE_URL=oracle://user:password@host:port/service
CORS_ORIGINS=http://localhost:5173,https://www.weedle.com.br
```

### CORS
A API está configurada para aceitar requisições de:
- `http://localhost:5173` (desenvolvimento local)
- `https://www.weedle.com.br` (produção)

## 📊 Estrutura do Banco de Dados

### Tabelas Principais
- **FATO_CONTRATACOES** - Dados de contratos
- **DIM_CLIENTE** - Dimensão de clientes
- **DIM_TEMPO** - Dimensão temporal
- **CLUSTERS** - Definições de clusters
- **CLIENTE_CLUSTER** - Associação cliente-cluster
- **LEADS** - Leads simulados
- **FATO_NPS** - Dados de NPS
- **FATO_TICKETS** - Tickets de suporte

## 🎯 Funcionalidades de ML

### Processo de Predição
1. **Entrada:** Valor total do contrato
2. **Normalização:** Aplicação do StandardScaler
3. **Predição:** KNN com 5 vizinhos mais próximos
4. **Resultado:** Cluster predito + score de confiança

### Métricas de Performance
- **Acurácia:** Medida durante o treinamento
- **Relatório de Classificação:** Por cluster
- **Confiança:** Score de confiança por predição

## 🔄 Retreinamento

O modelo pode ser retreinado periodicamente:

```bash
# Executar treinamento
python scripts/train_knn_model.py

# O script irá:
# 1. Carregar dados de data_exports/cliente_cluster.parquet
# 2. Treinar novo modelo KNN
# 3. Salvar modelo com timestamp
# 4. Atualizar modelo padrão
# 5. Gerar relatório de performance
```

---

**Desenvolvido com ❤️ pela equipe Weedle**