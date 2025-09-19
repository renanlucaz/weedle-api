from fastapi import FastAPI
from app.routers import dashboard

app = FastAPI(
    title="Weedle API",
    description="API para análise de KPIs e métricas de negócio",
    version="1.0.0"
)

app.include_router(dashboard.router)
