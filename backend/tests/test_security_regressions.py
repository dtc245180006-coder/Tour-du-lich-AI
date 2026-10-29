import hashlib

from fastapi.testclient import TestClient
from backend.app import auth
from backend.app.main import app, catch_all_frontend_pages
from fastapi import HTTPException
import pytest


def test_password_hashes_use_random_salts_and_support_legacy():
    first = auth.hash_password("sample password")
    assert first != auth.hash_password("sample password")
    assert auth.verify_password("sample password", first)
    assert not auth.verify_password("wrong", first)
    legacy = hashlib.sha256(b"tour_ai_salt_secure_2026old-password").hexdigest()
    assert auth.verify_password("old-password", legacy)


def test_anonymous_cannot_access_staff_bookings_or_record_payment():
    client = TestClient(app)
    assert client.get("/api/v1/bookings").status_code == 401
    assert client.get("/api/v1/bookings/1").status_code == 401
    assert client.post("/api/v1/bookings", json={
        "departure_id": 1, "customer_name": "Test", "customer_phone": "0901234567",
        "num_people": 1, "initial_payment": 1000000,
    }).status_code == 401
    assert client.post("/api/v1/auth/switch-role/ADMIN").status_code in (404, 405)


@pytest.mark.parametrize("path", ["../.env", "../../requirements.txt", "..\\.env"])
def test_file_handler_rejects_paths_outside_frontend(path):
    with pytest.raises(HTTPException) as exc:
        catch_all_frontend_pages(path)
    assert exc.value.status_code == 404


def test_public_dashboard_does_not_disclose_recent_customers():
    result = TestClient(app).get("/api/v1/stats/dashboard")
    assert result.status_code == 200
    assert result.json()["recent_bookings"] == []


def test_guest_request_retry_does_not_create_duplicate_booking():
    from backend.app.database import SessionLocal
    from backend.app import models
    from datetime import date, timedelta
    with SessionLocal() as db:
        tour = models.Tour(code='IDEMPOTENCY', title='Retry', destination='Test', base_price=100000)
        db.add(tour); db.flush()
        dep = models.Departure(tour_id=tour.id, departure_date=date.today()+timedelta(days=20),
                               return_date=date.today()+timedelta(days=21), total_slots=3, available_slots=3)
        db.add(dep); db.commit(); dep_id = dep.id
    client = TestClient(app)
    payload = {'departure_id': dep_id, 'customer_name': 'Retry', 'customer_phone': '0901234000', 'num_people': 1}
    headers = {'Idempotency-Key': 'guest-retry-test'}
    first = client.post('/api/v1/bookings/guest-request', json=payload, headers=headers)
    second = client.post('/api/v1/bookings/guest-request', json=payload, headers=headers)
    assert first.status_code == second.status_code == 200
    assert first.json()['id'] == second.json()['id']
    changed = client.post('/api/v1/bookings/guest-request', json={**payload, 'num_people': 2}, headers=headers)
    assert changed.status_code == 409
