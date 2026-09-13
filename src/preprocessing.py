#Paso 1: Crear el script de limpieza y trazabilidad (src/preprocessing.py)
#Crea o actualiza el archivo src/preprocessing.py con el siguiente código. Este script está diseñado para leer el archivo crudo, limpiar las anomalías monetarias, eliminar duplicados, tratar nulos y devolver métricas exactas del impacto de la limpieza:

from pathlib import Path
import pandas as pd


def clean_superstore_data(input_filepath: str, output_filepath: str = None):
  """Ejecuta el pipeline de limpieza y tratamiento riguroso de datos,

  cuantificando la retención y garantizando la trazabilidad.
  """
  print('--- INICIANDO PIPELINE DE PREPROCESAMIENTO ---')

  # Carga de datos crudos
  df = pd.read_csv(input_filepath)
  initial_rows = len(df)
  print(f'Registros iniciales en crudo: {initial_rows:,}')

  # 1. Tratamiento de duplicados transaccionales exactos
  duplicates_count = df.duplicated().sum()
  df = df.drop_duplicates()
  print(f'Duplicados exactos eliminados: {duplicates_count:,}')

  # 2. Limpieza y conversión rigurosa de variables monetarias y numéricas
  # Limpieza de 'sales'
  if 'sales' in df.columns:
    df['sales'] = (
        df['sales']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
    )
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')

  # Limpieza de otras métricas si aplican (ej. profit, quantity)
  for col in ['profit', 'quantity']:
    if col in df.columns and df[col].dtype == 'object':
      df[col] = (
          df[col]
          .astype(str)
          .str.replace('$', '', regex=False)
          .str.replace(',', '', regex=False)
          .str.strip()
      )
      df[col] = pd.to_numeric(df[col], errors='coerce')

  # 3. Tratamiento de valores nulos
  nulls_before = df.isnull().sum().sum()
  # Imputación o eliminación estratégica (ej. si sales es nulo, eliminamos la fila por integridad financiera)
  df = df.dropna(subset=['sales', 'product_id', 'customer_name'])
  nulls_after = df.isnull().sum().sum()
  print(
      f'Valores nulos tratados/eliminados en columnas clave: {nulls_before - nulls_after}'
  )

  # 4. Cálculo de métricas de retención (Trazabilidad)
  final_rows = len(df)
  retention_percentage = (final_rows / initial_rows) * 100

  print('--- MÉTRICAS DE TRAZABILIDAD Y CALIDAD ---')
  print(f'Registros finales procesados: {final_rows:,}')
  print(f'Porcentaje de retención del dataset: {retention_percentage:.2f}%')

  # Guardar dataset procesado si se especifica ruta
  if output_filepath:
    output_path = Path(output_filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f'Dataset limpio guardado exitosamente en: {output_path}')

  return df


if __name__ == '__main__':
  # Ejecución de prueba local
  raw_path = 'data/raw/SuperStoreOrders - SuperStoreOrders.csv'
  processed_path = 'data/processed/superstore_cleaned.csv'
  clean_superstore_data(raw_path, processed_path)

