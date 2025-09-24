from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from services.knn import KNNClusterPredictor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter(prefix="/leads", tags=["Leads"])


def get_cluster_name_by_id(cluster_id: int, db: Session) -> str:
    try:
        query = """
        SELECT DS_CLUSTER
        FROM CLUSTERS
        WHERE CLUSTER_ID = :cluster_id
        """

        result = db.execute(text(query), {"cluster_id": cluster_id}).fetchone()

        if result:
            return result[0]
        else:
            return f"Cluster {cluster_id}"

    except Exception as e:
        print(f"Erro ao buscar nome do cluster {cluster_id}: {str(e)}")
        return f"Cluster {cluster_id}"


def predict_cluster_with_knn(valor_contrato: float) -> int:
    try:
        predictor = KNNClusterPredictor()
        prediction = predictor.predict(valor_contrato)
        return prediction['predicted_cluster_id']

    except Exception as e:
        print(f"Erro na predição KNN: {str(e)}")


class SimularLeadRequest(BaseModel):
    cnpj: str
    nome_empresa: str
    segmento: str
    capital_social: float
    email: str
    produto: str
    valor_contrato: float


class SimularLeadResponse(BaseModel):
    success: bool
    message: str
    lead_id: Optional[str] = None
    data: Optional[dict] = None


@router.get("/")
async def get_all_leads(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    segmento: Optional[str] = None,
    cluster_name: Optional[str] = None,
    produto: Optional[str] = None
):
    try:
        query = """
        SELECT
            CNPJ,
            NOME_EMPRESA,
            SEGMENTO,
            CAPITAL_SOCIAL,
            EMAIL,
            PRODUTO,
            VALOR_CONTRATO,
            CLUSTER_NAME,
            DATA_SIMULACAO
        FROM LEADS
        """
        query += " ORDER BY DATA_SIMULACAO DESC"

        results = db.execute(text(query)).fetchall()

        leads = []
        for row in results:
            leads.append({
                "cnpj": row[0],
                "nome_empresa": row[1],
                "segmento": row[2],
                "capital_social": float(row[3]) if row[3] else 0,
                "email": row[4],
                "produto": row[5],
                "valor_contrato": float(row[6]) if row[6] else 0,
                "cluster_name": row[7],
                "data_simulacao": row[8].isoformat() if row[8] else None
            })

        return {
            "leads": leads,
            "total": len(leads),
            "limit": limit,
            "offset": offset,
            "filtros": {
                "segmento": segmento,
                "cluster_name": cluster_name,
                "produto": produto
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar leads: {str(e)}")


@router.post("/simular", response_model=SimularLeadResponse)
async def simular_lead(
    lead_data: SimularLeadRequest,
    db: Session = Depends(get_db)
):
    try:
        check_query = "SELECT CNPJ FROM LEADS WHERE CNPJ = :cnpj"
        existing_lead = db.execute(text(check_query), {"cnpj": lead_data.cnpj}).fetchone()

        if existing_lead:
            raise HTTPException(
                status_code=400, 
                detail=f"Lead com CNPJ {lead_data.cnpj} já existe"
            )

        predicted_cluster_id = predict_cluster_with_knn(lead_data.valor_contrato)

        cluster_name = get_cluster_name_by_id(predicted_cluster_id, db)

        print(f"KNN predição: Valor R$ {lead_data.valor_contrato:,.2f} → Cluster {predicted_cluster_id} → Nome: {cluster_name}")

        insert_query = """
        INSERT INTO LEADS (
            CNPJ, NOME_EMPRESA, SEGMENTO, CAPITAL_SOCIAL, 
            EMAIL, PRODUTO, VALOR_CONTRATO, CLUSTER_NAME, DATA_SIMULACAO
        ) VALUES (
            :cnpj, :nome_empresa, :segmento, :capital_social,
            :email, :produto, :valor_contrato, :cluster_name, :data_simulacao
        )
        """

        current_time = datetime.now()

        db.execute(text(insert_query), {
            "cnpj": lead_data.cnpj,
            "nome_empresa": lead_data.nome_empresa,
            "segmento": lead_data.segmento,
            "capital_social": lead_data.capital_social,
            "email": lead_data.email,
            "produto": lead_data.produto,
            "valor_contrato": lead_data.valor_contrato,
            "cluster_name": cluster_name,
            "data_simulacao": current_time
        })

        db.commit()

        select_query = """
        SELECT 
            CNPJ, NOME_EMPRESA, SEGMENTO, CAPITAL_SOCIAL,
            EMAIL, PRODUTO, VALOR_CONTRATO, CLUSTER_NAME, DATA_SIMULACAO
        FROM LEADS 
        WHERE CNPJ = :cnpj
        """

        result = db.execute(text(select_query), {"cnpj": lead_data.cnpj}).fetchone()

        lead_response = {
            "cnpj": result[0],
            "nome_empresa": result[1],
            "segmento": result[2],
            "capital_social": float(result[3]) if result[3] else 0,
            "email": result[4],
            "produto": result[5],
            "valor_contrato": float(result[6]) if result[6] else 0,
            "cluster_name": result[7],
            "data_simulacao": result[8].isoformat() if result[8] else None
        }

        return SimularLeadResponse(
            success=True,
            message="Lead simulado e inserido com sucesso",
            lead_id=lead_data.cnpj,
            data=lead_response
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao simular lead: {str(e)}")
