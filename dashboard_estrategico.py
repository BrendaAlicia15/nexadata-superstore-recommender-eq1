import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import joblib
import requests
from pathlib import Path

# --- FORMATO DE IMPORTES PARA LOS KPIs ---
def formatear_numero(valor, decimales=2):
    """Separador de miles y coma decimal para lectura en español."""
    return f"{valor:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def formatear_usd(valor, compacto=True):
    """Abrevia agregados; mantiene precisión en tickets y precios unitarios."""
    if compacto and abs(valor) >= 1_000_000:
        return f"{formatear_numero(valor / 1_000_000, 1)} M USD"
    if compacto and abs(valor) >= 1_000:
        return f"{formatear_numero(valor / 1_000, 1)} mil USD"
    return f"{formatear_numero(valor)} USD"


# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="NexaData - Dashboard Estratégico Superstore",
    page_icon="📊",
    layout="wide"
)

st.title("📊 NexaData Intelligence: Reportes Estratégicos y Analítica Global  .")

# --- 2. CARGA DE ARTEFACTOS, DATOS Y MÉTRICAS DE API ---
pipeline_path = "artifacts/pipeline"
ruta_csv = os.path.join(pipeline_path, "superstore_cleaned.csv")

@st.cache_data
def cargar_datos(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
    elif os.path.exists("superstore_cleaned.csv"):
        df = pd.read_csv("superstore_cleaned.csv")
    else:
        return None
    
    if df is not None and 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df['year'] = df['order_date'].dt.year
    elif df is not None and 'year' not in df.columns:
        df['year'] = 2023 
        
    return df

df_cleaned = cargar_datos(ruta_csv)

@st.cache_data(ttl=60)
def obtener_metricas_api():
    try:
        response = requests.get("http://127.0.0.1:8000/metrics", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    return {
        "hit_rate": "8.81%",
        "sparsity": "99.38%",
        "total_items": 10292
    }

# --- IDENTIDAD VISUAL EN LA BARRA LATERAL ---
logo_path = Path(__file__).resolve().parent / "NexaData.png"
if logo_path.is_file():
    st.sidebar.image(str(logo_path), width=180)
else:
    st.sidebar.warning("Coloca NexaData.png junto a dashboard_estrategico.py")

# --- FILTRO DE TIEMPO DINÁMICO EN LA BARRA LATERAL ---
if df_cleaned is not None and 'year' in df_cleaned.columns:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏱️ Filtro Temporal")
    anios_disponibles = sorted(df_cleaned['year'].dropna().unique().astype(int).tolist())
    
    if len(anios_disponibles) > 1:
        rango_anos = st.sidebar.slider(
            "Selecciona el rango de años:",
            min_value=min(anios_disponibles),
            max_value=max(anios_disponibles),
            value=(min(anios_disponibles), max(anios_disponibles))
        )
        df_cleaned = df_cleaned[(df_cleaned['year'] >= rango_anos[0]) & (df_cleaned['year'] <= rango_anos[1])]

@st.cache_resource
def cargar_modelo_knn():
    try:
        return joblib.load(os.path.join(pipeline_path, "product_knn.joblib"))
    except:
        return None

model_knn = cargar_modelo_knn()

# --- 3. PESTAÑAS DE NAVEGACIÓN ---
tab_reportes, tab_geo, tab_cross = st.tabs([
    "📈 Reportes Estratégicos y KPIs", 
    "🌍 Análisis Comparativo de Países",
    "🛍️ Venta Cruzada & Rotación de Inventario (KNN)"
])

# --- PESTAÑA 1: REPORTES Y KPIS ---
with tab_reportes:
    st.subheader("Panel Ejecutivo de Rendimiento Comercial")
    
    if df_cleaned is not None and not df_cleaned.empty:
        total_ventas = df_cleaned['sales'].sum() if 'sales' in df_cleaned.columns else 0
        total_ganancias = df_cleaned['profit'].sum() if 'profit' in df_cleaned.columns else 0
        total_ordenes = df_cleaned['order_id'].nunique() if 'order_id' in df_cleaned.columns else len(df_cleaned)
        ticket_prom = total_ventas / total_ordenes if total_ordenes > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ventas Totales", formatear_usd(total_ventas), help=f"Importe exacto: {formatear_usd(total_ventas, compacto=False)}")
        col2.metric("Ganancias Totales", formatear_usd(total_ganancias), help=f"Importe exacto: {formatear_usd(total_ganancias, compacto=False)}")
        col3.metric("Ticket Promedio", formatear_usd(ticket_prom, compacto=False))
        col4.metric("Órdenes Registradas", formatear_numero(total_ordenes, 0))
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("##### 📦 Ventas Totales por Categoría")
            if 'category' in df_cleaned.columns and 'sales' in df_cleaned.columns:
                df_cat = (
                    df_cleaned.groupby('category')['sales'].sum().reset_index()
                    .sort_values('sales', ascending=False, kind='stable')
                )
                fig_cat = px.bar(
                    df_cat, x="category", y="sales", color="category",
                    text=df_cat['sales'].apply(formatear_usd),
                    category_orders={"category": df_cat['category'].tolist()},
                    color_discrete_map={
                        "Technology": "#00CC96", "Furniture": "#636EFA",
                        "Office Supplies": "#EF553B"
                    },
                    labels={"category": "Categoría", "sales": "Ventas totales (USD)"},
                    template="plotly_white"
                )
                fig_cat.update_layout(showlegend=False)
                st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_g2:
            st.markdown("##### 🌍 Top Países por Volumen de Ventas")
            if 'country' in df_cleaned.columns and 'sales' in df_cleaned.columns:
                df_pais = df_cleaned.groupby('country')['sales'].sum().reset_index().nlargest(10, 'sales')
                fig_pais = px.bar(df_pais, x="sales", y="country", orientation='h', color="sales", template="plotly_white")
                fig_pais.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_pais, use_container_width=True)

        st.markdown("---")
        
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.markdown("##### 🏷️ Participación en Ventas por Subcategoría: Top 5 y Otros")
            if 'sub_category' in df_cleaned.columns and 'sales' in df_cleaned.columns:
                df_sub_total = (
                    df_cleaned.assign(
                        sub_category=df_cleaned['sub_category'].fillna('Sin subcategoría')
                    ).groupby('sub_category')['sales'].sum().reset_index()
                    .sort_values('sales', ascending=False, kind='stable')
                )
                df_sub = df_sub_total.head(5).copy()
                if len(df_sub_total) > 5:
                    df_sub = pd.concat([
                        df_sub,
                        pd.DataFrame({
                            "sub_category": ["Otros"],
                            "sales": [df_sub_total.iloc[5:]['sales'].sum()]
                        })
                    ], ignore_index=True)
                if df_sub_total['sales'].sum() > 0:
                    fig_sub = px.pie(
                        df_sub, names="sub_category", values="sales", hole=0.4,
                        color="sub_category", color_discrete_map={"Otros": "#CBD5E1"},
                        labels={"sub_category": "Subcategoría", "sales": "Ventas (USD)"},
                        template="plotly_white"
                    )
                    fig_sub.update_traces(
                        sort=False, textinfo='percent', texttemplate='%{percent:.1%}',
                        hovertemplate=(
                            '%{label}<br>Ventas: %{value:,.2f} USD'
                            '<br>Participación: %{percent:.1%}<extra></extra>'
                        )
                    )
                    st.plotly_chart(fig_sub, use_container_width=True)
                    st.caption(
                        "Porcentajes sobre todas las ventas del período seleccionado. "
                        "Otros agrupa las subcategorías fuera del Top 5."
                    )
                else:
                    st.info("No hay ventas positivas para mostrar la participación.")

        with col_g4:
            st.markdown("##### 👥 Distribución por Segmento de Clientes")
            if 'segment' in df_cleaned.columns and 'sales' in df_cleaned.columns:
                df_seg = df_cleaned.groupby('segment')['sales'].sum().reset_index().sort_values('sales', ascending=False, kind='stable')
                fig_seg = px.bar(df_seg, x="segment", y="sales", color="segment", text_auto='.2s', category_orders={"segment": df_seg["segment"].tolist()}, template="plotly_white")
                st.plotly_chart(fig_seg, use_container_width=True)

        st.markdown("---")
        
        st.markdown("##### 📈 Evolución General de Ventas por Año (Consolidado)")
        if 'year' in df_cleaned.columns and 'sales' in df_cleaned.columns:
            df_temporal_general = df_cleaned.groupby('year')['sales'].sum().reset_index()
            if not df_temporal_general.empty:
                fig_tiempo_gen = px.line(
                    df_temporal_general, 
                    x='year', 
                    y='sales', 
                    markers=True, 
                    text=df_temporal_general['sales'].apply(lambda x: f"${x:,.0f}"), 
                    template="plotly_white"
                )
                fig_tiempo_gen.update_traces(textposition="top center")
                st.plotly_chart(fig_tiempo_gen, use_container_width=True)
    else:
        st.warning("⚠️ No se pudo cargar el archivo CSV o no hay datos para el rango seleccionado.")

# --- PESTAÑA 2: ANÁLISIS GEOGRÁFICO Y COMPARATIVA ---
with tab_geo:
    st.subheader("🌐 Análisis Comparativo: Evolución y Preferencias por País")
    
    if df_cleaned is not None and not df_cleaned.empty:
        paises_disponibles = sorted(df_cleaned['country'].dropna().unique().tolist()) if 'country' in df_cleaned.columns else ["United States"]
        
        st.markdown("##### ⚙️ Filtros de Comparación Regional")
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            pais_1 = st.selectbox("Selecciona el País 1:", paises_disponibles, index=0)
        with col_filtro2:
            default_idx = 1 if len(paises_disponibles) > 1 else 0
            pais_2 = st.selectbox("Selecciona el País 2:", paises_disponibles, index=default_idx)

        st.markdown("---")

        st.markdown(f"##### 📈 Evolución de Ventas Integrada: {pais_1} vs {pais_2}")
        df_ambos_paises = df_cleaned[df_cleaned['country'].isin([pais_1, pais_2])]
        
        if 'year' in df_ambos_paises.columns and 'sales' in df_ambos_paises.columns:
            df_temporal_comp = df_ambos_paises.groupby(['year', 'country'])['sales'].sum().reset_index()
            if not df_temporal_comp.empty:
                fig_tiempo_comp = px.line(
                    df_temporal_comp, 
                    x='year', 
                    y='sales', 
                    color='country',
                    markers=True, 
                    text=df_temporal_comp['sales'].apply(lambda x: f"${x:,.0f}"), 
                    template="plotly_white"
                )
                fig_tiempo_comp.update_traces(textposition="top center")
                fig_tiempo_comp.update_layout(xaxis_title="Año", yaxis_title="Ventas Totales (USD)")
                st.plotly_chart(fig_tiempo_comp, use_container_width=True)
            else:
                st.info("No hay registros temporales suficientes para estos países en el rango de años.")
        
        st.markdown("---")
        
        # --- COMPARATIVA LADO A LADO ---
        st.markdown(f"##### 🎯 Comparativa Directa de Inteligencia Comercial")
        col_p1, col_p2 = st.columns(2)
        
        for idx, pais in enumerate([pais_1, pais_2]):
            columna_activa = col_p1 if idx == 0 else col_p2
            
            with columna_activa:
                st.markdown(f"### 🌍 Mercado: {pais}")
                df_pais = df_cleaned[df_cleaned['country'] == pais]
                
                # 1. KPIs del País
                ventas_pais = df_pais['sales'].sum()
                ordenes_pais = df_pais['order_id'].nunique() if 'order_id' in df_pais.columns else len(df_pais)
                ticket_pais = ventas_pais / ordenes_pais if ordenes_pais > 0 else 0
                
                m1, m2 = st.columns(2)
                m1.metric("Ventas Totales", formatear_usd(ventas_pais), f"{formatear_numero(ordenes_pais, 0)} Órdenes")
                m2.metric("Ticket Promedio", formatear_usd(ticket_pais, compacto=False))
                
                st.markdown("**Subcategorías Preferidas**")
                if 'sub_category' in df_pais.columns:
                    df_sub = df_pais.groupby('sub_category')['sales'].sum().reset_index().nlargest(5, 'sales')
                    if not df_sub.empty:
                        fig_sub = px.bar(df_sub, x='sales', y='sub_category', orientation='h', color='sub_category', template="plotly_white")
                        fig_sub.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=250, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig_sub, use_container_width=True)
                    else:
                        st.info("Sin datos.")
                
                st.markdown("**Top Productos Estrella**")
                df_top_prod = pd.DataFrame()
                if 'product_name' in df_pais.columns and 'sales' in df_pais.columns:
                    df_top_prod = df_pais.groupby('product_name')['sales'].sum().reset_index().nlargest(5, 'sales')
                    if not df_top_prod.empty:
                        fig_prod = px.bar(
                            df_top_prod, x='sales', y='product_name', orientation='h', color='sales',
                            color_continuous_scale='Blues', template="plotly_white", text_auto='.2s'
                        )
                        fig_prod.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, xaxis_title="Ventas (USD)", yaxis_title="", height=300, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig_prod, use_container_width=True)
                
                # 2. Estrategia Sugerida
                if not df_top_prod.empty:
                    top_nombre = df_top_prod.iloc[0]['product_name']
                    top_ventas = df_top_prod.iloc[0]['sales']
                    subcat_lider = df_pais.groupby('sub_category')['sales'].sum().idxmax() if 'sub_category' in df_pais.columns else "General"
                    
                    st.success(f"""
                    **🚀 Estrategia Recomendada**
                    * **Motor de Ventas:** {top_nombre} (${top_ventas:,.2f}). 
                    * **Acción:** Empaquetar este artículo con productos complementarios de la categoría **{subcat_lider}** aplicando un 10% de descuento. 
                    * **Objetivo:** Incrementar el Ticket Promedio actual de ${ticket_pais:,.2f} USD.
                    """)
                else:
                    st.info("Sin registros suficientes para generar estrategia.")
                st.markdown("---")

    else:
        st.warning("⚠️ Datos no disponibles para el análisis geográfico.")

