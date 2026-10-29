import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from backend.app.database import Base
from backend.app import models, schemas, crud

# Cấu hình CSDL SQLite in-memory độc lập cho kiểm thử
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Tạo tour mẫu
    tour = models.Tour(
        code="TEST-TOUR-01",
        title="Tour Thử Nghiệm Nha Trang",
        destination="Nha Trang",
        category="BIEN_DAO",
        duration_days=3,
        duration_nights=2,
        base_price=3000000
    )
    session.add(tour)
    session.commit()
    
    # Tạo lịch khởi hành còn đúng 5 chỗ
    today = date.today()
    departure = models.Departure(
        tour_id=tour.id,
        departure_date=today + timedelta(days=20),
        return_date=today + timedelta(days=23),
        total_slots=10,
        available_slots=5,
        status="OPEN"
    )
    session.add(departure)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_booking_reduces_available_slots(db):
    """Kiểm tra: Khi khách đặt chỗ thành công, số chỗ còn lại phải giảm chính xác số khách"""
    departure = db.query(models.Departure).first()
    initial_slots = departure.available_slots
    assert initial_slots == 5
    
    booking_in = schemas.BookingCreate(
        departure_id=departure.id,
        customer_name="Trần Văn Test",
        customer_phone="0911223344",
        num_people=2,
        initial_payment=1800000
    )
    
    booking = crud.create_booking(db, booking_in, user_name="Test Runner")
    assert booking.id is not None
    assert booking.num_people == 2
    assert booking.total_amount == 6000000 # 3.000.000 x 2
    assert booking.deposit_amount == 1800000 # 30% của 6tr
    assert booking.paid_amount == 1800000
    assert booking.status == "DEPOSITED"
    
    # Số chỗ còn phải giảm từ 5 xuống 3
    db.refresh(departure)
    assert departure.available_slots == 3
    assert departure.status == "OPEN"

def test_prevent_overbooking(db):
    """Kiểm tra Chống Overbooking: Đặt quá số chỗ còn trống phải bị từ chối với lỗi 400"""
    departure = db.query(models.Departure).first()
    assert departure.available_slots == 5
    
    # Yêu cầu 6 chỗ trong khi chỉ còn 5 chỗ
    booking_in = schemas.BookingCreate(
        departure_id=departure.id,
        customer_name="Khách Đi Đoàn Đông",
        customer_phone="0999888777",
        num_people=6
    )
    
    with pytest.raises(HTTPException) as exc_info:
        crud.create_booking(db, booking_in)
        
    assert exc_info.value.status_code == 400
    assert "Không đủ chỗ trống" in exc_info.value.detail
    
    # Đảm bảo số chỗ không bị trừ sai
    db.refresh(departure)
    assert departure.available_slots == 5

def test_booking_fills_departure_to_full(db):
    """Kiểm tra: Khi đặt hết số chỗ còn lại, trạng thái đợt khởi hành tự động chuyển sang FULL"""
    departure = db.query(models.Departure).first()
    
    booking_in = schemas.BookingCreate(
        departure_id=departure.id,
        customer_name="Khách Vừa Đủ",
        customer_phone="0933445566",
        num_people=5
    )
    
    crud.create_booking(db, booking_in)
    db.refresh(departure)
    assert departure.available_slots == 0
    assert departure.status == "FULL"

def test_cancellation_restores_slots_and_refunds(db):
    """Kiểm tra nghiệp vụ hủy tour: Phục hồi số chỗ và tính toán tiền hoàn cọc theo ngày"""
    departure = db.query(models.Departure).first()
    
    # 1. Đặt 3 chỗ và thanh toán 100%
    booking_in = schemas.BookingCreate(
        departure_id=departure.id,
        customer_name="Khách Muốn Hủy",
        customer_phone="0977665544",
        num_people=3,
        initial_payment=9000000
    )
    booking = crud.create_booking(db, booking_in)
    db.refresh(departure)
    assert departure.available_slots == 2
    
    # 2. Hủy tour trước 20 ngày (trên 15 ngày -> chính sách hoàn 100%)
    cancel_in = schemas.BookingCancel(reason="Bận việc đột xuất gia đình")
    cancelled_booking = crud.cancel_booking(db, booking.id, cancel_in, user_name="Admin Test")
    
    # 3. Kiểm tra số chỗ được hoàn lại đầy đủ
    db.refresh(departure)
    assert departure.available_slots == 5
    assert cancelled_booking.status == "CANCELLED"
    assert cancelled_booking.refund_amount == 9000000 # Hoàn 100%
    assert "100%" in cancelled_booking.cancellation_reason

def test_guest_booking_and_consultant_confirmation(db):
    """
    Kiểm tra luồng khách vãng lai:
    1. Khách gửi yêu cầu -> Trạng thái WAITING_CONFIRM, số chỗ trống CHƯA bị trừ.
    2. Nhân viên tư vấn duyệt đơn -> Số chỗ trống chính thức bị trừ và đơn chuyển sang PENDING.
    """
    departure = db.query(models.Departure).first()
    assert departure.available_slots == 5
    
    # 1. Khách vãng lai gửi yêu cầu
    guest_in = schemas.GuestBookingCreate(
        departure_id=departure.id,
        customer_name="Khách Vãng Lai Test",
        customer_phone="0918889999",
        customer_email="guest@test.vn",
        num_people=2,
        special_requests="Cần tư vấn thêm lịch trình"
    )
    req_booking = crud.create_guest_booking(db, guest_in)
    assert req_booking.status == "WAITING_CONFIRM"
    assert req_booking.num_people == 2
    
    # Số chỗ CHƯA bị trừ khi chưa được nhân viên xác nhận
    db.refresh(departure)
    assert departure.available_slots == 5
    
    # 2. Nhân viên tư vấn liên hệ và xác nhận giữ chỗ
    confirm_in = schemas.BookingConfirmRequest(note="Đã gọi điện tư vấn và chốt ngày đi")
    confirmed_booking = crud.confirm_guest_booking(db, req_booking.id, confirm_in, user_name="Tư Vấn Mỹ Duyên")
    assert confirmed_booking.status == "PENDING"
    
    # Lúc này số chỗ mới chính thức bị trừ từ 5 xuống 3
    db.refresh(departure)
    assert departure.available_slots == 3
