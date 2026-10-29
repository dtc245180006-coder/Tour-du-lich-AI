import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app import auth, models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def init_test_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed users
    admin_user = models.User(
        username="admin",
        hashed_password=auth.hash_password("admin123"),
        full_name="Administrator",
        role="ADMIN",
        is_active=True
    )
    consultant_user = models.User(
        username="tuvan",
        hashed_password=auth.hash_password("tuvan123"),
        full_name="Consultant User",
        role="CONSULTANT",
        is_active=True
    )
    db.add_all([admin_user, consultant_user])
    db.commit()
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)

def get_tokens():
    client = TestClient(app)
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_res.json()["access_token"]
    
    tuvan_res = client.post("/api/v1/auth/login", json={"username": "tuvan", "password": "tuvan123"})
    tuvan_token = tuvan_res.json()["access_token"]
    return admin_token, tuvan_token

def test_consultant_cannot_modify_tours():
    admin_token, tuvan_token = get_tokens()
    client = TestClient(app)

    # Consultant attempts to create tour -> 403 Forbidden
    tuvan_headers = {"Authorization": f"Bearer {tuvan_token}"}
    res = client.post("/api/v1/tours", json={
        "code": "TOUR-TEST",
        "title": "Tour Test RBAC",
        "destination": "Da Nang",
        "category": "BIEN_DAO",
        "duration_days": 3,
        "duration_nights": 2,
        "base_price": 3500000
    }, headers=tuvan_headers)
    assert res.status_code == 403

    # Admin creates tour -> 200
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_admin = client.post("/api/v1/tours", json={
        "code": "TOUR-TEST",
        "title": "Tour Test RBAC",
        "destination": "Da Nang",
        "category": "BIEN_DAO",
        "duration_days": 3,
        "duration_nights": 2,
        "base_price": 3500000
    }, headers=admin_headers)
    assert res_admin.status_code == 200
    tour_id = res_admin.json()["id"]

    # Consultant attempts to update tour -> 403
    res_up = client.put(f"/api/v1/tours/{tour_id}", json={"title": "Updated Title"}, headers=tuvan_headers)
    assert res_up.status_code == 403

    # Consultant attempts to delete tour -> 403
    res_del = client.delete(f"/api/v1/tours/{tour_id}", headers=tuvan_headers)
    assert res_del.status_code == 403

    # Consultant CAN view tours -> 200
    res_view = client.get("/api/v1/tours", headers=tuvan_headers)
    assert res_view.status_code == 200
    assert len(res_view.json()) == 1

def test_consultant_cannot_modify_departures():
    admin_token, tuvan_token = get_tokens()
    client = TestClient(app)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    tuvan_headers = {"Authorization": f"Bearer {tuvan_token}"}

    # Setup a tour first
    t_res = client.post("/api/v1/tours", json={
        "code": "TOUR-DEP",
        "title": "Tour Departure Test",
        "destination": "Ha Long",
        "category": "BIEN_DAO",
        "duration_days": 2,
        "duration_nights": 1,
        "base_price": 2000000
    }, headers=admin_headers)
    tour_id = t_res.json()["id"]

    # Consultant attempts to create departure -> 403
    dep_payload = {
        "tour_id": tour_id,
        "departure_date": "2026-10-01",
        "return_date": "2026-10-03",
        "total_slots": 20,
        "status": "OPEN"
    }
    res = client.post("/api/v1/departures", json=dep_payload, headers=tuvan_headers)
    assert res.status_code == 403

    # Admin creates departure -> 200
    res_admin = client.post("/api/v1/departures", json=dep_payload, headers=admin_headers)
    assert res_admin.status_code == 200
    dep_id = res_admin.json()["id"]

    # Consultant attempts start/complete/update/delete departure -> 403
    assert client.post(f"/api/v1/departures/{dep_id}/start", headers=tuvan_headers).status_code == 403
    assert client.post(f"/api/v1/departures/{dep_id}/complete", headers=tuvan_headers).status_code == 403
    assert client.put(f"/api/v1/departures/{dep_id}", json={"notes": "test"}, headers=tuvan_headers).status_code == 403
    assert client.delete(f"/api/v1/departures/{dep_id}", headers=tuvan_headers).status_code == 403

    # Consultant CAN view departures -> 200
    assert client.get("/api/v1/departures", headers=tuvan_headers).status_code == 200

