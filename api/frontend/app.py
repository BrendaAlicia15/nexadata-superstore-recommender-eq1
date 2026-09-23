import streamlit as st
import requests

st.set_page_config(
    page_title="Nexadata Superstore - Recomendador Híbrido",
    page_icon="🛍️",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
    <style>
        .main-header { font-size: 26px; font-weight: 700; color: #1E3A8A; }
        .sub-header { font-size: 16px; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛍️ Nexadata Superstore - Sistema de Recomendación Híbrido</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plataforma comercial inteligente impulsada por modelos híbridos (TruncatedSVD + k-NN) sincronizada con el pipeline oficial.</p>', unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🔍 Motor de Recomendación", "📊 Métricas y Validación del Modelo"])

with tab1:
    st.subheader("Búsqueda Interactiva de Productos Similares")
    
    col_input1, col_input2 = st.columns([2, 1])
    
    with col_input1:
        # Entrada directa por ID o SKU manual
        producto_seleccionado = st.text_input(
            "Ingresa o pega el ID del producto (SKU):",
            value="OFF-AR-10003651"
        ).strip()
    
    with col_input2:
        top_n = st.slider("Cantidad de recomendaciones:", min_value=1, max_value=10, value=5)

    if st.button("🚀 Obtener Recomendaciones Híbridas", type="primary"):
        with st.spinner("Consultando el espacio latente del modelo y métricas financieras..."):
            try:
                response = requests.get(f"{API_URL}/recomendaciones/similares/{producto_seleccionado}?top_n={top_n}")
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("¡Recomendaciones generadas exitosamente!")
                    
                    modelo_info = data.get("modelo", {})
                    st.info(f"**Modelo utilizado:** {modelo_info.get('tipo')} ({modelo_info.get('algoritmo')} - SVD: {modelo_info.get('svd_components')} comp, k-NN: k={modelo_info.get('knn_k')})")
                    
                    origen = data.get("producto_origen", {})
                    st.markdown(f"📌 **Producto de Origen:** {origen.get('nombre')} (*Categoría: {origen.get('categoria')}* | SKU: `{origen.get('sku')}`)")
                    
                    st.markdown("### 🎁 Productos Recomendados y Desempeño Comercial:")
                    st.info("ℹ️ **Nota sobre los scores de similitud:** Los valores indican qué tan cerca están los productos en el espacio latente del modelo (hasta 1.0). Las métricas reflejan el desempeño histórico real del ítem.")
                    
                    recomendaciones = data.get("recomendaciones", [])
                    for rec in recomendaciones:
                        pos = rec.get("posicion")
                        nombre = rec.get("nombre")
                        sku = rec.get("sku")
                        categoria = rec.get("categoria")
                        score = rec.get("score_similitud")
                        explicacion = rec.get("explicacion")
                        metricas = rec.get("metricas", {})
                        
                        sales = metricas.get("sales", 0.0)
                        qty = metricas.get("quantity", 0)
                        profit = metricas.get("profit", 0.0)
                        
                        with st.container():
                            c1, c2, c3 = st.columns([2.5, 1, 1])
                            with c1:
                                st.markdown(f"**{pos}. {nombre}** — *Cat: {categoria}* (`SKU: {sku}`)")
                                st.caption(f"💡 {explicacion}")
                            with c2:
                                st.metric("Similitud", f"{score:.2f}")
                                st.progress(float(score))
                            with c3:
                                st.markdown(f"💵 **Ventas:** ${sales:,.2f}")
                                st.markdown(f"📦 **Unidades:** {qty:,}")
                                st.markdown(f"📈 **Ganancia:** ${profit:,.2f}")
                            st.markdown("---")
                            
                elif response.status_code == 404:
                    st.error(f"El producto con ID '{producto_seleccionado}' no se encuentra registrado en el catálogo.")
                else:
                    st.error(f"Error en la API: {response.text}")
            except Exception as e:
                st.error(f"No se pudo conectar con el servidor de FastAPI. Detalle: {e}")

with tab2:
    st.subheader("Panel de Métricas y Validación del Pipeline")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="🎯 Hit Rate @ 5", value="8.81%", delta="Validado en prueba")
    with kpi2:
        st.metric(label="📐 Esparsidad de Matriz", value="99.38%", delta="Optimizado SVD")
    with kpi3:
        st.metric(label="📦 Catálogo Comercial", value="10,292", delta="Ítems sincronizados")
        
    st.markdown("---")
    
    st.markdown("### 📋 Resumen Ejecutivo y Diagnóstico del Modelo")
    
    col_desc1, col_desc2 = st.columns(2)
    with col_desc1:
        st.markdown("""
            * **Protocolo de Validación:** Split temporal / Validación cruzada offline (80% entrenamiento, 20% prueba).
            * **Arquitectura:** Modelo híbrido basado en descomposición de valores singulares truncados (`TruncatedSVD`) y vecinos más cercanos (`k-NN`).
            * **Trazabilidad:** Integración directa con los artefactos del pipeline y el catálogo comercial oficial.
        """)
    with col_desc2:
        st.markdown("""
            * **Impacto Comercial:** Maximiza la tasa de acierto en las primeras 5 recomendaciones y provee explicabilidad automática por categoría y ventas cruzadas.
            * **Optimización Espacial:** Reduce la dimensionalidad a 50 componentes latentes mitigando la alta esparsidad de la matriz de transacciones.
        """)
        
    st.markdown("---")
    st.subheader("Reporte JSON Consolidado de la API")

    try:
        res_metricas = requests.get(f"{API_URL}/evaluacion/metricas")
        if res_metricas.status_code == 200:
            m_data = res_metricas.json()
            st.json(m_data)
    except:
        st.info("Inicia el servidor backend para visualizar el reporte JSON completo de métricas.")