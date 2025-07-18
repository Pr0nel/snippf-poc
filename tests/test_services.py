# tests/test_services.py
from app.services.search_service import SearchService
from tests.fake_repo import FakeMedicamentoRepo

def test_search_service():
    repo = FakeMedicamentoRepo()
    service = SearchService(repo)
    results = service.execute(q="ejemplo", distrito="Ejemplo", min_precio=None, max_precio=None, limit=10, offset=0)
    assert len(results) == 1
    assert results[0].nombre_comercial == "Medicamento Ejemplo"