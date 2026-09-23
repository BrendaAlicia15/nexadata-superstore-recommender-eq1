#### ==============================================================================
#### SCRIPT OFICIAL DE CONFIGURACIÓN Y VERIFICACIÓN - NEXADATA SUPERSTORE
#### ==============================================================================
#### Guía rápida de comandos para ejecutar en la terminal:
#### 
#### 1. Configurar y verificar todo el entorno automáticamente:
####    #### python setup_pipeline.py
#### 
#### 2. Ejecutar las pruebas unitarias y de verificación de la API:
####    #### python test_api.py
#### 
#### 3. Generar los artefactos del pipeline localmente (10,292 productos):
####    #### python -m src.pipeline
#### 
#### 4. Eliminar el archivo obsoleto o vacío del control de versiones:
####    #### git rm models/recommender_pipeline.pkl
#### 
#### 5. Correr la API (Backend en FastAPI):
####    #### uvicorn api.main:app --reload
#### 
#### 6. Correr el Dashboard interactivo (Frontend en Streamlit):
####    #### streamlit run api/frontend/app.py
#### ==============================================================================

import subprocess
from pathlib import Path

def ejecutar_configuracion():
    #### Paso 1: Generar los artefactos localmente (IDs, vectores y KNN de 10,292 ítems)
    print("=== PASO 1: Generando artefactos del pipeline localmente ===")
    subprocess.run(["python", "-m", "src.pipeline"], check=True)
    
    #### Paso 2: Verificar la eliminación del archivo obsoleto de 0 bytes
    print("\n=== PASO 2: Verificando estado del archivo obsoleto ===")
    archivo_vacio = Path("models/recommender_pipeline.pkl")
    if archivo_vacio.exists():
        print("⚠️ Advertencia: El archivo obsoleto aún existe. Ejecuta en terminal: git rm models/recommender_pipeline.pkl")
    else:
        print("✅ Archivo obsoleto eliminado correctamente del control de versiones.")
        
    #### Paso 3 y 4: Ejecutar las pruebas unitarias para asegurar el 100% verde
    print("\n=== PASO 3 y 4: Ejecutando suite de pruebas y verificación (test_api.py) ===")
    subprocess.run(["python", "test_api.py"], check=True)
    print("\n🎉 ¡Entorno configurado, integrado y verificado exitosamente!")
    print("\n💡 Recuerda que puedes iniciar los servicios usando:")
    print("   - API: uvicorn api.main:app --reload")
    print("   - Dashboard: streamlit run api/frontend/app.py")

if __name__ == "__main__":
    ejecutar_configuracion()