# 🛒 NexaData - Superstore Recommender System

![Status](https://img.shields.io/badge/Status-En%20Desarrollo-blue)
![Sprint](https://img.shields.io/badge/Sprint-1%20(% ومDemo%201)-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blueviolet)

> **Consultora:** NexaData Analytics  
> **Industria:** Comercio y Consumo (E-commerce & Retail)  
> **Proyecto:** Sistema de Recomendación Inteligente de Productos  

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

El repositorio se encuentra organizado de manera modular para separar limpiamente la lógica de datos, los experimentos, los scripts de producción y las pruebas unitarias:

```text
nexadata-superstore-recommender/
│
├── api/                   # Endpoints y lógica de exposición del modelo (FastAPI)
├── data/
│   ├── raw/               # Datos originales inmutables (SuperStoreOrders.csv)
│   └── processed/         # Datos limpios y matrices transformadas
├── models/                # Modelos entrenados y serializados
├── notebooks/             # Bitácoras de experimentación y análisis
│   ├── 01_eda_and_cleaning.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_experimentation.ipynb
├── src/                   # Código fuente modular
│   ├── __init__.py
│   ├── preprocessing.py   # Scripts de limpieza y tratamiento sistémico
│   └── features.py        # Generación de matrices de interacción y variables
├── tests/                 # Pruebas unitarias e integración
├── .gitignore
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación principal del proyecto


---
## 🔍 4. Análisis Exploratorio de Datos (EDA) & Hallazgos

El análisis ejecutado sobre los 51,290 registros y 21 columnas del dataset original (en notebooks/01_eda_and_cleaning.ipynb) permitió descubrir dinámicas comerciales y limitaciones técnicas fundamentales:

  - Márgenes y Descuentos: Se identificaron categorías y subcategorías específicas (como Tables) que generan pérdidas financieras (negative profit) debido a políticas de   descuentos excesivos (superiores al 30%).

  - Sparsity (Escasez): La matriz de interacción usuario-producto presenta una dispersión superior al 99%, reflejando que los clientes adquieren solo una fracción muy reducida del catálogo general.

  - Cola Larga (Long Tail): Un alto porcentaje de productos registra muy pocas transacciones, concentrándose la demanda operativa en artículos de alta rotación.

  - Arranque en Frío (Cold Start): Se evidenció la necesidad de diseñar estrategias de respaldo (fallback basados en popularidad) para nuevos usuarios o productos sin historial transaccional previo.

 
---
🧹 5. Tratamiento de Datos y Limpieza
 
 Implementado modularmente en src/preprocessing.py, el pipeline de limpieza asegura la reproducibilidad ante nuevas ingestas de datos:
 
  - Detección y tratamiento estandarizado de valores nulos y duplicados transaccionales.
  - Limpieza, homologación y tipado correcto de variables monetarias y temporales (sales, profit, fechas de envío y pedido).
  - Cuantificación del impacto de cada decisión de limpieza para certificar la integridad analítica del dataset procesado.


---
🛠️ 6. Ingeniería de Características

Diseñado en src/features.py y documentado en notebooks/02_feature_engineering.ipynb, este bloque comprende:
  - Construcción de las matrices de interacción de usuarios y productos normalizadas.
  - Generación de variables agregadas de alto valor analítico: frecuencia de compra por cliente, volumen monetario acumulado, categorías preferidas y métricas de afinidad   
    cruzada entre subcategorías.


---
🚀 7. Instrucciones de Instalación y Ejecución
 
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

 4. Ejecutar el pipeline de procesamiento y limpieza:
 python src/preprocessing.py

---
## 🔍  8. Próximos Pasos (Sprint 2)

 Para la siguiente iteración del proyecto, el equipo de desarrollo se enfocará en:
    Finalización del modelado de filtrado colaborativo y experimentación con algoritmos de vecinos cercanos (KNN).
    Despliegue de los endpoints de recomendación mediante la API en FastAPI.
    Configuración de tableros de monitoreo y pruebas de rendimiento del sistema. 
