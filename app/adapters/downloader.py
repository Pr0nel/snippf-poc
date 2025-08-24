# app/adapters/downloader.py
from abc import ABC, abstractmethod
from app.config import ScraperConfig
import pandas as pd
from playwright.sync_api import TimeoutError, sync_playwright
from io import BytesIO
import requests
import os

class IDownloader(ABC):
    @abstractmethod
    def download_excels(self, product_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Descarga el catálogo general y un Excel de producto específico.
        Retorna una tupla con los DataFrames.
        """
        ...

class PlaywrightDownloader(IDownloader):
    def __init__(self, cfg: ScraperConfig):
        self.cfg = cfg

    def _get_page_and_handle_ads(self, playwright):
        """Método privado para inicializar la página y cerrar anuncios."""
        browser = playwright.chromium.launch(headless=self.cfg.playwright['headless'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        page.goto(self.cfg.playwright['url'], timeout=30000)
        # Esperar a que la página cargue completamente
        try:
            page.wait_for_load_state("networkidle", timeout=15000) # Espera hasta que no haya peticiones por >1s
            print("Página completamente cargada.")
        except Exception as e:
            print(f"Advertencia: La página no alcanzó 'networkidle': {e}")
        # Cerrar anuncios de la página. OJO: *ACTUALIZAR SELECTORES SI CAMBIA LOS ANUNCIOS*
        selectors_to_check = [
            self.cfg.playwright['selectors']['css_anuncio1'],
            self.cfg.playwright['selectors']['css_anuncio2']
        ]
        for idx, selector in enumerate(selectors_to_check, start=1):
            try:
                page.click(selector, timeout=5000)
                page.wait_for_timeout(800) # Esperar un momento tras cerrar
            except Exception as e:
                print(f"Error al cerrar anuncio {idx} con selector '{selector}': {e}")
        return browser, page

    def _click_element(self, page, selectors: list, timeout: int = 5000):
        """
        Intenta hacer clic en un elemento usando una lista de selectores.
        Retorna el selector que funcionó o lanza una excepción.
        """
        for selector in selectors:
            try:
                page.wait_for_selector(selector, state="visible", timeout=timeout).click()
                print(f"✅ Clic exitoso con selector: '{selector}'")
                return selector
            except Exception as e:
                print(f"❌ Fallo al hacer clic con selector '{selector}': {e}")
        raise Exception(f"Fallo al hacer clic en todos los selectores proporcionados: {selectors}")

    def download_excels(self, product_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        with sync_playwright() as playwright:
            browser, page = self._get_page_and_handle_ads(playwright)
            df01_raw = None
            df02_raw = None
            try:
                # 1. Descargar el Excel de catálogo general
                self._click_element(page, [
                    self.cfg.playwright['selectors']['css_download_catalog'],
                    self.cfg.playwright['selectors']['xpath_download_catalog']
                ])
                download = page.wait_for_event("download", timeout=20000) # Escucha del evento de descarga
                os.makedirs(os.path.dirname(self.cfg.download_settings['catalog_excel']), exist_ok=True)
                download.save_as(self.cfg.download_settings['catalog_excel'])
                df01_raw = pd.read_excel(self.cfg.download_settings['catalog_excel'], header=0, dtype=str, keep_default_na=False)

                # 2. Rellenar y buscar el producto en la misma página
                page.fill(self.cfg.playwright['selectors']['search_input_product_name'], product_name)

                # Manejo de la lista de autocompletado
                # Espera la lista de sugerencias y haz clic en el primer elemento
                page.wait_for_selector(self.cfg.playwright['selectors']['autocomplete_dropdown'], state="visible", timeout=10000)
                page.wait_for_selector(self.cfg.playwright['selectors']['autocomplete_item02'], state="visible", timeout=5000)
                page.click(self.cfg.playwright['selectors']['autocomplete_item02']) #Selecciona uno de la lista

                # Espera a que el selector del botón de búsqueda se vuelva visible, devuelve un objeto Locator,
                # cuando lo encuentra, hace clic inmediatamente
                page.wait_for_selector(self.cfg.playwright['selectors']['search_button_product_name'], state="visible", timeout=3000).click()

                # 3. Esperar y descargar el Excel del producto
                # Espera a que el selector se vuelva visible, devuelve un objeto Locator, cuando lo encuentra, hace clic inmediatamente
                page.wait_for_selector(self.cfg.playwright['selectors']['export_excel_product_name'], state="visible", timeout=10000).click()
                download_product = page.wait_for_event("download", timeout=20000) # Escucha del evento de descarga
                os.makedirs(os.path.dirname(self.cfg.download_settings['product_excel']), exist_ok=True)
                download_product.save_as(self.cfg.download_settings['product_excel'])
                df02_raw = pd.read_excel(self.cfg.download_settings['product_excel'], header=0, dtype=str, keep_default_na=False)
                return df01_raw, df02_raw
                
            except TimeoutError:
                # Si algún `wait_for_selector` o `wait_for_event` falla, se atrapa aquí.
                print(f"❌ No se encontró el producto o el botón de descarga del Excel para '{product_name}'.")
                return df01_raw, None

            except Exception as e:
                raise Exception(f"Fallo al descargar el Excel del producto: {e}")
            
            finally:
                browser.close()

class ScrapyDownloader(IDownloader):
    def __init__(self, cfg):
        self.cfg = cfg
        self.session = requests.Session()
        self.username = os.getenv("DIGEMID_USERNAME")
        self.password = os.getenv("DIGEMID_PASSWORD")

    def download_excels(self, product_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        self.session.headers.update({'User-Agent': 'MyScraper/0.1'})
        
        # Inicia sesión y obtén el token
        login_data = {'username': self.username, 'password': self.password}
        response = self.session.post(self.cfg.scrapy['login_url'], json=login_data, timeout=30)
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise ValueError("No se pudo obtener el token de autenticación.")
        
        # Envía la solicitud POST para descargar el catálogo
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Origin': self.cfg.scrapy['origin_url'],
            'Referer': self.cfg.scrapy['referer_url'],
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
        }
        data = {
            'filtro': {
                'situacion': 'ACT',
                'tokenGoogle': token
            }
        }
        
        # Descarga el Excel de catálogo general
        try:
            response = self.session.post(self.cfg.scrapy['download_excel_url'], headers=headers, json=data, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Error al descargar el archivo Excel: {e}")

        df_general = pd.read_excel(BytesIO(response.content), dtype=str)
        
        # Filter the general DataFrame to simulate the product download for Scrapy
        df_product = df_general[df_general['nombre_producto'].str.contains(product_name, case=False, na=False)]
        
        return df_general, df_product