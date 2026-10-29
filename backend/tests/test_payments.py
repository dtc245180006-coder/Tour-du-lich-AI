import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app import models, schemas, crud

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    tour = models.Tour(
        code="TEST-PAY-01",
        title="Tour Test Thanh Toán",
        destination="Phú Quốc",
        base_price=5000000
    )
    session.add(tour)
    session.commit()
    
    departure = models.Departure(
        tour_id=tour.id,
        departure_date=date.today() + timedelta(days=15),
        return_date=date.today() + timedelta(days=18),
        total_slots=20,
        available_slots=20,
        status="OPEN"
    )
    session.add(departure)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_deposit_and_final_payment_flow(db):
    """Kiểm tra luồng thanh toán: Đặt chỗ chưa thanh toán -> Đặt cọc (DEPOSITED) -> Thanh toán đủ (CONFIRMED)"""
    departure = db.query(models.Departure).first()
    
    # 1. Đặt 2 vé (Tổng tiền 10 triệu, cọc yêu cầu 30% = 3 triệu)
    booking_in = schemas.BookingCreate(
        departure_id=departure.id,
        customer_name="Lê Văn Hậu",
        customer_phone="0944556677",
        num_people=2,
        initial_payment=0.0 # Chưa trả tiền
    )
    booking = crud.create_booking(db, booking_in)
    assert booking.status == "PENDING"
    assert booking.paid_amount == 0.0
    assert booking.total_amount == 10000000
    assert booking.deposit_amount == 3000000
    
    # 2. Đóng tiền cọc 3.000.000 VNĐ
    pay_deposit = schemas.PaymentCreate(
        booking_id=booking.id,
        payment_type="DEPOSIT",
        amount=3000000,
        payment_method="BANK_TRANSFER"
    )
    crud.add_payment(db, pay_deposit, created_by="Kế toán viên")
    db.refresh(booking)
    assert booking.paid_amount == 3000000
    assert booking.status == "DEPOSITED"
    
    # 3. Đóng đợt cuối 7.000.000 VNĐ
    pay_final = schemas.PaymentCreate(
        booking_id=booking.id,
        payment_type="FINAL",
        amount=7000000,
        payment_method="CASH"
    )
    crud.add_payment(db, pay_final, created_by="Kế toán viên")
    db.refresh(booking)
    assert booking.paid_amount == 10000000
    assert booking.status == "CONFIRMED"
    
    # Kiểm tra lịch sử thanh toán
    payments = crud.get_payments(db, booking_id=booking.id)
    assert len(payments) == 2
