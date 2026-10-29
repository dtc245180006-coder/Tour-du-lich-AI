import pytest
from datetime import date
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, SessionLocal, engine
from backend.app import models, schemas, crud

client = TestClient(app)

def test_guest_tracking_and_magic_link():
    db = SessionLocal()
    departure = db.query(models.Departure).filter(models.Departure.available_slots >= 2).first()
    assert departure is not None
    
    # 1. Tạo đặt tour khách vãng lai có email
    guest_in = schemas.GuestBookingCreate(
        departure_id=departure.id,
        customer_name="Trần Văn Khách",
        customer_phone="0987654321",
        customer_email="dtc245180006@ictu.edu.vn",
        num_people=2,
        special_requests="Yêu cầu phòng đơn"
    )
    booking = crud.create_guest_booking(db, guest_in)
    assert booking.access_token is not None
    assert len(booking.access_token) >= 32
    b_code = booking.booking_code
    token = booking.access_token
    db.close()
    
    # 2. Test Magic Link (Không cần đăng nhập)
    res_magic = client.get(f"/api/v1/bookings/magic-track?code={b_code}&token={token}")
    assert res_magic.status_code == 200
    data_magic = res_magic.json()
    assert data_magic["booking_code"] == b_code
    assert data_magic["customer"]["email"] == "dtc245180006@ictu.edu.vn"
    assert data_magic["total_amount"] > 0
    assert "vietqr" in data_magic
    assert "https://img.vietqr.io" in data_magic["vietqr"]["qr_url"]
    
    # 3. Test Magic Link với token sai -> 404
    res_bad_token = client.get(f"/api/v1/bookings/magic-track?code={b_code}&token=sai_token_123")
    assert res_bad_token.status_code == 404
    
    # 4. Test Tra cứu bằng Mã đơn + Số điện thoại (Chính xác)
    res_track_phone = client.post("/api/v1/bookings/track-guest", json={
        "booking_code": b_code,
        "contact": "0987654321"
    })
    assert res_track_phone.status_code == 200
    assert res_track_phone.json()["customer"]["full_name"] == "Trần Văn Khách"
    
    # 5. Test Tra cứu bằng Mã đơn + Email (Chính xác)
    res_track_email = client.post("/api/v1/bookings/track-guest", json={
        "booking_code": b_code,
        "contact": "dtc245180006@ictu.edu.vn"
    })
    assert res_track_email.status_code == 200
    
    # 6. Test Tra cứu với SĐT/Email không khớp -> 403 Forbidden
    res_track_wrong = client.post("/api/v1/bookings/track-guest", json={
        "booking_code": b_code,
        "contact": "0999999999"
    })
    assert res_track_wrong.status_code == 403
