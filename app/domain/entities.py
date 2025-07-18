# app/domain/entities.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(slots=True, frozen=True)
class Medicamento:
    """
    Value Object que representa un medicamento en el catálogo DIGEMID.
    """
    codigo_cum: str
    nombre_comercial: str
    sustancia: str
    precio_max: Decimal
    distrito: str
    farmacia_nombre: str
    farmacia_direccion: str