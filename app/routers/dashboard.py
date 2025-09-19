from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from typing import Optional
from datetime import date

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/ltv-medio")
async def get_ltv_medio(
    db: Session = Depends(get_db),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    cluster_id: Optional[int] = None
):
    try:
        where_conditions = ["c.SITUACAO_CONTRATO = 'ATIVO'"]
        params = {}

        if data_inicio:
            where_conditions.append("t.DATA >= :data_inicio")
            params["data_inicio"] = data_inicio
        if data_fim:
            where_conditions.append("t.DATA <= :data_fim")
            params["data_fim"] = data_fim
        if cluster_id is not None:
            where_conditions.append("cc.CLUSTER_ID = :cluster_id")
            params["cluster_id"] = cluster_id

        query = f"""
        SELECT
            ROUND(AVG(LTV_CLIENTE), 2) AS LTV_MEDIO
        FROM (
            SELECT
                c.SK_CLIENTE,
                SUM(f.VL_TOTAL_CONTRATO) AS LTV_CLIENTE
            FROM
                FATO_CONTRATACOES f
            INNER JOIN DIM_CLIENTE c
                ON f.SK_CLIENTE = c.SK_CLIENTE
            INNER JOIN DIM_TEMPO t
                ON f.SK_TEMPO = t.SK_TEMPO
            INNER JOIN CLIENTE_CLUSTER cc
                ON cc.SK_CLIENTE = c.SK_CLIENTE
            WHERE {" AND ".join(where_conditions)}
            GROUP BY c.SK_CLIENTE
        )
        """

        result = db.execute(text(query), params).fetchone()

        return {
            "kpi": "ltv-medio",
            "valor": float(result[0]) if result and result[0] else 0,
            "unidade": "R$",
            "descricao": (
                "Valor total médio gasto por cliente durante todo o relacionamento"
                + (f" (Cluster {cluster_id})" if cluster_id else "")
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular LTV médio: {str(e)}")


@router.get("/ticket-medio")
async def get_ticket_medio(
    db: Session = Depends(get_db),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    segmento: Optional[str] = None,
    cluster_id: Optional[int] = None
):
    try:
        where_conditions = ["c.SITUACAO_CONTRATO = 'ATIVO'"]
        params = {}

        if data_inicio:
            where_conditions.append("t.DATA >= :data_inicio")
            params["data_inicio"] = data_inicio
        if data_fim:
            where_conditions.append("t.DATA <= :data_fim")
            params["data_fim"] = data_fim
        if segmento:
            where_conditions.append("c.DS_SEGMENTO = :segmento")
            params["segmento"] = segmento
        if cluster_id is not None:
            where_conditions.append("cc.CLUSTER_ID = :cluster_id")
            params["cluster_id"] = cluster_id

        query = f"""
        SELECT
            ROUND(AVG(f.VL_TOTAL_CONTRATO), 2) AS TICKET_MEDIO
        FROM
            FATO_CONTRATACOES f
        INNER JOIN DIM_CLIENTE c
            ON f.SK_CLIENTE = c.SK_CLIENTE
        INNER JOIN DIM_TEMPO t
            ON f.SK_TEMPO = t.SK_TEMPO
        INNER JOIN CLIENTE_CLUSTER cc
            ON cc.SK_CLIENTE = c.SK_CLIENTE
        WHERE {" AND ".join(where_conditions)}
        """

        result = db.execute(text(query), params).fetchone()

        return {
            "kpi": "ticket-medio",
            "valor": float(result[0]) if result and result[0] else 0,
            "unidade": "R$",
            "descricao": (
                "Valor médio de cada transação de venda"
                + (f" (Cluster {cluster_id})" if cluster_id else "")
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular ticket médio: {str(e)}")


@router.get("/taxa-cross-sell")
async def get_taxa_cross_sell(
    db: Session = Depends(get_db),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    cluster_id: Optional[int] = None
):
    try:
        query = """
        SELECT
            ROUND(
                (COUNT(CASE WHEN sub.QTD_CONTRATOS > 1 THEN 1 END) * 100.0) / NULLIF(COUNT(*), 0),
                2
            ) AS TAXA_CROSS_SELL
        FROM (
            SELECT
                c.SK_CLIENTE,
                COUNT(f.SK_CONTRATACAO) AS QTD_CONTRATOS
            FROM
                FATO_CONTRATACOES f
            INNER JOIN DIM_CLIENTE c
                ON f.SK_CLIENTE = c.SK_CLIENTE
            INNER JOIN CLIENTE_CLUSTER cc
                ON c.SK_CLIENTE = cc.SK_CLIENTE
            WHERE
                c.SITUACAO_CONTRATO = 'ATIVO'
        """

        params = {}
        if cluster_id:
            query += " AND cc.CLUSTER_ID = :cluster_id"
            params["cluster_id"] = cluster_id

        if data_inicio:
            query += " AND f.DT_CONTRATO >= :data_inicio"
            params["data_inicio"] = data_inicio

        if data_fim:
            query += " AND f.DT_CONTRATO <= :data_fim"
            params["data_fim"] = data_fim

        # Fecha o GROUP BY e a subquery
        query += """
            GROUP BY
                c.SK_CLIENTE
        ) sub
        """

        result = db.execute(text(query), params).fetchone()

        return {
            "kpi": "taxa-cross-sell",
            "valor": float(result[0]) if result and result[0] else 0,
            "unidade": "%",
            "descricao": "Porcentagem de clientes que possuem mais de um contrato ativo"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular taxa de cross-sell: {str(e)}")


@router.get("/nps")
async def get_nps(
    db: Session = Depends(get_db),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    cluster_id: Optional[int] = None
):
    try:
        # Query principal: calcula a MÉDIA das notas por tipo de NPS
        query = """
        SELECT
            sub.TIPO_NPS,
            ROUND(AVG(sub.NOTA_NPS), 2) AS MEDIA_NPS
        FROM (
            SELECT
                f.NOTA_NPS,
                f.TIPO_NPS
            FROM
                FATO_NPS f
            INNER JOIN DIM_CLIENTE c
                ON f.SK_CLIENTE = c.SK_CLIENTE
            INNER JOIN CLIENTE_CLUSTER cc
                ON c.SK_CLIENTE = cc.SK_CLIENTE
            WHERE f.NOTA_NPS > 0
        """

        params = {}
        if cluster_id:
            query += " AND cc.CLUSTER_ID = :cluster_id"
            params["cluster_id"] = cluster_id

        if data_inicio:
            query += " AND f.SK_TEMPO >= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_inicio)"
            params["data_inicio"] = data_inicio

        if data_fim:
            query += " AND f.SK_TEMPO <= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_fim)"
            params["data_fim"] = data_fim

        query += """
        ) sub
        GROUP BY sub.TIPO_NPS
        """

        results = db.execute(text(query), params).fetchall()

        kpis = {
            "media_nps_relacional": 0,
            "media_nps_suporte": 0,
            # "media_nps_produto": 0,
            "media_nps_geral": 0,
        }

        # Preenche os KPIs por tipo
        for row in results:
            tipo, media = row
            if tipo.upper() == "RELACIONAL":
                kpis["media_nps_relacional"] = float(media)
            elif tipo.upper() == "SUPORTE":
                kpis["media_nps_suporte"] = float(media)
            elif tipo.upper() == "PRODUTO":
                kpis["media_nps_produto"] = float(media)

        # Calcula a média geral (independente do tipo)
        query_geral = """
        SELECT ROUND(AVG(f.NOTA_NPS), 2) AS MEDIA_NPS_GERAL
        FROM
            FATO_NPS f
        INNER JOIN DIM_CLIENTE c
            ON f.SK_CLIENTE = c.SK_CLIENTE
        INNER JOIN CLIENTE_CLUSTER cc
            ON c.SK_CLIENTE = cc.SK_CLIENTE
        WHERE f.NOTA_NPS > 0
        """

        if cluster_id:
            query_geral += " AND cc.CLUSTER_ID = :cluster_id"
        if data_inicio:
            query_geral += " AND f.SK_TEMPO >= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_inicio)"
        if data_fim:
            query_geral += " AND f.SK_TEMPO <= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_fim)"

        result_geral = db.execute(text(query_geral), params).fetchone()
        kpis["media_nps_geral"] = float(result_geral[0]) if result_geral and result_geral[0] else 0

        return {
            "kpi": "media-nps",
            "valores": kpis,
            "unidade": "pontos (0 a 10)",
            "descricao": "Média simples das notas de NPS por tipo e geral"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular média de NPS: {str(e)}")


@router.get("/tempo-medio-resolucao")
async def get_tempo_medio_resolucao(
    db: Session = Depends(get_db),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    cluster_id: Optional[int] = None
):
    try:
        query = """
        SELECT
            ROUND(AVG(ft.tempo_resolucao_dias), 2) AS tmr_medio,
            COUNT(*) AS total_tickets,
            MIN(ft.tempo_resolucao_dias) AS menor_tempo,
            MAX(ft.tempo_resolucao_dias) AS maior_tempo
        FROM
            FATO_TICKETS ft
        INNER JOIN DIM_CLIENTE c
            ON ft.SK_CLIENTE = c.SK_CLIENTE
        INNER JOIN CLIENTE_CLUSTER cc
            ON c.SK_CLIENTE = cc.SK_CLIENTE
        WHERE ft.tempo_resolucao_dias IS NOT NULL
        """

        params = {}

        # Filtro por cluster
        if cluster_id:
            query += " AND cc.CLUSTER_ID = :cluster_id"
            params["cluster_id"] = cluster_id

        # Filtros de data
        if data_inicio:
            query += " AND ft.SK_TEMPO >= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_inicio)"
            params["data_inicio"] = data_inicio
        if data_fim:
            query += " AND ft.SK_TEMPO <= (SELECT SK_TEMPO FROM DIM_TEMPO WHERE DATA = :data_fim)"
            params["data_fim"] = data_fim

        result = db.execute(text(query), params).fetchone()

        return {
            "kpi": "Tempo Médio de Resolução (TMR)",
            "valor": float(result[0]) if result and result[0] else 0,
            "unidade": "dias",
            "descricao": "Tempo médio que a equipe de suporte leva para resolver um chamado",
            "detalhes": {
                "total_tickets": int(result[1]) if result and result[1] else 0,
                "menor_tempo": float(result[2]) if result and result[2] else 0,
                "maior_tempo": float(result[3]) if result and result[3] else 0
            },
            "filtros": {
                "cluster_id": cluster_id,
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular TMR: {str(e)}")
