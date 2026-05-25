from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post(
        "/api/predict",
        json={"text": "This is a real news article that reports factual events."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "confidence" in data
    assert "word_impacts" in data
    assert "stylometrics" in data

def test_predict_empty_text():
    response = client.post(
        "/api/predict",
        json={"text": "   "}
    )
    assert response.status_code == 400

def test_model_info_endpoint():
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "vocab_size" in data
    assert "accuracy" in data
    assert "classes" in data

def test_sandbox_training_endpoint():
    response = client.post(
        "/api/train/sandbox",
        json={
            "items": [
                {"text": "fake news example one", "label": "FAKE"},
                {"text": "fake news example two", "label": "FAKE"},
                {"text": "real news example one", "label": "REAL"},
                {"text": "real news example two", "label": "REAL"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert "model_info" in data
