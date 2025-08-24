# app/main.py
import asyncio  # opcional, solo si decides async
from app.adapters.downloader import PlaywrightDownloader, ScrapyDownloader
from app.adapters.data_cleaner import DataFrameCleaner
from app.adapters.scraper import DigemidScraper
from app.config import ScraperConfig
import os
from dotenv import load_dotenv

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
    load_dotenv() # carga variables de entorno desde el archivo .env

    # Lee una variable de entorno para determinar el entorno
    env = os.environ.get('ENV', 'dev') # Si no está definida, usa 'dev' por defecto
    config_path = f'app/config_{env}.yml'

    # Carga la configuración desde el archivo YAML
    # Utiliza el método para leer y parsear el archivo de configuración
    # y convertirlo en un objeto de tipo ScraperConfig
    cfg = ScraperConfig.from_yaml(config_path)

    # Inyección de dependencias
    # En lugar de que DigemidScraper cree sus propias instancias de PlaywrightDownloader y DataFrameCleaner
    # estas se le pasan a través del constructor
    scraper = DigemidScraper(
        downloader  = PlaywrightDownloader(cfg), # Se crea una instancia de la clase
        cleaner     = DataFrameCleaner(), # Se crea una instancia de la clase
        cfg         = cfg # Se pasa el objeto de configuración
    )
    df_general, df_producto = scraper.download(cfg.product_name) # Llama al método download() del objeto scraper
    if df_general is not None:
        print("✅ Descarga y limpieza del Catálogo General completada con éxito.")
        print("\n--- Catalogo General (primeras 5 filas) ---")
        print(df_general.head())
    
    if df_producto is not None:
        print("✅ Descarga y limpieza de los Productos Buscados completada con éxito.")
        print("\n--- Productos Buscados (primeras 5 filas) ---")
        print(df_producto.head())

    if df_general is None and df_producto is None:
        print("❌ No se pudo descargar ningún archivo.")

if __name__ == "__main__":
    run_scraper()