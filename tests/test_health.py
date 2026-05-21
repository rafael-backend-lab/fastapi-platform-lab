import os
import sys

# Garante que o pytest enxergue o main.py na raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert data.get("ok") is True
    assert "FastAPI Platform Lab" in data.get("msg", "")


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert data.get("status") == "ok"


def test_dbstatus_structure():
    """
    Esse teste NÃO exige que o banco esteja “ok”.
    Ele só garante que a rota responda com JSON no formato esperado.

    Se o banco estiver fora do ar, a própria rota retorna:
        {"db": "error", "detail": "..."}
    e o teste continua passando.
    """
    response = client.get("/dbstatus")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "db" in data
    assert data["db"] in ("ok", "error")