from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dashboard, clusters, leads


app = FastAPI(
    title="Weedle API",
    description="API para análise de KPIs e métricas de negócio",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",  # se você roda o React localmente
    "http://127.0.0.1:5173",
    # "https://meuapp.com"  # adicione seu domínio de produção depois
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # pode usar ["*"] em dev, mas não em produção
    allow_credentials=True,
    allow_methods=["*"],  # ou ["GET", "POST", ...] se quiser limitar
    allow_headers=["*"],  # ou ["Content-Type", "Authorization"]
)

app.include_router(dashboard.router)
app.include_router(clusters.router)
app.include_router(leads.router)
