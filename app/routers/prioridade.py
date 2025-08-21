from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/prioridade")
def get_prioridade(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT * FROM DIM_PRIORIDADE"))
        prioridade = [dict(row._mapping) for row in result]
        return prioridade
    except Exception as e:
        return e
