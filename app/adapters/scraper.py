# app/adapters/scraper.py
from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd
import requests
from io import BytesIO


class IDigemidScraper(Protocol):
    """Protocolo (interfaz estructural) para el scraper."""

    def download(self) -> pd.DataFrame:
        ...


class DigemidScraper:
    """
    Implementación concreta:
    descarga el Excel oficial de DIGEMID y lo convierte a DataFrame limpio.
    """

    URL = "https://opm-digemid.minsa.gob.pe/descarga/catalogo.xlsx" # Actualizar URL oficial del catálogo

    def download(self) -> pd.DataFrame:
        response = requests.get(self.URL, verify=False, timeout=30)
        response.raise_for_status()
        df = pd.read_excel(
            BytesIO(response.content),
            dtype=str,
            keep_default_na=False,
        )

        # Normalización mínima
        df = df.rename(
            columns={
                "CUM": "CUM",
                "NOMBRE": "NOMBRE",
                "SUSTANCIA": "SUSTANCIA",
                "PRECIO": "PRECIO",
                "DISTRITO": "DISTRITO",
                "FARMACIA": "FARMACIA",
                "FARM_DIRE": "FARM_DIRE"
            }
        )
        return df