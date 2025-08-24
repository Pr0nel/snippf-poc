# app/adapters/scraper.py
from typing import Protocol
import pandas as pd
from app.adapters.data_cleaner import DataFrameCleaner
from app.adapters.downloader import IDownloader
from app.config import ScraperConfig

class IDigemidScraper(Protocol):
    """Protocolo (interfaz estructural) para el scraper que descarga dos archivos."""

    def download(self, product_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        ...

class DigemidScraper(IDigemidScraper):
    """
    Implementación concreta:
    descarga catalogoproductos.xlsx y preciosProductos.xlsx de DIGEMID; y los convierte a DataFrame limpio.
    """

    def __init__(self, downloader: IDownloader, cleaner: DataFrameCleaner, cfg: ScraperConfig):
        self.downloader = downloader
        self.cleaner = cleaner
        self.cfg = cfg

    # Código corregido en scraper.py
    def download(self, product_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        df01_raw, df02_raw = self.downloader.download_excels(product_name)
    
        # Limpia el primer DataFrame
        df01_raw = self.cleaner.clean_catalog(df01_raw)
    
        # Limpia el segundo DataFrame solo si no es nulo
        if df02_raw is not None:
            df02_raw = self.cleaner.clean_product(df02_raw)
        
        return df01_raw, df02_raw