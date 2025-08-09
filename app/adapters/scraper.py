# app/adapters/scraper.py
from abc import ABC, abstractmethod
from typing import Protocol
import pandas as pd
from io import BytesIO
import os
from playwright.sync_api import sync_playwright
import requests

class IDigemidScraper(Protocol):
    """Protocolo (interfaz estructural) para el scraper."""

    def download(self) -> pd.DataFrame:
        ...

class DigemidScraper(IDigemidScraper):
    """
    Implementación concreta:
    descarga el Excel oficial de DIGEMID y lo convierte a DataFrame limpio.
    """

    def download(self) -> pd.DataFrame:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)  # headless=False para ver el navegador
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://opm-digemid.minsa.gob.pe/#/consulta-producto")

            # Cerrar anuncios si existen
            try:
                # Haga clic en el botón de cierre de anuncios (asumiendo que hay un botón con este selector)
                page.click("body > ngb-modal-window > div > div > app-modal-comunicacion > div.modal-footer.pr-3.pl-3 > button")
            except Exception as e:
                print(f"Error al cerrar el primer anuncio: {e}")
            try:
                # Haga clic en el botón de cierre de anuncios (asumiendo que hay un botón con este selector)
                page.click("body > ngb-modal-window > div > div > app-modal-informativo-inicio > div.modal-footer.pr-3.pl-3 > button")
            except Exception as e:
                print(f"Error al cerrar el segundo anuncio: {e}")
            
            # Haga clic en el botón de descarga usando el selector CSS
            try:
                page.click("body > app-root > app-consulta-productos-listar > div:nth-child(2) > div.card > div > div.centro.p-0.m-0 > a > span")
            except Exception as e:
                print(f"Error con el primer selector CSS: {e}")
                # Intentar el segundo selector XPath si el primero falla
                try:
                    page.click("xpath=/html/body/app-root/app-consulta-productos-listar/div[2]/div[2]/div/div[2]/a/span")
                except Exception as e:
                    print(f"Error con el segundo selector XPath: {e}")
            
            # Esperar a que el archivo se descargue
            with page.expect_download() as download_info:
                pass
            download = download_info.value
            download_path = download.path
            download.save_as("catalogoproductos.xlsx")
            
            browser.close()

        # Leer el archivo Excel y convertirlo a DataFrame
        # Detectar automáticamente el primer encabezado en la hoja
        df = pd.read_excel("catalogoproductos.xlsx", header=0, dtype=str, keep_default_na=False)

        # Normalización mínima
        df.columns = df.iloc[0]  # Asignar los nombres de las columnas del primer renglón
        df = df[1:]  # Borrar el primer renglón que ahora es la cabecera
        
        return df

# Uso del scraper
if __name__ == "__main__":
    scraper = DigemidScraper()
    df = scraper.download()
    if df is not None:
        print(df.head())
    else:
        print("No se pudo descargar el archivo.")