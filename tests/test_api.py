import os
import sys

# making sure project root is on sys.path so we can import main, database, models
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
import pytest

from main import app
from database import Base, engine


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """
    Drop and recreate all tables before each test so we start with a clean DB.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def get_sample_payload(vin: str = "abc123"):
    return {
        "vin": vin,
        "manuName": "Toyota",
        "description": "Test car",
        "horsePower": 150,
        "modelName": "Corolla",
        "modelYear": 2020,
        "purchasePrice": 20000,
        "fuelType": "Gasoline",
    }


def test_create_vehicle_success():
    payload = get_sample_payload("abc123")

    res = client.post("/vehicle", json=payload)
    assert res.status_code == 201

    data = res.json()
    assert data["vin"] == "ABC123"
    assert data["manuName"] == "Toyota"
    assert "id" in data


def test_create_vehicle_duplicate_vin_returns_422():
    '''
    Expected output: success, fail
    '''

    payload = get_sample_payload("dupvin")

    res1 = client.post("/vehicle", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/vehicle", json=payload)
    assert res2.status_code == 422

    data = res2.json()
    assert "vin" in str(data).lower()


def test_get_vehicle_by_vin():
    payload = get_sample_payload("get123")

    # POST: 201 OK
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    # GET: 200 OK
    res_get = client.get("/vehicle/get123")
    assert res_get.status_code == 200

    data = res_get.json()
    assert data["vin"] == "GET123"
    assert data["manuName"] == "Toyota"


def test_list_vehicles():
    res_empty = client.get("/vehicle")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    client.post("/vehicle", json=get_sample_payload("list1"))

    res_list = client.get("/vehicle")
    assert res_list.status_code == 200

    data = res_list.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["vin"] == "LIST1"


def test_update_vehicle():
    payload = get_sample_payload("upd123")
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    updated_payload = {
        "vin": "upd123",
        "manuName": "Toyota",
        "description": "Updated description",
        "horsePower": 180,
        "modelName": "Corolla",
        "modelYear": 2021,
        "purchasePrice": 21000,
        "fuelType": "Hybrid",
    }

    res_update = client.put("/vehicle/upd123", json=updated_payload)
    assert res_update.status_code == 200

    data = res_update.json()
    assert data["description"] == "Updated description"
    assert data["horsePower"] == 180
    assert data["modelYear"] == 2021
    assert data["fuelType"] == "Hybrid"


def test_delete_vehicle():
    payload = get_sample_payload("del123")
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    # DELETE: 204 NONE
    res_delete = client.delete("/vehicle/del123")
    assert res_delete.status_code == 204

    res_get = client.get("/vehicle/del123")
    assert res_get.status_code == 404