def test_consultant_cannot_modify_guides():
    admin_token, tuvan_token = get_tokens()
    client = TestClient(app)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    tuvan_headers = {"Authorization": f"Bearer {tuvan_token}"}

    guide_payload = {
        "full_name": "Nguyen Van A",
        "phone": "0987654321",
        "languages": "Tiếng Việt, Tiếng Anh",
        "experience_years": 5,
        "status": "AVAILABLE"
    }

    # Consultant attempts to create guide -> 403
    assert client.post("/api/v1/guides", json=guide_payload, headers=tuvan_headers).status_code == 403

    # Admin creates guide -> 200
    res_admin = client.post("/api/v1/guides", json=guide_payload, headers=admin_headers)
    assert res_admin.status_code == 200
    guide_id = res_admin.json()["id"]

    # Consultant attempts to update/delete guide -> 403
    assert client.put(f"/api/v1/guides/{guide_id}", json={"experience_years": 6}, headers=tuvan_headers).status_code == 403
    assert client.delete(f"/api/v1/guides/{guide_id}", headers=tuvan_headers).status_code == 403

    # Consultant CAN view guides -> 200
    assert client.get("/api/v1/guides", headers=tuvan_headers).status_code == 200

def test_multi_field_search():
    admin_token, _ = get_tokens()
    client = TestClient(app)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Add tours
    client.post("/api/v1/tours", json={
        "code": "TOUR-HN-SAPA",
        "title": "Hành trình Sa Pa Mù Sương",
        "destination": "Lào Cai - Sa Pa",
        "category": "NUI_RUNG",
        "duration_days": 3,
        "duration_nights": 2,
        "base_price": 2800000,
        "highlights": "Đỉnh Fansipan, bản Cát Cát"
    }, headers=admin_headers)

    client.post("/api/v1/tours", json={
        "code": "TOUR-PQ-SUN",
        "title": "Thiên Đường Biển Đảo Phú Quốc",
        "destination": "Kiên Giang - Phú Quốc",
        "category": "BIEN_DAO",
        "duration_days": 4,
        "duration_nights": 3,
        "base_price": 5500000,
        "highlights": "Bãi Sao, Cáp treo Hòn Thơm"
    }, headers=admin_headers)

    # Search tours by keyword
    r1 = client.get("/api/v1/tours?keyword=fansipan")
    assert len(r1.json()) == 1
    assert r1.json()[0]["code"] == "TOUR-HN-SAPA"

    r2 = client.get("/api/v1/tours?keyword=Phú Quốc")
    assert len(r2.json()) == 1
    assert r2.json()[0]["code"] == "TOUR-PQ-SUN"

    r3 = client.get("/api/v1/tours?category=BIEN_DAO")
    assert len(r3.json()) == 1
    assert r3.json()[0]["code"] == "TOUR-PQ-SUN"

def test_guest_and_consultant_cannot_view_revenue():
    """Kiểm tra: Khách vãng lai và Tư vấn viên không được xem doanh thu qua API thống kê"""
    client = TestClient(app)
    admin_token, tuvan_token = get_tokens()

    # 1. Khách vãng lai (không token): total_revenue = 0
    res_guest = client.get("/api/v1/stats/dashboard")
    assert res_guest.status_code == 200
    assert res_guest.json()["total_revenue"] == 0
    assert res_guest.json()["total_collected"] == 0

    # 2. Nhân viên tư vấn (CONSULTANT): total_revenue = 0
    res_tuvan = client.get(
        "/api/v1/stats/dashboard",
        headers={"Authorization": f"Bearer {tuvan_token}"}
    )
    assert res_tuvan.status_code == 200
    assert res_tuvan.json()["total_revenue"] == 0
    assert res_tuvan.json()["total_collected"] == 0

    # 3. Quản trị viên (ADMIN): Được xem doanh thu đầy đủ
    res_admin = client.get(
        "/api/v1/stats/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    assert "total_revenue" in res_admin.json()

