# app/adapters/downloader.py
from abc import ABC, abstractmethod
from app.config import ScraperConfig
import pandas as pd
from playwright.sync_api import sync_playwright
from io import BytesIO
import requests
import os

class IDownloader(ABC):
    @abstractmethod
    def download_excel(self) -> pd.DataFrame:
        ...

class PlaywrightDownloader(IDownloader):
    def __init__(self, cfg: ScraperConfig):
        self.cfg = cfg

    def download_excel(self) -> pd.DataFrame:
        with sync_playwright() as playwright:
            cfg = self.cfg
            browser = playwright.chromium.launch(headless=True)  # headless=False para ver el navegador
            #context = browser.new_context()
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()
            page.goto(cfg.url, timeout=30000)

            # Esperar a que la página cargue completamente (útil en apps Angular como DIGEMID)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)  # Espera hasta que no haya peticiones por >1s
                print("Página completamente cargada.")
            except Exception as e:
                print(f"Advertencia: La página no alcanzó 'networkidle' completamente: {e}")

            # Cerrar anuncios de la página (OJO: ACTUALIZAR SELECTORES SI CAMBIA LOS ANUNCIOS)
            for idx, selector in enumerate([cfg.css_anuncio1, cfg.css_anuncio2], start=1):
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.click(selector)
                    print(f"Anuncio {idx} cerrado con selector: {selector}")
                    page.wait_for_timeout(800)  # Esperar un momento tras cerrar
                except Exception as e:
                    print(f"Error al cerrar anuncio {idx} con selector '{selector}': {e}")
            
            # Haga clic en el botón de descarga usando el selector CSS o selector XPath
            download_selector = None
            download = None
            for selector in [cfg.css_download, cfg.xpath_download]:
                try:
                    # Asegurarse de que el elemento es visible
                    page.wait_for_selector(selector, state="visible", timeout=10000)
                    # Iniciar escucha de descarga 
                    with page.expect_download(timeout=20000) as download_info:
                        # Hacer clic DENTRO del contexto
                        page.click(selector)
                    download = download_info.value
                    download_selector = selector # El selector que funcionó
                    print(f"Descarga iniciada con selector: {selector}")
                    break
                except Exception as e:
                    print(f"Fallo con selector '{selector}': {e}")

            if not download_selector:
                raise Exception("No se pudo hacer clic en el botón de descarga")

            # Asegurar que la carpeta exista y luego guardar el archivo descargado
            download_dir = os.path.dirname(cfg.download_path)
            os.makedirs(download_dir, exist_ok=True)
            try:
                download.save_as(cfg.download_path)
                print(f"Archivo descargado y guardado en: {cfg.download_path}")
            except Exception as e:
                raise Exception(f"No se pudo guardar la descarga: {e}")
            
            browser.close()

        # Leer el archivo Excel y convertirlo a DataFrame
        # Detectar automáticamente el primer encabezado en la hoja
        df_raw = pd.read_excel(cfg.download_path, header=0, dtype=str, keep_default_na=False)
        return df_raw

class ScrapyDownloader(IDownloader):
    def __init__(self, cfg):
        self.cfg = cfg
        self.session = requests.Session()

    def download_excel(self) -> pd.DataFrame:
        self.session.headers.update({'User-Agent': 'MyScraper/0.1'})
        resp = self.session.get(self.cfg.url, timeout=30)
        resp.raise_for_status()
        
        # Si la página tiene anuncios, intenta cerrarlos
        try:
            resp = self.session.get(self.cfg.css_anuncio1, timeout=30)
            resp = self.session.get(self.cfg.css_anuncio2, timeout=30)
        except requests.RequestException:
            pass  # Si hay error al intentar cerrar el anuncio, se ignora
        
        # Descarga el Excel
        return pd.read_excel(BytesIO(resp.content), dtype=str)