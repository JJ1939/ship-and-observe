from app import app

def test_health():
    res = app.test_client().get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}

def test_add_item_requires_name():
    res = app.test_client().post("/items", json={})
    assert res.status_code == 400
