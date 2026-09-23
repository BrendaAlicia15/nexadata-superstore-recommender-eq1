from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()

def test_recomendacion_producto_valido():
    sku_prueba = "OFF-AR-10003651"
    response = client.get(f"/recomendaciones/similares/{sku_prueba}?top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert "recomendaciones" in data
    assert len(data["recomendaciones"]) == 3

def test_recomendacion_producto_flexible():
    response = client.get("/recomendaciones/similares/PRODUCTO-FALSO-99999?top_n=2")
    assert response.status_code == 200
    data = response.json()
    assert "recomendaciones" in data
    assert len(data["recomendaciones"]) == 2