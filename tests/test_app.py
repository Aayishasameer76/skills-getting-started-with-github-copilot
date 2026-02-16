from fastapi.testclient import TestClient
from src.app import app
from urllib.parse import quote
import uuid

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    enc_activity = quote(activity, safe="")
    email = f"test-{uuid.uuid4().hex}@example.com"

    # Sign up
    resp = client.post(f"/activities/{enc_activity}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail
    resp = client.post(f"/activities/{enc_activity}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{enc_activity}/participants?email={quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants


def test_unregister_nonexistent():
    activity = "Chess Club"
    enc_activity = quote(activity, safe="")
    email = "no-such-user@example.com"

    resp = client.delete(f"/activities/{enc_activity}/participants?email={quote(email, safe='')}")
    assert resp.status_code == 404
