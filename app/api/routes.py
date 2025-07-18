# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.services.ingest_service import IngestService
from app.services.search_service import SearchService
from app.adapters.postgres_repo import PostgresMedicamentoRepo
from app.infra.db import get_session

router = APIRouter(prefix="/api/v1", tags=["catalog"])


# ----- Ingestar datos (privado) ---------------------------------------------
@router.post("/ingest", summary="Cargar catálogo DIGEMID")
def ingest(
    service: IngestService = Depends(
        lambda: IngestService(
            repo=PostgresMedicamentoRepo(get_session()),
        )
    ),
):
    """
    Descarga el Excel de DIGEMID y persiste los medicamentos.
    Acceso interno.
    """
    try:
        inserted = service.execute()
        return {"status": "ok", "inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Búsqueda pública -------------------------------------------------------
@router.get("/search", summary="Buscar medicamentos")
def search(
    q: str = Query(..., description="Nombre comercial o sustancia"),
    distrito: Optional[str] = Query(None, description="Filtro por distrito"),
    min_precio: Optional[float] = Query(None, ge=0),
    max_precio: Optional[float] = Query(None, ge=0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: SearchService = Depends(
        lambda: SearchService(
            repo=PostgresMedicamentoRepo(get_session()),
        )
    ),
):
    """
    Autocompletado + filtros de precio y distrito.
    Retorna lista paginada.
    """
    try:
        results = service.execute(
            q=q,
            distrito=distrito,
            min_precio=min_precio,
            max_precio=max_precio,
            limit=limit,
            offset=offset,
        )
        return {"total": len(results), "items": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))