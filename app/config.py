# app/config.py
import yaml
from dataclasses import dataclass

@dataclass
class ScraperConfig:
    env: str
    product_name: str
    download_settings: dict
    playwright: dict
    scrapy: dict
    
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Mapea los datos del YAML a los atributos de la clase
        return cls(
            env             = data.get('env', 'dev'),
            product_name    = data.get('product_name', None),
            download_settings  = data.get('download_settings', {}),
            playwright      = data.get('playwright', {}),
            scrapy          = data.get('scrapy', {})
        )