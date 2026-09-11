# Propósito de data_loader.py, Función principal: Centralizar y estandarizar la carga del archivo de datos crudos (SuperStoreOrders - SuperStoreOrders.csv) desde la carpeta data/raw/.
# Ventaja modular: Evita repetir código de lectura de archivos en cada Jupyter Notebook o script de modelado, asegurando que cualquier transformación inicial o conversión de tipos de datos se aplique de forma consistente desde el origen.

import pandas as pd
from pathlib import Path

def cargar_datos_crudos(filepath: str = '../data/raw/SuperStoreOrders - SuperStoreOrders.csv') -> pd.DataFrame:
    """
    Carga el dataset crudo de Superstore asegurando rutas relativas correctas
    y validando la existencia del archivo.
    """
    ruta_archivo = Path(filepath)
    
    if not ruta_archivo.exists():
        # Intenta ajustar la ruta si se ejecuta desde la raíz del proyecto en lugar de notebooks/
        ruta_alternativa = Path('data/raw/SuperStoreOrders - SuperStoreOrders.csv')
        if ruta_alternativa.exists():
            ruta_archivo = ruta_alternativa
        else:
            raise FileNotFoundError(f"No se pudo encontrar el archivo en la ruta: {filepath}")
            
    print(f"--- CARGANDO DATOS DESDE: {ruta_archivo} ---")
  
    df = pd.read_csv(ruta_archivo, encoding='utf-8')
    print(f"Registros totales cargados: {df.shape[0]:,}".replace(',', '.'))
    print(f"Columnas detectadas: {list(df.columns)}")
    
    return df

if __name__ == '__main__':
    # Prueba rápida de ejecución del módulo
    df_test = cargar_datos_crudos()
    print(df_test.head(3))