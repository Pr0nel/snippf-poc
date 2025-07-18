# tests/test_entities.py
from app.domain.entities import Medicamento

def test_medicamento_creation():
    med = Medicamento(codigo_cum="123", nombre_comercial="Medicamento")
    assert med.codigo_cum == "123"
    assert med.nombre_comercial == "Medicamento"