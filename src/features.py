import pandas as pd
import numpy as np

def calcular_variables_agregadas(df_transacciones):
    # Normalizar nombres de columnas a minúsculas y reemplazar espacios por guiones bajos
    df_transacciones.columns = df_transacciones.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Compatibilidad con identificadores de producto
    if 'product_id' in df_transacciones.columns and 'product_code' not in df_transacciones.columns:
        df_transacciones['product_code'] = df_transacciones['product_id']

    # Forzar conversión de columnas numéricas clave por si tienen texto o formato con comas
    for col in ['sales', 'quantity', 'profit', 'discount']:
        if col in df_transacciones.columns:
            df_transacciones[col] = pd.to_numeric(df_transacciones[col].astype(str).str.replace(',', '.'), errors='coerce')

    # 1. Extracción de características temporales a partir de order_date
    if 'order_date' in df_transacciones.columns:
        df_transacciones['order_date'] = pd.to_datetime(df_transacciones['order_date'], errors='coerce')
        df_transacciones['order_year'] = df_transacciones['order_date'].dt.year
        df_transacciones['order_month'] = df_transacciones['order_date'].dt.month
        df_transacciones['order_dayofweek'] = df_transacciones['order_date'].dt.dayofweek

    # 2. Métricas de comportamiento y RFM por cliente
    fecha_ref = df_transacciones['order_date'].max() + pd.Timedelta(days=1) if 'order_date' in df_transacciones.columns and df_transacciones['order_date'].notna().any() else pd.Timestamp.today()
    
    agg_dict_cliente = {}
    if 'order_date' in df_transacciones.columns:
        agg_dict_cliente['recencia'] = ('order_date', lambda x: (fecha_ref - x.max()).days if pd.notna(x.max()) else 0)
    if 'order_id' in df_transacciones.columns:
        agg_dict_cliente['frecuencia_compra'] = ('order_id', 'count')
    elif 'sales' in df_transacciones.columns:
        agg_dict_cliente['frecuencia_compra'] = ('sales', 'count')
    if 'product_code' in df_transacciones.columns:
        agg_dict_cliente['productos_distintos'] = ('product_code', 'nunique')
    if 'quantity' in df_transacciones.columns:
        agg_dict_cliente['unidades_totales'] = ('quantity', 'sum')
    if 'sales' in df_transacciones.columns:
        agg_dict_cliente['gasto_total'] = ('sales', 'sum')
        agg_dict_cliente['ticket_promedio'] = ('sales', 'mean')

    features_cliente = df_transacciones.groupby('customer_name').agg(**agg_dict_cliente).reset_index()

    # 3. Métricas de rendimiento y popularidad por producto
    prod_col = 'product_code' if 'product_code' in df_transacciones.columns else df_transacciones.columns[0]
    
    agg_dict_prod = {}
    if 'sales' in df_transacciones.columns:
        agg_dict_prod['popularidad_global'] = ('sales', 'count')
        agg_dict_prod['ventas_acumuladas'] = ('sales', 'sum')
    if 'customer_name' in df_transacciones.columns:
        agg_dict_prod['clientes_distintos'] = ('customer_name', 'nunique')
    if 'quantity' in df_transacciones.columns:
        agg_dict_prod['unidades_acumuladas'] = ('quantity', 'sum')

    features_producto = df_transacciones.groupby(prod_col).agg(**agg_dict_prod).reset_index()

    return features_cliente, features_producto