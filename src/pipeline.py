# Lee el csv original, ejecuta la limpieza y genera matriz (datos crudos -> interacciones y catálogo ordenado)
# Para ejecutar desde cualquier directorio con ``python -m src.pipeline``


from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from scipy.sparse import csr_matrix, save_npz

from src.preprocessing import clean_superstore_data
from src.train import train_model

import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_ROOT / "data" / "raw" / "SuperStoreOrders - SuperStoreOrders.csv"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "pipeline"

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_revision() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def build_interactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Sumar unidades compradas por cliente y producto, en orden estable."""
    required = {"customer_name", "product_id", "quantity"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError(f"Faltan columnas para la matriz: {sorted(missing)}")

    rows = transactions.dropna(subset=["customer_name", "product_id", "quantity"])
    if rows.empty:
        raise ValueError("No hay interacciones válidas después de la limpieza")
    matrix = rows.pivot_table(
        index="customer_name",
        columns="product_id",
        values="quantity",
        aggfunc="sum",
        fill_value=0,
        sort=True,
    )
    if matrix.empty or (matrix.to_numpy() < 0).any():
        raise ValueError("La matriz está vacía o contiene cantidades negativas")
    return matrix


def run(raw_data: Path = RAW_DATA, output_dir: Path = OUTPUT_DIR) -> dict:
    """Generar artefactos desde el CSV crudo, sin depender de notebooks."""
    if not raw_data.is_file():
        raise FileNotFoundError(f"No existe el CSV original: {raw_data}")
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned = clean_superstore_data(
        str(raw_data), str(output_dir / "superstore_cleaned.csv")
    )
    matrix = build_interactions(cleaned)
    customer_ids = matrix.index.astype(str).tolist()
    product_ids = matrix.columns.astype(str).tolist()

    save_npz(output_dir / "customer_product_quantity.npz", csr_matrix(matrix.to_numpy()))
    (output_dir / "customer_ids.json").write_text(
        json.dumps(customer_ids, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "product_ids.json").write_text(
        json.dumps(product_ids, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = {
        "transactions_cleaned": len(cleaned),
        "customers": len(customer_ids),
        "products": len(product_ids),
        "total_units": int(matrix.to_numpy().sum()),
        "matrix_shape": list(matrix.shape),
    }
    summary["training"] = train_model(output_dir)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = output_dir / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)

    artifact_names = [
        "superstore_cleaned.csv",
        "customer_product_quantity.npz",
        "customer_ids.json",
        "product_ids.json",
        "svd_model.joblib",
        "product_knn.joblib",
        "product_vectors.joblib",
        "summary.json",
    ]

    run_record = {
        "run_id": run_id,
        "git_commit": git_revision(),
        "input_sha256": sha256_file(raw_data),
        "python_version": platform.python_version(),
        "dependencies": {
            package: version(package)
            for package in ("pandas", "scipy", "scikit-learn", "joblib")
        },
        "summary": summary,
        "artifacts_sha256": {
            name: sha256_file(output_dir / name) for name in artifact_names
        },
    }
    (run_dir / f"{run_id}.json").write_text(
        json.dumps(run_record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-data", type=Path, default=RAW_DATA)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    print(json.dumps(run(args.raw_data, args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
