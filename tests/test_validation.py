def test_create_intent_validation_error(client):
    resp = client.post("/api/payments/intents", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

