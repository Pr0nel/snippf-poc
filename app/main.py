# app/main.py
import asyncio  # opcional, solo si decides async
from app.adapters.downloader import PlaywrightDownloader, ScrapyDownloader
from app.adapters.data_cleaner import DataFrameCleaner
from app.adapters.scraper import DigemidScraper
from app.config import ScraperConfig

from fastapi import FastAPI
from app.infra.db import get_session
from app.adapters.postgres_repo import PostgresMedicamentoRepo
from app.services.ingest_service import IngestService
from app.services.search_service import SearchService

"""
app = FastAPI(title="SNIPPF - Catálogo Farmacéutico DIGEMID")


@app.on_event("startup")
async def startup_event():
"""
    #Inicializa los servicios al arrancar FastAPI.
"""
    app.state.repo = PostgresMedicamentoRepo(get_session())
    app.state.ingest_service = IngestService(repo=app.state.repo)
    app.state.search_service = SearchService(repo=app.state.repo)


@app.post("/api/v1/ingest", response_model=dict)
def ingest():
"""
#Carga el catálogo DIGEMID.
"""
    inserted = app.state.ingest_service.execute()
    return {"status": "ok", "inserted": inserted}


@app.get("/api/v1/search", response_model=list)
def search(
    q: str = None,
    distrito: str = None,
    min_precio: float = None,
    max_precio: float = None,
    limit: int = 20,
    offset: int = 0,
):
"""
#Búsqueda paginada y filtrada.
"""
    results = app.state.search_service.execute(
        q=q,
        distrito=distrito,
        min_precio=min_precio,
        max_precio=max_precio,
        limit=limit,
        offset=offset,
    )
    return {"total": len(results), "items": results}
"""

def run_scraper():
    cfg = ScraperConfig()
    scraper = DigemidScraper(
        downloader=PlaywrightDownloader(cfg),
        #downloader = ScrapyDownloader(cfg),
        cleaner=DataFrameCleaner()
    )
    df = scraper.download()
    if df is not None:
        print("✅ Scraping OK:")
        print(df.head())
    else:
        print("❌ No se pudo descargar el archivo.")

# Punto de entrada
if __name__ == "__main__":
    run_scraper()