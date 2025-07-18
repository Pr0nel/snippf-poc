# app/services/ingest_service.py
from typing import List
from app.domain.entities import Medicamento
from app.domain.repositories import IMedicamentoRepo
from app.adapters.scraper import IDigemidScraper
from decimal import Decimal

class IngestService:
    """
    Caso de uso: descargar y persistir el catálogo DIGEMID.
    """

    def __init__(self, repo: IMedicamentoRepo, scraper: IDigemidScraper) -> None:
        self.repo = repo
        self.scraper = scraper

    def execute(self) -> int:
        """
        Devuelve la cantidad de medicamentos insertados.
        """
        raw_df = self.scraper.download()
        meds: List[Medicamento] = [
            Medicamento(
                codigo_cum=str(row["CUM"]),
                nombre_comercial=str(row["NOMBRE"]),
                sustancia=str(row["SUSTANCIA"]),
                precio_max=Decimal(str(row["PRECIO"])),
                distrito=str(row["DISTRITO"]),
                farmacia_nombre=str(row["FARMACIA"]),
                farmacia_direccion=str(row["FARM_DIRE"])
            )
            for _, row in raw_df.iterrows()
        ]
        self.repo.save(meds)
        return len(meds)