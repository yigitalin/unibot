from io import BytesIO

from fastapi.testclient import TestClient

from app import app

browser = TestClient(app)


def test_ping():
    response = browser.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workspace_creation_rejects_non_pdf():
    response = browser.post(
        "/knowledge-bases",
        data={"label": "Test"},
        files={"files": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "En az bir PDF dosyasi yuklemelisiniz."


def test_chat_rejects_unknown_space():
    response = browser.post("/chat", json={"space_id": "missing", "prompt": "Merhaba"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Soru sorulacak bilgi alani bulunamadi."


def test_chat_rejects_blank_prompt():
    response = browser.post("/chat", json={"space_id": "missing", "prompt": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Soru alani bos birakilamaz."
