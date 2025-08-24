# app/adapters/data_cleaner.py
from typing import Any
import pandas as pd
from datetime import datetime

class DataFrameCleaner:
    """Responsabilidad única: limpiar el Excel descargado."""
    def clean(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raw_df.columns = raw_df.iloc[0] # Asignar los nombres de las columnas del primer renglón
        return raw_df[1:]   # Borrar el primer renglón que ahora es la cabecera
    
    def clean_catalog(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia el DataFrame del catálogo general, extrae la fecha de actualización
        y establece la cabecera correcta.
        """
        try:
            # 1. Extraer la fecha de actualización de la celda B6
            # La celda B6 se encuentra en la fila con índice 4 y columna con índice 1
            raw_date_value = raw_df.iloc[4, 1]
            update_date = pd.to_datetime(raw_date_value, format='%d/%m/%Y %I:%M:%S %p')

            # 2. Establecer la fila de la cabecera (fila 7, índice 6) y eliminar metadatos
            # Asignar la fila 7 como la cabecera del DataFrame
            raw_df.columns = raw_df.iloc[5]
            # Eliminar las filas de metadatos (incluyendo la fila de cabecera original)
            cleaned_df = raw_df.iloc[6:].reset_index(drop=True)
            
            # 3. Agregar la columna de la fecha de actualización y de datos
            cleaned_df['fec_actualizacion_cpf'] = update_date
            cleaned_df['fec_datos'] = datetime.now()
            
            return cleaned_df
            
        except Exception as e:
            # Si la limpieza falla, es mejor saber por qué
            raise Exception(f"Fallo en la limpieza del catálogo general: {e}")
        
    def clean_product(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia el DataFrame del precio productos.
        """
        try:
            # 1. Establecer la fila de la cabecera (fila 8, índice 7) y eliminar metadatos
            # Asignar la fila 8 como la cabecera del DataFrame
            raw_df.columns = raw_df.iloc[6]
            # Eliminar las filas de metadatos (incluyendo la fila de cabecera original)
            cleaned_df = raw_df.iloc[7:].reset_index(drop=True)
            
            # 2. Agregar la columna de la fecha de datos
            cleaned_df['fec_datos'] = datetime.now()
            
            return cleaned_df
            
        except Exception as e:
            # Si la limpieza falla, es mejor saber por qué
            raise Exception(f"Fallo en la limpieza del catálogo general: {e}")