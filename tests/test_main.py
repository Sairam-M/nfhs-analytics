import tempfile
import os

from fastapi.testclient import TestClient
from app.main import app

from .test_utility import upload_data_for_testing,\
                            VALID_DATA_1,\
                            VALID_DATA_2,\
                            SMALL_DATA_1

import pandas as pd

client = TestClient(app)


def test_upload_csv_valid():
    # Create sample dataframe
    df = pd.DataFrame({
        "state": ["A", "B", "C", ""],
        "anemia_women": [50, 60, "70", 30],
        "bmi_low": [20, 30, pd.NA,30],
        "child_mortality_rate": [10,15, -2, 1],
        "female_education_years": [7,8, None, 5],
        "rural_population": [30, 50, 40, 20]

    })

    # Create temp file
    tmp =  tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    try:
        df.to_csv(tmp.name, index=False)
        tmp.close() # Close the file so it can be read by the API

        # Open file in binary mode for upload
        with open(tmp.name, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.csv", f, "text/csv")} # File tuple: (filename, fileobj, content_type)
            )
    finally:
        os.remove(tmp.name)
    # Assertions
    assert response.status_code == 200
    assert "message" in response.json()

def test_upload_csv_invalid():
    response = client.post("/upload", files={})

    assert response.status_code in [400, 422]


def test_get_states_structure():
    upload_data_for_testing(VALID_DATA_1)
    response = client.get("/states")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["states"], list)

def test_top_states_by_score_default_n():
    upload_data_for_testing(VALID_DATA_2)
    response = client.get("/top-states-by-score")

    assert response.status_code == 200
    data = response.json()

    assert "top_states_by_score" in data
    assert isinstance(data["top_states_by_score"], list)
    assert len(data["top_states_by_score"]) == 5

def test_top_states_by_score_custom_n():
    upload_data_for_testing(VALID_DATA_1)
    n = 3
    response = client.get(f"/top-states-by-score?n={n}")

    assert response.status_code == 200
    data = response.json()

    assert len(data["top_states_by_score"]) == n

def test_get_state_profile_valid_name():
    upload_data_for_testing(SMALL_DATA_1)
    state = "A"
    response = client.get(f"/state-profile/{state}")

    assert response.status_code == 200
    data = response.json()

    assert data["state"] == state
    assert "metrics" in data
    assert type(data["metrics"]) == dict
    assert "risk_score" in data
    assert "score_band" in data
    assert "risk_category" in data
    assert "reason" in data

def test_get_state_profile_invalid_name():
    upload_data_for_testing(SMALL_DATA_1)
    state = "Random"
    response = client.get(f"/state-prodile/{state}")

    assert response.status_code == 404