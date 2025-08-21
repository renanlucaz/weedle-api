from fastapi import FastAPI
from app.routers import prioridade
from app.routers import health

app = FastAPI()

app.include_router(prioridade.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "API online"}