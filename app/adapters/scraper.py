# app/adapters/scraper.py
from typing import Protocol
import pandas as pd
from app.adapters.data_cleaner import DataFrameCleaner
from app.adapters.downloader import IDownloader

class IDigemidScraper(Protocol):
    """Protocolo (interfaz estructural) para el scraper."""

    def download(self) -> pd.DataFrame:
        ...

class DigemidScraper(IDigemidScraper):
    """
    Implementación concreta:
    descarga el Excel oficial catalogoproductos.xlsx de DIGEMID y lo convierte a DataFrame limpio.
    """

    def __init__(self, downloader: IDownloader, cleaner: DataFrameCleaner):
        self.downloader = downloader
        self.cleaner = cleaner

    def download(self) -> pd.DataFrame:
        df_raw = self.downloader.download_excel()
        return self.cleaner.clean(df_raw)