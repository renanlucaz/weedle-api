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
            N_CLIENTS
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
        # Buscar dados do cluster
        query_cluster = """
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
            N_CLIENTS
        FROM CLUSTERS
        WHERE CLUSTER_ID = :cluster_id
        """
        
        cluster_result = db.execute(text(query_cluster), {"cluster_id": cluster_id}).fetchone()
        
        if not cluster_result:
            raise HTTPException(status_code=404, detail="Cluster não encontrado")
        
        # Buscar ações do cluster
        query_acoes = """
        SELECT 
            ID,
            ACAO
        FROM CLUSTER_ACOES
        WHERE CLUSTER_ID = :cluster_id
        ORDER BY ID
        """
        
        acoes_results = db.execute(text(query_acoes), {"cluster_id": cluster_id}).fetchall()
        
        # Organizar ações
        acoes = []
        for acao in acoes_results:
            acoes.append({
                "id": acao[0],
                "acao": acao[1]
            })
        
        return {
            "cluster_id": cluster_result[0],
            "descricao": cluster_result[1],
            "total_tickets_abertos": int(cluster_result[2]) if cluster_result[2] else 0,
            "total_desconto_concedido": float(cluster_result[3]) if cluster_result[3] else 0,
            "media_nps": round(float(cluster_result[4]), 1) if cluster_result[4] else 0,
            "qtd_avaliacoes_nps": int(cluster_result[5]) if cluster_result[5] else 0,
            "qtd_contratos": int(cluster_result[6]) if cluster_result[6] else 0,
            "valor_total_contratado": float(cluster_result[7]) if cluster_result[7] else 0,
            "media_dias_resolucao_ticket": float(cluster_result[8]) if cluster_result[8] else 0,
            "n_clients": int(cluster_result[9]) if cluster_result[9] else 0,
            "acoes": acoes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cluster: {str(e)}")


@router.get("/{cluster_id}/acoes")
async def get_cluster_acoes(
    cluster_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca todas as ações de um cluster específico
    """
    try:
        # Verificar se o cluster existe
        query_cluster = "SELECT CLUSTER_ID FROM CLUSTERS WHERE CLUSTER_ID = :cluster_id"
        cluster_exists = db.execute(text(query_cluster), {"cluster_id": cluster_id}).fetchone()
        
        if not cluster_exists:
            raise HTTPException(status_code=404, detail="Cluster não encontrado")
        
        # Buscar ações do cluster
        query_acoes = """
        SELECT 
            ID,
            ACAO
        FROM CLUSTER_ACOES
        WHERE CLUSTER_ID = :cluster_id
        ORDER BY ID
        """
        
        acoes_results = db.execute(text(query_acoes), {"cluster_id": cluster_id}).fetchall()
        
        # Organizar ações
        acoes = []
        for acao in acoes_results:
            acoes.append({
                "id": acao[0],
                "acao": acao[1]
            })
        
        return {
            "cluster_id": cluster_id,
            "acoes": acoes,
            "total_acoes": len(acoes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ações do cluster: {str(e)}")


@router.get("/ranking/nps")
async def get_clusters_ranking_nps(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Ranking de clusters por NPS (maior para menor)
    """
    try:
        query = """
        SELECT 
            CLUSTER_ID,
            DS_CLUSTER,
            MEDIA_NPS,
            QTD_AVALIACOES_NPS,
            N_CLIENTS
        FROM CLUSTERS
        WHERE MEDIA_NPS IS NOT NULL
        ORDER BY MEDIA_NPS DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = db.execute(text(query), {"limit": limit}).fetchall()
        
        ranking = []
        for i, row in enumerate(results, 1):
            ranking.append({
                "posicao": i,
                "cluster_id": row[0],
                "descricao": row[1],
                "media_nps": round(float(row[2]), 1),
                "qtd_avaliacoes_nps": int(row[3]) if row[3] else 0,
                "n_clients": int(row[4]) if row[4] else 0
            })
        
        return {
            "ranking": "NPS (maior para menor)",
            "dados": ranking,
            "total": len(ranking)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking NPS: {str(e)}")


@router.get("/ranking/valor")
async def get_clusters_ranking_valor(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Ranking de clusters por valor total contratado (maior para menor)
    """
    try:
        query = """
        SELECT 
            CLUSTER_ID,
            DS_CLUSTER,
            VALOR_TOTAL_CONTRATADO,
            QTD_CONTRATOS,
            N_CLIENTS
        FROM CLUSTERS
        WHERE VALOR_TOTAL_CONTRATADO IS NOT NULL
        ORDER BY VALOR_TOTAL_CONTRATADO DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = db.execute(text(query), {"limit": limit}).fetchall()
        
        ranking = []
        for i, row in enumerate(results, 1):
            ranking.append({
                "posicao": i,
                "cluster_id": row[0],
                "descricao": row[1],
                "valor_total_contratado": float(row[2]),
                "qtd_contratos": int(row[3]) if row[3] else 0,
                "n_clients": int(row[4]) if row[4] else 0
            })
        
        return {
            "ranking": "Valor Total Contratado (maior para menor)",
            "dados": ranking,
            "total": len(ranking)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking de valor: {str(e)}")


@router.get("/ranking/tickets")
async def get_clusters_ranking_tickets(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Ranking de clusters por total de tickets abertos (maior para menor)
    """
    try:
        query = """
        SELECT 
            CLUSTER_ID,
            DS_CLUSTER,
            TOTAL_TICKETS_ABERTOS,
            MEDIA_DIAS_RESOLUCAO_TICKET,
            N_CLIENTS
        FROM CLUSTERS
        WHERE TOTAL_TICKETS_ABERTOS IS NOT NULL
        ORDER BY TOTAL_TICKETS_ABERTOS DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = db.execute(text(query), {"limit": limit}).fetchall()
        
        ranking = []
        for i, row in enumerate(results, 1):
            ranking.append({
                "posicao": i,
                "cluster_id": row[0],
                "descricao": row[1],
                "total_tickets_abertos": int(row[2]),
                "media_dias_resolucao_ticket": float(row[3]) if row[3] else 0,
                "n_clients": int(row[4]) if row[4] else 0
            })
        
        return {
            "ranking": "Total de Tickets Abertos (maior para menor)",
            "dados": ranking,
            "total": len(ranking)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking de tickets: {str(e)}")


@router.get("/ranking/resolucao")
async def get_clusters_ranking_resolucao(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Ranking de clusters por tempo médio de resolução (menor para maior - melhor performance)
    """
    try:
        query = """
        SELECT 
            CLUSTER_ID,
            DS_CLUSTER,
            MEDIA_DIAS_RESOLUCAO_TICKET,
            TOTAL_TICKETS_ABERTOS,
            N_CLIENTS
        FROM CLUSTERS
        WHERE MEDIA_DIAS_RESOLUCAO_TICKET IS NOT NULL
        ORDER BY MEDIA_DIAS_RESOLUCAO_TICKET ASC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = db.execute(text(query), {"limit": limit}).fetchall()
        
        ranking = []
        for i, row in enumerate(results, 1):
            ranking.append({
                "posicao": i,
                "cluster_id": row[0],
                "descricao": row[1],
                "media_dias_resolucao_ticket": float(row[2]),
                "total_tickets_abertos": int(row[3]) if row[3] else 0,
                "n_clients": int(row[4]) if row[4] else 0
            })
        
        return {
            "ranking": "Tempo Médio de Resolução (menor para maior - melhor performance)",
            "dados": ranking,
            "total": len(ranking)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking de resolução: {str(e)}")


@router.get("/resumo/geral")
async def get_clusters_resumo_geral(db: Session = Depends(get_db)):
    """
    Resumo geral de todos os clusters com totais e médias
    """
    try:
        query = """
        SELECT 
            COUNT(*) as total_clusters,
            SUM(N_CLIENTS) as total_clientes,
            SUM(QTD_CONTRATOS) as total_contratos,
            SUM(VALOR_TOTAL_CONTRATADO) as valor_total_geral,
            SUM(TOTAL_TICKETS_ABERTOS) as total_tickets_geral,
            SUM(TOTAL_DESCONTO_CONCEDIDO) as total_desconto_geral,
            AVG(MEDIA_NPS) as media_nps_geral,
            AVG(MEDIA_DIAS_RESOLUCAO_TICKET) as media_resolucao_geral,
            SUM(QTD_AVALIACOES_NPS) as total_avaliacoes_nps
        FROM CLUSTERS
        """
        
        result = db.execute(text(query)).fetchone()
        
        return {
            "resumo_geral": {
                "total_clusters": int(result[0]) if result[0] else 0,
                "total_clientes": int(result[1]) if result[1] else 0,
                "total_contratos": int(result[2]) if result[2] else 0,
                "valor_total_geral": float(result[3]) if result[3] else 0,
                "total_tickets_geral": int(result[4]) if result[4] else 0,
                "total_desconto_geral": float(result[5]) if result[5] else 0,
                "media_nps_geral": round(float(result[6]), 2) if result[6] else 0,
                "media_resolucao_geral": round(float(result[7]), 2) if result[7] else 0,
                "total_avaliacoes_nps": int(result[8]) if result[8] else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo geral: {str(e)}")


@router.get("/comparacao/{cluster_id1}/{cluster_id2}")
async def compare_clusters(
    cluster_id1: int,
    cluster_id2: int,
    db: Session = Depends(get_db)
):
    """
    Compara dois clusters lado a lado
    """
    try:
        query = """
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
            N_CLIENTS
        FROM CLUSTERS
        WHERE CLUSTER_ID IN (:cluster_id1, :cluster_id2)
        ORDER BY CLUSTER_ID
        """
        
        results = db.execute(text(query), {
            "cluster_id1": cluster_id1,
            "cluster_id2": cluster_id2
        }).fetchall()
        
        if len(results) != 2:
            raise HTTPException(status_code=404, detail="Um ou ambos os clusters não foram encontrados")
        
        cluster1_data = {
            "cluster_id": results[0][0],
            "descricao": results[0][1],
            "total_tickets_abertos": int(results[0][2]) if results[0][2] else 0,
            "total_desconto_concedido": float(results[0][3]) if results[0][3] else 0,
            "media_nps": round(float(results[0][4]), 1) if results[0][4] else 0,
            "qtd_avaliacoes_nps": int(results[0][5]) if results[0][5] else 0,
            "qtd_contratos": int(results[0][6]) if results[0][6] else 0,
            "valor_total_contratado": float(results[0][7]) if results[0][7] else 0,
            "media_dias_resolucao_ticket": float(results[0][8]) if results[0][8] else 0,
            "n_clients": int(results[0][9]) if results[0][9] else 0
        }
        
        cluster2_data = {
            "cluster_id": results[1][0],
            "descricao": results[1][1],
            "total_tickets_abertos": int(results[1][2]) if results[1][2] else 0,
            "total_desconto_concedido": float(results[1][3]) if results[1][3] else 0,
            "media_nps": round(float(results[1][4]), 1) if results[1][4] else 0,
            "qtd_avaliacoes_nps": int(results[1][5]) if results[1][5] else 0,
            "qtd_contratos": int(results[1][6]) if results[1][6] else 0,
            "valor_total_contratado": float(results[1][7]) if results[1][7] else 0,
            "media_dias_resolucao_ticket": float(results[1][8]) if results[1][8] else 0,
            "n_clients": int(results[1][9]) if results[1][9] else 0
        }
        
        return {
            "comparacao": {
                "cluster_1": cluster1_data,
                "cluster_2": cluster2_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comparar clusters: {str(e)}")
