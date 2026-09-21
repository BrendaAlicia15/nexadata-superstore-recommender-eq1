# Entrenamiento reproducible de recomendaciones por similitud de productos

from pathlib import Path

import joblib
from scipy.sparse import load_npz
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors


def train_model(
    output_dir: Path,
    components: int = 50,
    neighbors: int = 10,
    seed: int = 42,
) -> dict:
    # Ajustar SVD sobre clientes × productos y vecinos sobre productos
    interactions = load_npz(output_dir / "customer_product_quantity.npz")
    max_components = min(interactions.shape) - 1

    if not 1 <= components <= max_components:
        raise ValueError(f"components debe estar entre 1 y {max_components}")
    if not 1 <= neighbors < interactions.shape[1]:
        raise ValueError("neighbors debe ser menor que la cantidad de productos")

    svd = TruncatedSVD(n_components=components, random_state=seed)
    svd.fit(interactions)

    product_vectors = svd.components_.T.copy()
    if product_vectors.shape != (interactions.shape[1], components):
        raise RuntimeError("La matriz latente no coincide con el catálogo")

    knn = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_neighbors=neighbors + 1,
    )
    knn.fit(product_vectors)

    joblib.dump(svd, output_dir / "svd_model.joblib")
    joblib.dump(knn, output_dir / "product_knn.joblib")
    joblib.dump(product_vectors, output_dir / "product_vectors.joblib")

    return {
        "components": components,
        "neighbors": neighbors,
        "seed": seed,
        "product_vector_shape": list(product_vectors.shape),
        "explained_variance_ratio": float(svd.explained_variance_ratio_.sum()),
    }