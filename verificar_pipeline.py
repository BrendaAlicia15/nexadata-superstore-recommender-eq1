from pathlib import Path
import joblib

# Buscar el archivo de modelo disponible en notebooks o models
rutas_posibles = [
    Path("notebooks/hybrid_knn_optimo.pkl"),
    Path("notebooks/model_knn.pkl"),
    Path("models/recommender_pipeline.pkl")
]

modelo_cargado = None
ruta_usada = None

for ruta in rutas_posibles:
    if ruta.exists():
        try:
            print(f"Intentando cargar desde: {ruta}")
            modelo_cargado = joblib.load(ruta)
            ruta_usada = ruta
            break
        except Exception as e:
            print(f"⚠️ No se pudo leer {ruta} (posible archivo dañado): {e}")

if modelo_cargado is not None:
    print(f"✅ ¡Modelo cargado exitosamente desde {ruta_usada}!")
    if hasattr(modelo_cargado, 'n_samples_fit_'):
        print(f"Filas entrenadas en el k-NN: {modelo_cargado.n_samples_fit_}")
    else:
        print("El objeto es un pipeline o diccionario estructurado.")
else:
    print("❌ No se encontró ningún archivo de modelo válido.")

# Verificar la lista de productos
ruta_lista = Path("notebooks/lista_productos.pkl")
if ruta_lista.exists():
    lista_prod = joblib.load(ruta_lista)
    print(f"✅ Catálogo de productos detectado. Total de ítems: {len(lista_prod)}")