# app/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Medicamento


class IMedicamentoRepo(ABC):
    """
    Puerto (interface) que define las operaciones
    que cualquier implementación de persistencia debe ofrecer.
    """

    @abstractmethod
    def save(self, medicamentos: List[Medicamento]) -> None:
        """Persiste o actualiza la lista de medicamentos."""
        ...

    @abstractmethod
    def search(
        self,
        q: str,
        distrito: Optional[str],
        min_precio: Optional[float],
        max_precio: Optional[float],
        limit: int,
        offset: int
    ) -> List[Medicamento]:
        """Busca medicamentos con filtros y paginación."""
        ...