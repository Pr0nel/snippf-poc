# tests/fake_repo.py
from typing import List
from app.domain.entities import Medicamento

class FakeMedicamentoRepo:
    def __init__(self):
        self.data = [
            Medicamento(
                codigo_cum="CUM001",
                nombre_comercial="Medicamento Ejemplo",
                sustancia="Sustancia Ejemplo",
                precio_max=10.0,
                distrito="Distrito Ejemplo",
                farmacia_nombre="Farmacia Ejemplo",
                farmacia_direccion="Dirección Ejemplo"
            )
        ]

    def save(self, medicamentos: List[Medicamento]) -> None:
        # Simula el guardado en la base de datos
        self.data.extend(medicamentos)

    def search(self, q: str, distrito: str, min_precio: float, max_precio: float, limit: int, offset: int) -> List[Medicamento]:
        # Simula una búsqueda en la base de datos
        return [
            med for med in self.data
            if q.lower() in med.nombre_comercial.lower()
            and (distrito is None or med.distrito == distrito)
            and (min_precio is None or med.precio_max >= min_precio)
            and (max_precio is None or med.precio_max <= max_precio)
        ][:limit][offset:]