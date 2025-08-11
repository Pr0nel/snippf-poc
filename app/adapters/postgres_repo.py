# app/adapters/postgres_repo.py
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.entities import Medicamento
from app.domain.repositories import IMedicamentoRepo

class PostgresMedicamentoRepo(IMedicamentoRepo):
    """
    Repositorio concreto que persiste y consulta medicamentos usando SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------ #
    # Guardar / actualizar
    # ------------------------------------------------------------------ #
    def save(self, medicamentos: List[Medicamento]) -> None:
        self.session.execute(text("TRUNCATE TABLE medicamentos;"))
        for m in medicamentos:
            self.session.execute(
                text(
                    """
                    INSERT INTO medicamentos
                    (codigo_cum, nombre_comercial, sustancia, precio_max,
                     distrito, farmacia_nombre, farmacia_lat, farmacia_lon)
                    VALUES (:cum, :nombre, :sust, :precio,
                            :dist, :farmacia, :lat, :lon)
                    """
                ),
                {
                    "cum": m.codigo_cum,
                    "nombre": m.nombre_comercial,
                    "sust": m.sustancia,
                    "precio": m.precio_max,
                    "dist": m.distrito,
                    "farmacia": m.farmacia_nombre,
                    "lat": m.farmacia_lat,
                    "lon": m.farmacia_lon,
                },
            )
        self.session.commit()

    # ------------------------------------------------------------------ #
    # Búsqueda paginada y filtrada
    # ------------------------------------------------------------------ #
    def search(
        self,
        q: str,
        distrito: Optional[str],
        min_precio: Optional[float],
        max_precio: Optional[float],
        limit: int,
        offset: int,
    ) -> List[Medicamento]:
        sql = """
            SELECT
                codigo_cum,
                nombre_comercial,
                sustancia,
                precio_max,
                distrito,
                farmacia_nombre,
                farmacia_direccion
            FROM medicamentos
            WHERE nombre_comercial ILIKE :q
              AND (:distrito IS NULL OR distrito = :distrito)
              AND (:min_precio IS NULL OR precio_max >= :min_precio)
              AND (:max_precio IS NULL OR precio_max <= :max_precio)
            ORDER BY nombre_comercial
            LIMIT :limit OFFSET :offset
        """
        rows = self.session.execute(
            text(sql),
            {
                "q": f"%{q}%",
                "distrito": distrito,
                "min_precio": min_precio,
                "max_precio": max_precio,
                "limit": limit,
                "offset": offset,
            },
        ).all()

        return [
            Medicamento(
                codigo_cum=r.codigo_cum,
                nombre_comercial=r.nombre_comercial,
                sustancia=r.sustancia,
                precio_max=r.precio_max,
                distrito=r.distrito,
                farmacia_nombre=r.farmacia_nombre,
                farmacia_direccion=r.farmacia_direccion
            )
            for r in rows
        ]