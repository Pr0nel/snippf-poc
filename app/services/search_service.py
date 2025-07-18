# app/services/search_service.py
from typing import List, Optional
from app.domain.entities import Medicamento
from app.domain.repositories import IMedicamentoRepo


class SearchService:
    """
    Caso de uso: búsqueda paginada y filtrada de medicamentos.
    """

    def __init__(self, repo: IMedicamentoRepo) -> None:
        self.repo = repo

    def execute(
        self,
        q: str,
        distrito: Optional[str],
        min_precio: Optional[float],
        max_precio: Optional[float],
        limit: int,
        offset: int
    ) -> List[Medicamento]:
        """
        Delega la consulta al repositorio.
        """
        return self.repo.search(
            q=q,
            distrito=distrito,
            min_precio=min_precio,
            max_precio=max_precio,
            limit=limit,
            offset=offset
        )