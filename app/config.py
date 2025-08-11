import os
from dataclasses import dataclass

@dataclass
class ScraperConfig:
    url: str = os.getenv("DIGEMID_URL", "https://opm-digemid.minsa.gob.pe/#/consulta-producto")
    css_download: str = os.getenv("CSS_DOWNLOAD", "body > app-root > app-consulta-productos-listar > div:nth-child(2) > div.card > div > div.centro.p-0.m-0 > a > span")
    xpath_download: str = os.getenv("XPATH_DOWNLOAD", "xpath="+"/html/body/app-root/app-consulta-productos-listar/div[2]/div[2]/div/div[2]/a/span")
    css_anuncio1: str = os.getenv("CSS_ANUNCIO1", "body > ngb-modal-window > div > div > app-modal-comunicacion > div.modal-footer.pr-3.pl-3 > button")
    css_anuncio2: str = os.getenv("CSS_ANUNCIO2", "body > ngb-modal-window > div > div > app-modal-informativo-inicio > div.modal-footer.pr-3.pl-3 > button")
    download_path: str = os.getenv("DOWNLOAD_PATH", "docs/catalogoproductos.xlsx")
    