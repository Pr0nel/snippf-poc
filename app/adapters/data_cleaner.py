from typing import Any
import pandas as pd

class DataFrameCleaner:
    """Responsabilidad única: limpiar el Excel descargado."""
    def clean(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raw_df.columns = raw_df.iloc[0] # Asignar los nombres de las columnas del primer renglón
        return raw_df[1:]   # Borrar el primer renglón que ahora es la cabecera