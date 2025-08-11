# tests/test_scraper.py
import pytest
from unittest.mock import patch
from app.adapters.scraper import DigemidScraper
import pandas as pd

class TestDigemidScraper:
    @pytest.fixture
    def setup(self):
        self.scraper = DigemidScraper()

    @patch('playwright.sync_api.sync_playwright')
    def test_download_failure(self, mock_sync_playwright):
        # Mockear el comportamiento esperado al descargar
        mock_sync_playwright.return_value.__enter__.return_value.download.return_value = None
        
        # Ejecutar el método download y verificar el resultado
        result = self.scraper.download()
        assert result is None, "El método download debería devolver None si falla"

    @patch('playwright.sync_api.sync_playwright')
    @patch('pandas.read_excel')
    def test_download_success(self, mock_sync_playwright, mock_read_excel):
        # Mockear el comportamiento esperado al descargar y el DataFrame
        mock_sync_playwright.return_value.__enter__.return_value.download.return_value = mock.Mock()
        mock_read_excel.return_value = pd.DataFrame({
            'column1': [1, 2],
            'column2': [3, 4]
        })
        
        # Mockear el comportamiento esperado al cerrar anuncios y hacer clic en el botón de descarga
        mock_sync_playwright.return_value.__enter__.return_value.new_page.return_value.click.side_effect = [None]
        
        # Ejecutar el método download y verificar el resultado
        result = self.scraper.download()
        assert pytest.is_instance(result, pd.DataFrame), "El método download debería devolver un DataFrame"
        assert not result.empty, "El DataFrame devuel ser no vacío"