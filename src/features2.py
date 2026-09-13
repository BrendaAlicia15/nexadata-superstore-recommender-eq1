#Paso 2: Crear el script de ingeniería de características (src/features.py)
#Crea el archivo src/features.py. Este script transforma el historial de transacciones en variables analíticas que capturan el comportamiento real del cliente y la afinidad de productos:

from pathlib import Path
import numpy as np
import pandas as pd


def generate_user_item_features(processed_filepath: str):
  """Genera características de comportamiento de usuarios y productos

  para alimentar los modelos de recomendación.
  """
  print('--- GENERANDO INGENIERÍA DE CARACTERÍSTICAS ---')
  df = pd.read_csv(processed_filepath)

  # Asegurar formato de fecha si existe la columna de fecha de orden
  date_col = next(
      (
          col
          for col in df.columns
          if 'date' in col.lower() or 'fecha' in col.lower()
      ),
      None,
  )
  if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    max_date = df[date_col].max()
  else:
    max_date = pd.Timestamp('2026-01-01')  # Referencia por defecto

  # 1. Features a nivel de Usuario (Customer Behavior)
  # Recencia (días desde su última compra), Frecuencia (total de órdenes) y Ticket Promedio (Monetary / AOV)
  if date_col:
    customer_recency = (
        df.groupby('customer_name')[date_col]
        .apply(lambda x: (max_date - x.max()).days)
        .rename('recency_days')
    )
  else:
    customer_recency = pd.Series(0, index=df['customer_name'].unique(), name='recency_days')

  customer_metrics = df.groupby('customer_name').agg(
      frequency_orders=('order_id', 'nunique'),
      total_spent=('sales', 'sum'),
      avg_ticket=('sales', 'mean'),
  )

  customer_features = pd.concat([customer_metrics, customer_recency], axis=1)
  print(f'Matriz de características de usuarios generada: {customer_features.shape}')

  # 2. Features a nivel de Producto (Product Afinity / Popularity)
  product_features = df.groupby('product_id').agg(
      times_purchased=('order_id', 'count'),
      total_revenue_prod=('sales', 'sum'),
      avg_sale_price=('sales', 'mean'),
  )
  print(f'Matriz de características de productos generada: {product_features.shape}')

  return customer_features, product_features


if __name__ == '__main__':
  processed_path = 'data/processed/superstore_cleaned.csv'
  cust_feat, prod_feat = generate_user_item_features(processed_path)
  print(cust_feat.head())
  print(prod_feat.head())
