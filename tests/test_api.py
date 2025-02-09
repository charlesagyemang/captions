from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_transcribe():
    audio_file = {"file": ("test.mp3", open("tests/test.mp3", "rb"), "audio/mpeg")}
    response = client.post("/transcribe/", files=audio_file)
    assert response.status_code == 200
    assert "text" in response.json()
