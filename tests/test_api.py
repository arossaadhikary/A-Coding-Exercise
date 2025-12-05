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


def get_sample_payload(vin: str = "1HGCM82633A004352"):
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
    # valid 17-char VIN
    payload = get_sample_payload("1HGCM82633A004352")

    res = client.post("/vehicle", json=payload)
    assert res.status_code == 201

    data = res.json()
    assert data["vin"] == "1HGCM82633A004352"
    assert data["manuName"] == "Toyota"
    assert "id" in data


def test_create_vehicle_duplicate_vin_returns_422():
    '''
    Expected output: success, fail
    '''
    # valid 17-char VIN for duplicate test
    dup_vin = "1HGCM82633A004353"
    payload = get_sample_payload(dup_vin)

    res1 = client.post("/vehicle", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/vehicle", json=payload)
    assert res2.status_code == 422

    data = res2.json()
    assert "vin" in str(data).lower()


def test_get_vehicle_by_vin():
    # using lowercase valid VIN to show normalization
    vin = "1hgcm82633a004354"
    payload = get_sample_payload(vin)

    # POST: 201 OK
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    # GET: 200 OK
    res_get = client.get("/vehicle/1hgcm82633a004354")
    assert res_get.status_code == 200

    data = res_get.json()
    # VIN should be normalized to uppercase, still 17 chars
    assert data["vin"] == "1HGCM82633A004354"
    assert data["manuName"] == "Toyota"


def test_list_vehicles():
    res_empty = client.get("/vehicle")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    # add one vehicle with a valid 17 char VIN
    vin = "1hgcm82633a004355"
    client.post("/vehicle", json=get_sample_payload(vin))

    res_list = client.get("/vehicle")
    assert res_list.status_code == 200

    data = res_list.json()
    assert isinstance(data, list)
    assert len(data) == 1
    # normalized to uppercase
    assert data[0]["vin"] == "1HGCM82633A004355"


def test_update_vehicle():
    # valid VIN for update test
    vin = "1hgcm82633a004356"
    payload = get_sample_payload(vin)
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    updated_payload = {
        "vin": vin,  # must match path VIN
        "manuName": "Toyota",
        "description": "Updated description",
        "horsePower": 180,
        "modelName": "Corolla",
        "modelYear": 2021,
        "purchasePrice": 21000,
        "fuelType": "Hybrid",
    }

    res_update = client.put(f"/vehicle/{vin}", json=updated_payload)
    assert res_update.status_code == 200

    data = res_update.json()
    assert data["description"] == "Updated description"
    assert data["horsePower"] == 180
    assert data["modelYear"] == 2021
    assert data["fuelType"] == "Hybrid"


def test_delete_vehicle():
    # valid VIN for delete test
    vin = "1hgcm82633a004357"
    payload = get_sample_payload(vin)
    res_create = client.post("/vehicle", json=payload)
    assert res_create.status_code == 201

    # DELETE: 204 NONE
    res_delete = client.delete(f"/vehicle/{vin}")
    assert res_delete.status_code == 204

    res_get = client.get(f"/vehicle/{vin}")
    assert res_get.status_code == 404

def test_invalid_vin_inputs():
    """
    Test several invalid VIN scenarios:
    - too short
    - too long
    - contains illegal characters (I, O, Q)
    - contains non-alphanumeric characters
    - missing VIN entirely
    """

    payload_short = get_sample_payload("1HGCM82633A00435")
    res_short = client.post("/vehicle", json=payload_short)
    assert res_short.status_code == 422
    assert "17 characters" in str(res_short.json()).lower()

    payload_long = get_sample_payload("1HGCM82633A00435299")
    res_long = client.post("/vehicle", json=payload_long)
    assert res_long.status_code == 422
    assert "17 characters" in str(res_long.json()).lower()

    payload_forbidden = get_sample_payload("1HGCM8I633A004352")  # contains I
    res_forbidden = client.post("/vehicle", json=payload_forbidden)
    assert res_forbidden.status_code == 422
    assert "cannot contain" in str(res_forbidden.json()).lower()

    payload_symbols = get_sample_payload("1HGCM82633A00!352")
    res_symbols = client.post("/vehicle", json=payload_symbols)
    assert res_symbols.status_code == 422
    assert "only a-z and 0-9" in str(res_symbols.json()).lower()

    missing_vin_payload = get_sample_payload()
    del missing_vin_payload["vin"]
    res_missing = client.post("/vehicle", json=missing_vin_payload)
    assert res_missing.status_code == 422
