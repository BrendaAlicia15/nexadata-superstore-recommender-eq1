import os
import pandas as pd
from scipy.sparse import csr_matrix

def cargar_matriz_interaccion(filepath=None):
    """Carga y valida la matriz de interacción real de forma robusta."""
    if filepath is None:
        # Obtiene la ruta absoluta de la carpeta 'src' y busca 'data' en la raíz
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, '../data/matriz_interaccion.csv')
        
    df_pivot = pd.read_csv(filepath, index_col=0)
    if df_pivot.isnull().sum().sum() > 0:
        df_pivot = df_pivot.fillna(0)
    return df_pivot

def calcular_variables_agregadas(df_transacciones):
    """Genera métricas de comportamiento: frecuencia, volumen monetario y afinidades."""
    frecuencia = df_transacciones.groupby('customer_name').size().rename('frecuencia_compra')
    volumen_monetario = df_transacciones.groupby('customer_name')['sales'].sum().rename('volumen_monetario')
    
    cat_preferencias = pd.crosstab(df_transacciones['customer_name'], df_transacciones['category'])
    cat_preferencias.columns = [f'pref_cat_{col.lower()}' for col in cat_preferencias.columns]
    
    subcat_afinidades = pd.crosstab(df_transacciones['customer_name'], df_transacciones['sub_category'])
    subcat_afinidades.columns = [f'afin_subcat_{col.lower().replace(" ", "_")}' for col in subcat_afinidades.columns]
    
    df_features = pd.concat([frecuencia, volumen_monetario, cat_preferencias, subcat_afinidades], axis=1).fillna(0)
    return df_features

def optimizar_matriz_dispersa(df_pivot):
    """Convierte la matriz densa en dispersa (CSR) y extrae listas de mapeo."""
    sparse_matrix = csr_matrix(df_pivot.values)
    lista_clientes = df_pivot.index.tolist()
    lista_productos = df_pivot.columns.tolist()
    return sparse_matrix, lista_clientes, lista_productos

if __name__ == "__main__":
    df_test = cargar_matriz_interaccion()
    print(f"Prueba exitosa - Dimensiones cargadas: {df_test.shape}")