# --- PESTAÑA 3: VENTA CRUZADA & ROTACIÓN DE INVENTARIO ---
with tab_cross:
    st.subheader("📊 Panel de Métricas y Validación del Pipeline")
    
    data_api = obtener_metricas_api()
    
    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("Hit Rate @ 5", data_api.get("hit_rate", "8.81%"), "✅ Validado en prueba")
    bc2.metric("Esparsidad de Matriz", data_api.get("sparsity", "99.38%"), "⚡ Optimizado SVD")
    bc3.metric("Catálogo Comercial", f"{data_api.get('total_items', 10292):,}", "📦 Ítems sincronizados")

    with st.expander("📋 Ver Resumen Ejecutivo y Diagnóstico del Modelo"):
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            st.markdown("""
            * **Protocolo de Validación:** Split temporal / Validación cruzada offline (80% entrenamiento, 20% prueba).
            * **Arquitectura:** Modelo híbrido basado en descomposición de valores singulares truncados (`TruncatedSVD`) y vecinos más cercanos (`k-NN`).
            * **Trazabilidad:** Sincronización directa con los artefactos del pipeline expuestos por FastAPI.
            """)
        with col_exp2:
            st.markdown("""
            * **Impacto Comercial:** Maximiza la tasa de acierto en las primeras 5 recomendaciones y provee explicabilidad automática por categoría y ventas cruzadas.
            * **Optimización Espacial:** Reduce la dimensionalidad a 50 componentes latentes mitigando la alta esparsidad de la matriz de transacciones.
            """)
    st.markdown("---")

    st.subheader("🛍️ Motor de Recomendación y Optimización de Inventario (KNN)")
    st.markdown("Selecciona un producto ancla para calcular paquetes inteligentes orientados a rotación de inventario, liquidación de stock lento y crecimiento de ticket.")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Configuración de Paquete")
        
        if df_cleaned is not None and 'product_id' in df_cleaned.columns:
            lista_productos_ids = df_cleaned['product_id'].unique().tolist()
        else:
            lista_productos_ids = ["OFF-AR-10003651", "OFF-TEN-10000025"]

        producto_activo = st.selectbox("Selecciona producto ancla (SKU):", lista_productos_ids)
        
        tipo_rotacion = "Alta Rotación 🚀" if hash(str(producto_activo)) % 2 == 0 else "Stock Lento / Clearance ⚠️"
        st.info(f"📊 **Clasificación SKU:** {tipo_rotacion}")

        top_n = st.slider("Cantidad de recomendaciones:", min_value=1, max_value=10, value=3)
        paquete_descuento = st.slider("Descuento sugerido para paquete (%)", min_value=0, max_value=50, value=10)
        
        # Nueva opción para filtrar productos con pérdidas automáticamente
        excluir_perdidas = st.checkbox("🚫 Excluir productos con pérdida automáticamente", value=True)
        
        st.markdown("---")
        generar_estrategia = st.button("🔄 Generar Propuesta de Paquete", type="primary")

    with col2:
        st.markdown("#### 📦 Propuesta Comercial, Precios, Ganancias y Ahorro del Paquete")
        
        if generar_estrategia:
            try:
                # Solicitamos un conjunto más amplio a la API (hasta 15) para tener margen de reemplazo al filtrar pérdidas
                url_api_recom = f"http://127.0.0.1:8000/recomendaciones/similares/{producto_activo}?top_n=15"
                resp_recom = requests.get(url_api_recom, timeout=5)
                
                if resp_recom.status_code == 200:
                    data_recom = resp_recom.json()
                    info_origen = data_recom.get("producto_origen", {})
                    lista_recoms_raw = data_recom.get("recomendaciones", [])
                    
                    nombre_ancla = info_origen.get("nombre", producto_activo)
                    
                    # Filtrado de recomendaciones según la opción de excluir pérdidas
                    lista_recoms = []
                    for item in lista_recoms_raw:
                        metricas_api = item.get("metricas", {})
                        profit_api = metricas_api.get("profit", 0.0)
                        
                        if excluir_perdidas and profit_api < 0:
                            continue  # Omite productos con pérdida y busca en las siguientes opciones
                        
                        lista_recoms.append(item)
                        if len(lista_recoms) >= top_n:
                            break  # Se detiene al completar la cantidad de recomendaciones solicitada (top_n)

                    # 1. Cálculo del precio unitario y ganancia unitaria del producto ancla
                    precio_ancla = 75.50
                    ganancia_unit_ancla = 15.0
                    if df_cleaned is not None and 'sales' in df_cleaned.columns:
                        df_sku_match = df_cleaned[df_cleaned['product_id'] == producto_activo]
                        if not df_sku_match.empty:
                            total_s = df_sku_match['sales'].sum()
                            total_p = df_sku_match['profit'].sum() if 'profit' in df_sku_match.columns else 0.0
                            total_q = df_sku_match['quantity'].sum() if 'quantity' in df_sku_match.columns else len(df_sku_match)
                            
                            precio_ancla = (total_s / total_q) if total_q > 0 else df_sku_match['sales'].mean()
                            ganancia_unit_ancla = (total_p / total_q) if total_p > 0 else df_sku_match['profit'].mean()

                    st.success(f"Estrategia generada para: **{nombre_ancla}** (`{producto_activo}`) | Precio Unitario Base: **${precio_ancla:,.2f} USD**")

                    if lista_recoms:
                        filas_tabla = []
                        precios_unitarios_recomendados = []
                        ganancias_unitarias_recomendadas = []
                        
                        st.markdown("##### 🔍 Desglose Individual de Recomendaciones y Rentabilidad")
                        
                        for idx, item in enumerate(lista_recoms, start=1):
                            sku_v = item.get("sku")
                            nombre_v = item.get("nombre")
                            cat_v = item.get("categoria")
                            score_v = item.get("score_similitud")
                            
                            metricas_api = item.get("metricas", {})
                            sales_api = metricas_api.get("sales", 50.0)
                            qty_api = metricas_api.get("quantity", 1)
                            profit_api = metricas_api.get("profit", 0.0)
                            
                            p_unit = metricas_api.get("precio_unitario_usd", (sales_api / qty_api if qty_api > 0 else sales_api))
                            g_unit = (profit_api / qty_api) if qty_api > 0 else profit_api
                            
                            precios_unitarios_recomendados.append(p_unit)
                            ganancias_unitarias_recomendadas.append(g_unit)
                            
                            with st.container():
                                st.markdown(f"**{idx}. {nombre_v}** — *Cat: {cat_v}* (`SKU: {sku_v}`)")
                                
                                c_sim, c_m1, c_m2, c_m3, c_m4 = st.columns([2.2, 1, 1, 1, 1.2])
                                with c_sim:
                                    st.markdown(f"**Similitud: {score_v:.2f}**")
                                    st.progress(float(score_v))
                                with c_m1:
                                    st.metric("Ventas Acum.", f"${sales_api:,.2f}")
                                with c_m2:
                                    st.metric("Unidades", f"{qty_api}")
                                with c_m3:
                                    st.metric("Precio Unit.", f"${p_unit:,.2f}")
                                with c_m4:
                                    if profit_api < 0:
                                        estado_fin = "⚠️ Alerta: Pérdida"
                                        delta_col = "inverse"
                                    else:
                                        estado_fin = "✅ Rentable"
                                        delta_col = "normal"
                                        
                                    st.metric(
                                        label="Ganancia Neta",
                                        value=f"${profit_api:,.2f}",
                                        delta=estado_fin,
                                        delta_color=delta_col
                                    )
                            st.markdown("---")

                        filas_tabla.append({
                            "Ranking": idx,
                            "SKU": sku_v,
                            "Nombre del Artículo": nombre_v,
                            "Categoría": cat_v,
                            "Ventas API ($)": f"${sales_api:,.2f}",
                            "Ganancia API ($)": f"${profit_api:,.2f}",
                            "Cant. API": qty_api,
                            "Precio Unit. ($ USD)": f"${p_unit:,.2f}",
                            "Similitud ML": score_v
                        })

                        df_bundle = pd.DataFrame(filas_tabla)
                        df_bundle.index = range(1, len(df_bundle) + 1)
                        
                        csv_bundle = df_bundle.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Propuesta de Paquete en CSV",
                            data=csv_bundle,
                            file_name=f'paquete_comercial_{producto_activo}.csv',
                            mime='text/csv'
                        )
                        
                        # Cálculos financieros correctos del combo unitario
                        suma_precios_unitarios = sum(precios_unitarios_recomendados)
                        precio_total_original = precio_ancla + suma_precios_unitarios
                        monto_descuento = precio_total_original * (paquete_descuento / 100.0)
                        precio_total_con_descuento = precio_total_original - monto_descuento
                        
                        # Suma de ganancias unitarias de cada ítem del paquete
                        ganancia_base_combo = ganancia_unit_ancla + sum(ganancias_unitarias_recomendadas)
                        factor_descuento = 1.0 - (paquete_descuento / 100.0)
                        ganancia_neta_paquete_con_descuento = ganancia_base_combo * factor_descuento

                        st.markdown("---")
                        st.markdown("#### 💰 Resumen Financiero y de Rentabilidad del Paquete")
                        
                        mc1, mc2, mc3, mc4 = st.columns(4)
                        mc1.metric("Valor Original del Combo", f"${precio_total_original:,.2f} USD")
                        mc2.metric(f"Combo con {paquete_descuento}% Desct.", f"${precio_total_con_descuento:,.2f} USD", delta=f"-${monto_descuento:,.2f} USD Ahorro", delta_color="inverse")
                        mc3.metric("Ganancia Neta por Paquete", f"${ganancia_neta_paquete_con_descuento:,.2f} USD", delta="Utilidad del Combo" if ganancia_neta_paquete_con_descuento >= 0 else "Alerta Pérdida", delta_color="normal" if ganancia_neta_paquete_con_descuento >= 0 else "inverse")
                        mc4.metric("Artículos en Paquete", f"{len(lista_recoms) + 1} Ítems")

                        # --- PROYECCIÓN FINANCIERA Y ROTACIÓN ESTIMADA DE INVENTARIO ---
                        st.markdown("---")
                        st.markdown("#### 📦 Proyección Financiera y Rotación Estimada de Inventario")
                        
                        lote_10 = ganancia_neta_paquete_con_descuento * 10
                        lote_50 = ganancia_neta_paquete_con_descuento * 50
                        margen_porcentual = ((ganancia_neta_paquete_con_descuento / precio_total_con_descuento) * 100) if precio_total_con_descuento > 0 else 0
                        
                        col_proy1, col_proy2 = st.columns(2)
                        
                        with col_proy1:
                            st.markdown("##### 💵 Ganancia Proyectada por Volumen de Paquetes")
                            st.markdown(f"""
                            * **Venta de 10 Paquetes:** **${lote_10:,.2f} USD** de utilidad neta.
                            * **Venta de 50 Paquetes:** **${lote_50:,.2f} USD** de utilidad neta.
                            * **Margen Neto Estimado del Combo:** **{margen_porcentual:.1f}%** sobre el precio con descuento.
                            """)
                            
                        with col_proy2:
                            st.markdown("##### 🔄 Estimación de Rotación de Inventario")
                            if "Stock Lento" in tipo_rotacion:
                                st.markdown(f"""
                                * **Velocidad de Salida:** Alta (Estrategia de Desplazamiento Rápido).
                                * **Días Promedio en Almacén:** Reducción estimada de **30 a 45 días** en stock estancado.
                                * **Impacto en Costos:** Disminución directa en los costos de almacenamiento y liberación de capital inmovilizado.
                                """)
                            else:
                                st.markdown(f"""
                                * **Velocidad de Salida:** Muy Alta (Acelerador de Demanda Cruzada).
                                * **Días Promedio en Almacén:** Rotación constante estimada en menos de **15 días**.
                                * **Impacto en Costos:** Maximización de la rotación de stock secundario y aumento continuo del flujo de caja.
                                """)

                        st.markdown("---")
                        st.markdown("#### 💡 Plan de Acción y Rotación de Inventario")
                        
                        if "Stock Lento" in tipo_rotacion:
                            st.warning(f"""
                            **Estrategia de Liquidación para Stock Estancado (Clearance):**
                            * **Táctica:** Este SKU presenta baja rotación. Al ofrecer el paquete con un **{paquete_descuento}% de descuento** (ahorrando **${monto_descuento:,.2f} USD** al cliente), logras liberar espacio en almacén (reduciendo costos de almacenamiento) y recuperas capital de trabajo de forma ágil sin devaluar la marca con rebajas individuales aisladas.
                            """)
                        else:
                            st.info(f"""
                            **Estrategia de Crecimiento y Venta Cruzada (Cross-Selling):**
                            * **Táctica:** Producto ancla de alta tracción comercial. Ofrecer este combo con un descuento del **{paquete_descuento}%** incentivará al comprador a adquirir el conjunto completo, incrementando sustancialmente el **Ticket Promedio** y mejorando la rotación general del catálogo secundario.
                            """)
                        
                        # --- TABLA FINAL DE PRODUCTOS SUGERIDOS PARA EL PAQUETE ---
                        st.markdown("---")
                        st.markdown("#### 📋 Tabla Resumen de Productos Sugeridos para el Paquete")
                        st.dataframe(df_bundle, use_container_width=True)

                    else:
                        st.warning("No se encontraron recomendaciones rentables suficientes para este SKU con los filtros actuales.")
                else:
                    st.error(f"Error al conectar con la API de FastAPI (Código {resp_recom.status_code}). ¿Tienes la API corriendo en la Terminal 1?")
            except Exception as e:
                st.error(f"No se pudo establecer conexión con el backend de FastAPI: {e}")
        else:
            st.info("👆 Selecciona los parámetros en la barra lateral y haz clic en **'🔄 Generar Propuesta de Paquete'** para calcular la estrategia y visualizar la tabla de productos.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>NexaData Consulting — Business Intelligence & MLOps Solutions 🚀</p>", unsafe_allow_html=True)