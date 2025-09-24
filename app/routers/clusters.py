from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("/")
async def get_all_clusters(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    offset: Optional[int] = 0
):  
    """
    Lista todos os clusters com suas métricas
    """
    try:
        # Query para buscar clusters
        query_clusters = """
        SELECT 
            CLUSTER_ID,
            DS_CLUSTER,
            TOTAL_TICKETS_ABERTOS,
            TOTAL_DESCONTO_CONCEDIDO,
            MEDIA_NPS,
            QTD_AVALIACOES_NPS,
            QTD_CONTRATOS,
            VALOR_TOTAL_CONTRATADO,
            MEDIA_DIAS_RESOLUCAO_TICKET,
            N_CLIENTS,
            COMPORTAMENTO
        FROM CLUSTERS
        ORDER BY CLUSTER_ID
        """
        
        if limit:
            query_clusters += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        cluster_results = db.execute(text(query_clusters)).fetchall()
        
        query_acoes = """
        SELECT 
            ID,
            CLUSTER_ID,
            ACAO
        FROM CLUSTER_ACOES
        ORDER BY CLUSTER_ID, ID
        """
        acoes_results = db.execute(text(query_acoes)).fetchall()
        
        acoes_por_cluster = {}
        for acao in acoes_results:
            cluster_id = acao[1]
            if cluster_id not in acoes_por_cluster:
                acoes_por_cluster[cluster_id] = []
            
            acoes_por_cluster[cluster_id].append({
                "id": acao[0],
                "acao": acao[2]
            })
        
        # Organizar clusters
        clusters = []
        for row in cluster_results:
            cluster_id = row[0]
            clusters.append({
                "cluster_id": cluster_id,
                "descricao": row[1],
                "total_tickets_abertos": int(row[2]) if row[2] else 0,
                "total_desconto_concedido": float(row[3]) if row[3] else 0,
                "media_nps": round(float(row[4]), 1) if row[4] else 0,
                "qtd_avaliacoes_nps": int(row[5]) if row[5] else 0,
                "qtd_contratos": int(row[6]) if row[6] else 0,
                "valor_total_contratado": float(row[7]) if row[7] else 0,
                "media_dias_resolucao_ticket": float(row[8]) if row[8] else 0,
                "n_clients": int(row[9]) if row[9] else 0,
                "comportamento": row[10],
                "acoes": acoes_por_cluster.get(cluster_id, [])
            })
        
        return {
            "clusters": clusters,
            "total": len(clusters),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clusters: {str(e)}")


@router.get("/{cluster_id}")
async def get_cluster_by_id(
    cluster_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca um cluster específico por ID
    """
    try:
        # Buscar dados do cluster com ações usando JOIN
        query = """
        SELECT 
            c.CLUSTER_ID,
            c.DS_CLUSTER,
            c.TOTAL_TICKETS_ABERTOS,
            c.TOTAL_DESCONTO_CONCEDIDO,
            c.MEDIA_NPS,
            c.QTD_AVALIACOES_NPS,
            c.QTD_CONTRATOS,
            c.VALOR_TOTAL_CONTRATADO,
            c.MEDIA_DIAS_RESOLUCAO_TICKET,
            c.N_CLIENTS,
            ca.ID as ACAO_ID,
            ca.ACAO
        FROM CLUSTERS c
        LEFT JOIN CLUSTER_ACOES ca ON c.CLUSTER_ID = ca.CLUSTER_ID
        WHERE c.CLUSTER_ID = :cluster_id
        ORDER BY ca.ID
        """

        query_acoes = """
        SELECT 
            ID,
            CLUSTER_ID,
            ACAO
        FROM CLUSTER_ACOES
        WHERE CLUSTER_ID = :cluster_id
        ORDER BY ID
        """
        
        results = db.execute(text(query), {"cluster_id": cluster_id}).fetchall()

        acoes_results = db.execute(text(query_acoes), {"cluster_id": cluster_id}).fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="Cluster não encontrado")
        
        # Organizar dados do cluster e ações
        cluster_data = None
        acoes = []

        for acao in acoes_results:
            acoes.append({
                "id": acao[0],
                "acao": acao[1]
            })
        
        for row in results:
            if cluster_data is None:
                # Primeira linha contém os dados do cluster
                cluster_data = {
                    "cluster_id": row[0],
                    "descricao": row[1],
                    "total_tickets_abertos": int(row[2]) if row[2] else 0,
                    "total_desconto_concedido": float(row[3]) if row[3] else 0,
                    "media_nps": round(float(row[4]), 1) if row[4] else 0,
                    "qtd_avaliacoes_nps": int(row[5]) if row[5] else 0,
                    "qtd_contratos": int(row[6]) if row[6] else 0,
                    "valor_total_contratado": float(row[7]) if row[7] else 0,
                    "media_dias_resolucao_ticket": float(row[8]) if row[8] else 0,
                    "n_clients": int(row[9]) if row[9] else 0
                }

        return {
            **cluster_data,
            "acoes": acoes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cluster: {str(e)}")
