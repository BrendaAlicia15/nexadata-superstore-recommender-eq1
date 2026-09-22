import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="Nexadata Superstore - Recomendador Híbrido",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

st.title("🛍️ Sistema de Recomendación - Nexadata Superstore")
st.markdown("Plataforma comercial inteligente impulsada por modelos híbridos (SVD + k-NN).")

# Creación de Pestañas para cumplir con la rúbrica del Dashboard Interactivo
tab1, tab2 = st.tabs(["🔍 Motor de Recomendación", "📊 Métricas y Validación del Modelo"])

with tab1:
    st.header("Búsqueda de Productos Similares")
    
    producto_id = st.text_input("ID del Producto (SKU):", value="OFF-AR-10003651")
    top_n = st.slider("Cantidad de recomendaciones:", min_value=1, max_value=10, value=5)

    if st.button("Obtener Recomendaciones Híbridas"):
        try:
            response = requests.get(f"{API_URL}/recomendaciones/similares/{producto_id}?top_n={top_n}")
            data = response.json()
            
            if response.status_code != 200:
                st.error(data.get("detail", "Ocurrió un error al procesar la solicitud."))
            else:
                st.success("¡Recomendaciones generadas exitosamente!")
                
                # Mostrar info del modelo de forma limpia si es un diccionario
                modelo_info = data.get('modelo', {})
                if isinstance(modelo_info, dict):
                    modelo_str = f"{modelo_info.get('tipo')} ({modelo_info.get('algoritmo')} - SVD: {modelo_info.get('svd_components')} comp, k-NN: k={modelo_info.get('knn_k')})"
                else:
                    modelo_str = str(modelo_info)
                
                st.info(f"**Modelo utilizado:** {modelo_str}")
                
                orig = data.get("producto_origen", {})
                st.markdown(f"📌 **Producto de Origen:** {orig.get('nombre')} (*Categoría: {orig.get('categoria')}* | SKU: `{orig.get('sku')}`)")
                
                st.markdown("### 🎁 Productos Recomendados para el Cliente:")
                for i, rec in enumerate(data.get("recomendaciones", []), 1):
                    st.markdown(
                        f"**{i}. {rec.get('nombre')}** — *Cat: {rec.get('categoria')}* "
                        f"(SKU: `{rec.get('sku')}` | Score de Similitud: `{rec.get('score_similitud', 0)}`)"
                    )
                    if 'explicacion' in rec:
                        st.caption(f"💡 *{rec.get('explicacion')}*")
        except Exception as e:
            st.error(f"No se pudo conectar con la API: {e}")

with tab2:
    st.header("Evaluación y Métricas de Negocio (Sprint 2)")
    st.markdown("Indicadores clave de rendimiento (KPIs) del sistema de recomendación optimizado.")
    
    try:
        res_metrics = requests.get(f"{API_URL}/evaluacion/metricas")
        if res_metrics.status_code == 200:
            metrics_data = res_metrics.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Hit Rate @ 5", value=metrics_data["metricas_clave"]["hit_rate_at_5"])
            with col2:
                st.metric(label="Esparsidad de la Matriz", value=metrics_data["metricas_clave"]["esparsidad_matriz"])
            with col3:
                st.metric(label="Catálogo Total", value=f"{metrics_data['metricas_clave']['total_productos_catalogo']} ítems")
                
            st.subheader("📋 Protocolo de Validación")
            st.write(metrics_data.get("protocolo_validacion"))
            
            st.subheader("⚙️ Modelo Seleccionado")
            st.write(metrics_data.get("modelo_seleccionado"))
            
            st.subheader("💡 Análisis Crítico y Decisiones Técnicas")
            st.success(metrics_data.get("analisis_critico"))
        else:
            st.warning("Carga las métricas ejecutando la API en el puerto 8000.")
    except Exception:
        st.warning("Asegúrate de que la API esté encendida para visualizar las métricas en tiempo real.")