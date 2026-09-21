import streamlit as st
import requests

st.set_page_config(
    page_title="Nexadata Superstore - Recomendador",
    page_icon="🛒",
    layout="centered"
)

st.title("🛍️ Sistema de Recomendación - Nexadata Superstore")
st.write("Interfaz interactiva para explorar recomendaciones de productos en tiempo real.")

API_URL = "http://localhost:8000"

tab1, tab2 = st.tabs(["🔍 Similares (KNN Item-Based)", "🔥 Populares (Baseline)"])

with tab1:
    st.subheader("Búsqueda de Productos Similares")
    producto_id = st.text_input("ID del Producto:", "OFF-AR-10003651")
    top_n = st.slider("Cantidad de recomendaciones:", min_value=1, max_value=10, value=5)
    
    if st.button("Obtener Recomendaciones KNN", type="primary"):
        if not producto_id.strip():
            st.warning("Por favor, ingresa un ID válido.")
        else:
            with st.spinner("Consultando la API..."):
                try:
                    response = requests.get(f"{API_URL}/recomendaciones/similares/{producto_id.strip()}?top_n={top_n}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(data["error"])
                        else:
                            st.success("¡Recomendaciones generadas exitosamente!")
                            st.info(f"**Modelo utilizado:** {data.get('modelo')}")
                            
                            origen = data.get("producto_origen", {})
                            st.write(f"📌 **Producto de Origen:** {origen.get('nombre')} *(Categoría: {origen.get('categoria')})*")
                            
                            st.write("### 🎁 Productos Recomendados para el Cliente:")
                            for idx, prod in enumerate(data.get("recomendaciones", []), 1):
                                nombre = prod.get("nombre")
                                categoria = prod.get("categoria")
                                sku = prod.get("id")
                                st.markdown(f"**{idx}. {nombre}** — *Cat: {categoria}* (`SKU: {sku}`)")
                    else:
                        st.error("Error al conectar con la API.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ No se pudo conectar con la API de FastAPI.")

with tab2:
    st.subheader("Productos Más Populares (Baseline)")
    top_n_pop = st.slider("Cantidad:", min_value=1, max_value=10, value=5, key="pop_s")
    if st.button("Ver Populares", type="primary"):
        response = requests.get(f"{API_URL}/recomendaciones/populares?top_n={top_n_pop}")
        if response.status_code == 200:
            st.json(response.json())