from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
  response = client.get(
      "/health"
  )  # Ajusta según tu ruta de verificación de estado
  assert response.status_code in [200, 404]


def test_recomendacion_producto_valido():
  # Usa un ID real válido de tu catálogo
  response = client.get("/recomendaciones/similares/OFF-AR-10003658?top_n=3")
  assert response.status_code == 200
  data = response.json()
  assert "recomendaciones" in data
  assert len(data["recomendaciones"]) == 3


def test_recomendacion_producto_no_existente():
  response = client.get("/recomendaciones/similares/PRODUCTO-FALSO-999")
  assert response.status_code == 404
  assert "no se encuentra registrado" in response.json()["detail"]