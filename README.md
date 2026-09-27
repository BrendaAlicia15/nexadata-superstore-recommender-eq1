# 🛒 NexaData - Superstore Recommender System

![Status](https://img.shields.io/badge/Status-En%20Desarrollo-blue)
![Sprint](https://img.shields.io/badge/Sprint-1%20(% ومDemo%201)-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blueviolet)

> **Consultora:** NexaData Analytics  
> **Industria:** Comercio y Consumo (E-commerce & Retail)  
> **Proyecto:** Sistema de Recomendación Inteligente de Productos (End-to-End)

> **Problematica Inicial :** Superstore empresa global  enfrenta una creciente competencia en el mercado minorista, lo que exige una estrategia basada en datos para comprender mejor a sus clientes, productos y desempeño regional. El análisis de miles de registros de transacciones detalla pedidos, envíos y resultados financieros segmentados por categorías y regiones. El problema de negocio consiste en que la compañía no aprovecha de manera óptima su historial transaccional para perfilar las preferencias de los compradores y ofrecerles sugerencias oportunas que impulsen nuevas transacciones.

 
---

## 👥 Equipo de Trabajo
* **Product Owner (Henry):** Validación de requerimientos y objetivos de negocio.

* **Equipo de Desarrollo (Data Team):** 
  * Integrantes:
           
    1.	Barreras, Brenda - Científico de Datos
    2.	Venegas, Camilo  - Ingeniero de Datos
    3.	Domingo, Joaquín - Analista de Datos

  * Roles rotativos y multidisciplinarios en ingeniería de datos, MLOps y modelado analítico.

  ---


## 📌 1. Contexto del Negocio y del Proyecto

En el entorno competitivo del comercio electrónico actual, ofrecer experiencias de usuario personalizadas es clave para incrementar la retención, el ticket promedio y la fidelización de los clientes. El objetivo principal de este proyecto es diseñar, desarrollar e implementar un prototipo funcional de un sistema de recomendación de productos basado en el historial transaccional del dataset de Superstore.

Como equipo consultor, aplicamos el marco de trabajo Scrum con iteraciones semanales (Sprints) y la metodología CRISP-DM, asegurando la trazabilidad, la calidad y la reproducibilidad completa de todo el ciclo de vida de los datos.

---

## ⚙️ 2. Configuración del Repositorio y Git Workflow

Para garantizar una colaboración eficiente entre los miembros del equipo ubicados en Argentina, Colombia y México, y evitar conflictos en el código, se estableció un flujo de trabajo estructurado en Git:
 
* **Ramas Principales:** `main` (producción/entregables estables) y `dev` (integración continua del equipo).
* **Ramas de Características:** Ramas individuales (`feature/<nombre-componente>`) para el desarrollo aislado de scripts y notebooks.
* **Políticas de Pull Request (PR):** Prohibido el *push* directo a `dev` o `main`. Todo cambio requiere obligatoriamente un *Pull Request* acompañado de un proceso de *Code Review* por parte de al menos otro integrante del equipo.

---
## 🗂️ 3. Estructura del Proyecto

El repositorio se encuentra organizado de manera modular:

```text
nexadata-superstore-recommender-eq1/
│
├── api/
│   ├── frontend/
│   │   └── app.py            # Interfaz gráfica interactiva (Streamlit)
│   ├── main.py               # Endpoints y lógica del Backend (FastAPI)
│   └── requirements.txt      # Dependencias específicas de la API
│
├── artifacts/
│   └── pipeline/             # Datos limpios y artefactos serializados (SVD, matrices, IDs)
│
├── data/
│   ├── raw/                  # Datos originales inmutables
│   └── processed/            # Datos limpios y matrices transformadas
│
├── models/                   # Modelos entrenados y serializados
├── src/                      # Código fuente modular
│   ├── pipeline.py           # Pipeline de preprocesamiento y limpieza
│   └── train.py              # Entrenamiento del modelo (SVD + k-NN)
│
├── notebooks/                # Bitácoras de experimentación y EDA
├── setup_pipeline.py         # Script automatizado de configuración
├── test_api.py               # Pruebas automatizadas de integración
├── requirements.txt          # Dependencias generales del proyecto
└── README.md                 # Documentación principal


---
## 🔍 4. Análisis Exploratorio de Datos (EDA) & Hallazgos

El análisis ejecutado sobre los 51,290 registros y 21 columnas del dataset original (en notebooks/01_eda_and_cleaning.ipynb) permitió descubrir dinámicas comerciales y limitaciones técnicas fundamentales:

  - Márgenes y Descuentos: Se identificaron categorías y subcategorías específicas (como Tables) que generan pérdidas financieras (negative profit) debido a políticas de descuentos excesivos (superiores al 30%).

  - Sparsity (Escasez): La matriz de interacción usuario-producto presenta una dispersión superior al 99%, reflejando que los clientes adquieren solo una fracción muy reducida del catálogo general.

  - Cola Larga (Long Tail): Un alto porcentaje de productos registra muy pocas transacciones, concentrándose la demanda operativa en artículos de alta rotación.

  - Arranque en Frío (Cold Start): Se evidenció la necesidad de diseñar estrategias de respaldo (fallback basados en popularidad) para nuevos usuarios o productos sin historial transaccional previo.

 
---
## 🧹 5. Tratamiento de Datos y Limpieza
 
 Implementado modularmente en src/preprocessing.py, el pipeline de limpieza asegura la reproducibilidad ante nuevas ingestas de datos:
 
  - Detección y tratamiento estandarizado de valores nulos y duplicados transaccionales.
  - Limpieza, homologación y tipado correcto de variables monetarias y temporales (sales, profit, fechas de envío y pedido).
  - Cuantificación del impacto de cada decisión de limpieza para certificar la integridad analítica del dataset procesado.

  Implementado modularmente en src/pipeline.py y src/train.py:
  - Limpieza estandarizada de valores nulos y duplicados con un 100% de retención de datos limpios (51,290 transacciones procesadas).
  - Construcción de una matriz de interacción masiva para 795 clientes y 10,292 productos únicos.

---
## 🛠️ 6. Ingeniería de Características

Diseñado en src/features.py y documentado en notebooks/02_feature_engineering.ipynb, este bloque comprende:
  - Construcción de las matrices de interacción de usuarios y productos normalizadas.
  - Generación de variables agregadas de alto valor analítico: frecuencia de compra por cliente, volumen monetario acumulado, categorías preferidas y métricas de afinidad cruzada entre subcategorías.

---


🚀 7. Sprint 2: Evaluación, Despliegue y Demo Funcional

Durante el Sprint 2, el equipo consolidó la solución técnica incorporando:

- Modelo Híbrido Óptimo: Combinación de Reducción Dimensional (TruncatedSVD con 50 componentes) y Filtrado Colaborativo basado en Vecinos Cercanos ($k$-NN con $k=10$), alcanzando un Hit Rate @ 5 de 8.81%.

- API de Producción (FastAPI): Exposición de endpoints robustos para consultas en tiempo real y métricas de evaluación formal (/evaluacion/metricas).

- Dashboard Interactivo (Streamlit): Interfaz web moderna con navegación orientada a la toma de decisiones de negocio, permitiendo buscar productos similares con nombres comerciales reales y consultar los KPIs clave.

---

🛠️ 8. Guía de Ejecución Local (Despliegue Dual)
Para levantar todo el sistema de manera local (Backend y Frontend en paralelo), abre dos terminales independientes en la raíz del proyecto y sigue estos pasos:

Activar tu entorno virtual:

# En Windows:

venv\Scripts\activate

# En Mac/Linux:

source venv/bin/activate

Instalar dependencias:

pip install -r requirements.txt

pip install -r api/requirements.txt

Ejecutar el Pipeline de Configuración y Pruebas:

python setup_pipeline.py

python test_api.py

Levantar los Servicios en Paralelo:

Terminal 1 (Backend - FastAPI):

uvicorn api.main:app --reload

Terminal 2 (Frontend - Streamlit):

streamlit run api/frontend/app.py

(La interfaz web se abrirá automáticamente en http://localhost:8501/) [cite: 4]

---

## 📋 9. Estructura y Artefactos del Pipeline
El sistema se basa en un catálogo validado de 10,292 productos únicos y 795 clientes, procesando un total de 51,290 transacciones. Los artefactos oficiales se generan de forma reproducible y se almacenan en artifacts/pipeline/:

product_ids.json: Identificadores únicos del catálogo.
product_vectors.joblib: Matriz de vectores latentes ($10,292 \times 50$) [cite: 4].
product_knn.joblib: Modelo k-NN ajustado con 10,292 muestras [cite: 4].


## 🚀 10. Instrucciones de Instalación y Ejecución
 
 1. Clonar el repositorio:
 git clone [https://github.com/tu-usuario/nexadata-superstore-recommender.git](https://github.com/tu-usuario/nexadata-superstore-recommender.git)
 cd nexadata-superstore-recommender

 2. Crear y activar un entorno virtual:
 python -m venv venv
 # En Windows:
 venv\Scripts\activate
 # En Mac/Linux:
 source venv/bin/activate

 3. Instalar las dependencias:
 pip install -r requirements.txt

 4. Ejecutar el pipeline completo desde la raíz del repositorio:
  ```powershell
   python -m src.pipeline
  ```

   El comando lee `data/raw/SuperStoreOrders - SuperStoreOrders.csv`, limpia
   las transacciones, construye la matriz cliente-producto y entrena el modelo
   SVD + KNN. Los resultados se guardan en `artifacts/pipeline/`.

   Cada ejecución crea además un JSON en `artifacts/pipeline/runs/` con el hash
   del CSV de entrada, el commit de Git, las versiones del entorno, los
   parámetros y los hashes de los artefactos. Esta carpeta se excluye de Git.

   Para usar otras rutas:

  ```powershell
   python -m src.pipeline --raw-data "ruta/al/archivo.csv" --output-dir "ruta/de/salida"
  ```
---

## 🛠️ 11. Guía de Instalación y Ejecución Local

Paso 1: Clonar el repositorio y configurar entorno

git clone [https://github.com/BrendaAlicia15/nexadata-superstore-recommender-eq1.git](https://github.com/BrendaAlicia15/nexadata-superstore-recommender-eq1.git)
cd nexadata-superstore-recommender-eq1

# Crear y activar entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

Paso 2: Instalar dependencias
pip install -r requirements.txt
pip install -r api/requirements.txt

Paso 3: Ejecutar el Pipeline de Configuración y Pruebas
python setup_pipeline.py
python test_api.py

Paso 4: Levantar los Servicios (Despliegue Dual en Paralelo)
Para levantar todo el sistema, abre dos terminales independientes con tu entorno virtual activo:

Terminal 1 (Backend - FastAPI):
uvicorn api.main:app --reload

Terminal 2 (Frontend - Streamlit):
streamlit run api/frontend/app.py
  (La interfaz web se abrirá automáticamente en http://localhost:8501/)


   
---

## 📋 12. Estructura y Artefactos del Pipeline
El sistema se basa en un catálogo validado de **10,292 productos únicos** y **795 clientes**, procesando un total de 51,290 transacciones. Los artefactos oficiales se generan de forma reproducible y se almacenan en `artifacts/pipeline/`:
* `product_ids.json`: Identificadores únicos del catálogo.
* `product_vectors.joblib`: Matriz de vectores latentes ($10,292 \times 50$)[cite: 4].
* `product_knn.joblib`: Modelo k-NN ajustado con 10,292 muestras[cite: 4].

---

## 🛠️ 13. Guía de Instalación y Ejecución Dashboard Estratégico

1. Abrir la terminal y activar tu entorno virtual
Abre una terminal (o la consola de tu editor como VS Code) situada en la carpeta raíz de tu proyecto (nexadata-superstore-recommender-eq1/) y activa tu entorno virtual:

En Windows (CMD o PowerShell): 
Bash
venv\Scripts\activate

En Mac / Linux:
Bash
source venv/bin/activate


2. Verificar dependencias necesarias
Asegúrate de tener instaladas las librerías requeridas para levantar la interfaz y procesar los modelos (Streamlit, Pandas, Plotly, Scikit-learn, Joblib):

Bash
pip install streamlit pandas plotly scikit-learn joblib


3. Verificar la ubicación de los archivos clave
Para que el dashboard cargue tanto los datos reales como el modelo de Machine Learning sin errores, verifica que estén en sus respectivas rutas dentro del proyecto:

Dataset limpio: artifacts/pipeline/superstore_cleaned.csv (o en la raíz como respaldo).
Modelo k-NN serializado: artifacts/pipeline/product_knn.joblib.

4. Ejecutar la aplicación con Streamlit
Corre el siguiente comando en tu terminal 
Bash
streamlit run dashboard_estrategico.py

Streamlit compilará la aplicación de manera inmediata y te proporcionará en la terminal las URLs locales (por ejemplo: http://localhost:8501 o el puerto que asigne automáticamente).

La interfaz gráfica se abrirá de forma automática en tu navegador web predeterminado lista para que interactúes con los reportes estratégicos, el análisis geográfico y el motor de venta cruzada.


## 📊 14. Actualización del Sistema: Módulos de Inteligencia de Negocio y Optimización de Inventario (Streamlit Dashboard)
1. Panel Ejecutivo de Rendimiento Comercial (KPIs y Reportes Globales)

Métricas Principales: Incorporación de tarjetas ejecutivas para el seguimiento en tiempo real de:

- Ventas Totales (en USD).
- Ganancias Totales (en USD).
- Ticket Promedio global de la compañía.
- Volumen Total de Órdenes registradas.
- Visualizaciones Interactivas (Plotly):
- Gráficas de barras comparativas de Ventas Totales por Categoría (Furniture, Office Supplies, Technology).
- Gráfica de barras horizontales del Top de Países con Mayor Volumen de Ventas.
- Diagrama de anillos (Donut Chart) con el Desglose de Ventas por Subcategoría.
- Análisis de distribución de ventas por Segmento de Clientes (Consumer, Corporate, Home Office).

2. Análisis Temporal, Geográfico y Preferencias del Consumidor por País

- Evolución Temporal: Gráfica de líneas interactiva que muestra la tendencia y el crecimiento acumulado de las Ventas por Año.
- Filtro Geográfico Interactivo: Selector dinámico por país que ajusta de manera automática:
- Las Subcategorías Preferidas en la región seleccionada.
- Los Productos Estrella y su respectivo volumen transaccional.
- El Top 10 de Productos con Mayor Venta en ese mercado específico.
- Insights Automáticos Regionales: Cajas de recomendación dinámicas que calculan el ticket promedio local y sugieren tácticas   
  comerciales adaptadas al comportamiento de compra de cada país.

 3. Motor de Recomendación, Venta Cruzada y Optimización de Inventario (k-NN)
 
 Clasificación de Rotación de SKU: El sistema analiza y etiqueta automáticamente el producto seleccionado en dos categorías operativas:

- Alta Rotación 🚀: Productos ancla de gran tracción comercial ideales para estrategias de crecimiento (Cross-Selling).
- Stock Lento / Clearance ⚠️: Artículos con baja salida en almacén, identificados como candidatos prioritarios para liquidación.

Cálculo Financiero y de Ahorro en Paquetes:

- Selección interactiva de la cantidad de recomendaciones ($N$ vecinos del modelo $k$-NN) y del porcentaje de descuento del combo.- - - Cálculo dinámico del Valor Original del Combo frente al Precio con Descuento, mostrando de forma clara el Ahorro Total para el  
  Cliente en USD.

Planes de Acción Comercial Automatizados:

- Para Stock Lento: Estrategias de liquidación para liberar espacio físico en almacén y recuperar capital de trabajo sin devaluar la marca mediante rebajas aisladas.

- Para Alta Rotación: Tácticas de empaquetado (Bundling) con artículos complementarios para elevar de forma inmediata el ticket promedio.
