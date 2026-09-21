from fastapi import FastAPI
import joblib
import os
import numpy as np
import pandas as pd
from functools import lru_cache

# 1. Definición inicial de rutas del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="API de Recomendaciones - Nexadata Superstore",
    description="API enriquecida con nombres comerciales y categorías",
    version="2.2.0"
)

modelo_baseline = None
modelo_knn = None
matriz_interacciones = None
lista_ids_productos = []
diccionario_productos = {}

try:
    print("Cargando modelos de Machine Learning y Base de Datos de Productos...")
    ruta_baseline = os.path.join(BASE_DIR, "notebooks", "modelo_baseline.pkl")
    ruta_knn = os.path.join(BASE_DIR, "notebooks", "modelo_knn.pkl")
    ruta_matriz = os.path.join(BASE_DIR, "notebooks", "sparse_matrix_item_user.pkl")
    ruta_catalogo = os.path.join(BASE_DIR, "notebooks", "catalogo_productos.pkl")
    
    # 2. Ruta exacta al archivo maestro en data/raw/
    ruta_csv_orders = os.path.join(BASE_DIR, "data", "raw", "SuperStoreOrders - SuperStoreOrders.csv")
    
    if os.path.exists(ruta_csv_orders):
        df_orders = pd.read_csv(ruta_csv_orders, encoding='latin1')
        df_orders.columns = [c.lower().strip() for c in df_orders.columns]
        
        if 'product_id' in df_orders.columns and 'product_name' in df_orders.columns:
            df_unique = df_orders.drop_duplicates(subset=['product_id'])
            for _, row in df_unique.iterrows():
                pid = str(row['product_id']).strip()
                pname = str(row['product_name'])
                pcat = str(row['category']) if 'category' in df_orders.columns else "General"
                diccionario_productos[pid] = {"nombre": pname, "categoria": pcat}
            print(f"¡Base de datos cargada con éxito! Total productos mapeados: {len(diccionario_productos)}")
        else:
            print("⚠️ Las columnas product_id o product_name no se encontraron en el CSV.")
    else:
        print(f"⚠️ No se encontró el archivo en la ruta: {ruta_csv_orders}")

    modelo_baseline = joblib.load(ruta_baseline)
    modelo_knn = joblib.load(ruta_knn)
    matriz_interacciones = joblib.load(ruta_matriz)
    catalogo_productos = joblib.load(ruta_catalogo)
    
    try:
        lista_ids_productos = catalogo_productos.index.tolist()
    except AttributeError:
        lista_ids_productos = list(catalogo_productos)
        
    print("¡Modelos y recursos cargados exitosamente!")
except Exception as e:
    print(f"Error crítico al cargar recursos: {e}")

def obtener_info_producto(prod_id: str):
    """Consulta la base de datos cruzada para extraer el nombre comercial real y categoría."""
    prod_id_clean = str(prod_id).strip()
    if prod_id_clean in diccionario_productos:
        info = diccionario_productos[prod_id_clean]
        return {
            "id": prod_id_clean,
            "nombre": info["nombre"],
            "categoria": info["categoria"]
        }
    else:
        return {
            "id": prod_id_clean,
            "nombre": f"Producto {prod_id_clean}",
            "categoria": "General"
        }

@lru_cache(maxsize=128)
def calcular_similitud_cached(indice_producto: int, top_n: int):
    matriz_trabajo = matriz_interacciones
    max_filas = matriz_trabajo.shape[0] if hasattr(matriz_trabajo, "shape") else len(matriz_trabajo)
    indice_seguro = indice_producto % max_filas if indice_producto >= max_filas else indice_producto

    if hasattr(matriz_trabajo, 'tocsr'):
        vector_producto = matriz_trabajo.getrow(indice_seguro)
    elif hasattr(matriz_trabajo, 'iloc'):
        vector_producto = matriz_trabajo.iloc[indice_seguro].values.reshape(1, -1)
    else:
        vector_producto = matriz_trabajo[indice_seguro]
        if hasattr(vector_producto, 'ndim') and vector_producto.ndim == 1:
            vector_producto = vector_producto.reshape(1, -1)

    n_features_esperadas = getattr(modelo_knn, "n_features_in_", vector_producto.shape[1])
    if vector_producto.shape[1] != n_features_esperadas:
        if vector_producto.shape[1] > n_features_esperadas:
            vector_producto = vector_producto[:, :n_features_esperadas]
        else:
            padding = np.zeros((vector_producto.shape[0], n_features_esperadas - vector_producto.shape[1]))
            vector_producto = np.hstack([vector_producto, padding])

    distancias, indices = modelo_knn.kneighbors(vector_producto, n_neighbors=top_n + 1)
    return indices.flatten()[1:].tolist()

@app.get("/")
def read_root():
    return {"mensaje": "API de Recomendaciones Avanzada - Nexadata Superstore"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API lista y operando."}

@app.get("/recomendaciones/similares/{producto_id}")
def obtener_recomendaciones_similares(producto_id: str, top_n: int = 5):
    try:
        if matriz_interacciones is None or modelo_knn is None:
            return {"error": "Modelos no cargados."}

        if producto_id not in lista_ids_productos:
            return {"error": f"El producto '{producto_id}' no se encontró en el catálogo."}
            
        indice_producto = lista_ids_productos.index(producto_id)
        indices_recomendados = calcular_similitud_cached(indice_producto, top_n)
        
        recomendaciones_enriquecidas = []
        for i in indices_recomendados:
            mapped_idx = int(i) % len(lista_ids_productos)
            pid = lista_ids_productos[mapped_idx]
            recomendaciones_enriquecidas.append(obtener_info_producto(pid))
        
        return {
            "modelo": "KNN Item-Based (Enriquecido con BD)",
            "producto_origen": obtener_info_producto(producto_id),
            "cantidad_solicitada": top_n,
            "recomendaciones": recomendaciones_enriquecidas[:top_n]
        }
    except Exception as e:
        idx_base = lista_ids_productos.index(producto_id) if producto_id in lista_ids_productos else 0
        ids_alt = [lista_ids_productos[(idx_base + i) % len(lista_ids_productos)] for i in range(1, top_n + 1)]
        recs_fallback = [obtener_info_producto(pid) for pid in ids_alt]
        return {
            "modelo": "KNN Item-Based (Fallback Enriquecido)",
            "producto_origen": obtener_info_producto(producto_id),
            "cantidad_solicitada": top_n,
            "recomendaciones": recs_fallback,
            "nota": "Respaldo dinámico activado con nombres de BD."
        }