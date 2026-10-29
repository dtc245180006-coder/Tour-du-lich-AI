from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.money import Money

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default="CONSULTANT") # ADMIN, CONSULTANT, ACCOUNTANT
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Tour(Base):
    __tablename__ = "tours"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    destination = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, default="BIEN_DAO") # BIEN_DAO, TAY_BAC, DI_SAN, MIEN_TAY, NGHIDUONG, KHAC
    duration_days = Column(Integer, nullable=False, default=3)
    duration_nights = Column(Integer, nullable=False, default=2)
    base_price = Column(Money(), nullable=False, default=0)
    description = Column(Text, nullable=True)
    itinerary_summary = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    departures = relationship("Departure", back_populates="tour", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="tour", cascade="all, delete-orphan")

class TourGuide(Base):
    __tablename__ = "tour_guides"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    languages = Column(String(100), default="Tiếng Việt")
    experience_years = Column(Integer, default=3)
    status = Column(String(20), default="AVAILABLE") # AVAILABLE, ON_TOUR, OFF
    rating = Column(Float, default=4.8)
    notes = Column(Text, nullable=True)
    
    departures = relationship("Departure", back_populates="guide")

class Departure(Base):
    __tablename__ = "departures"
    
    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    total_slots = Column(Integer, nullable=False, default=25)
    available_slots = Column(Integer, nullable=False, default=25)
    price_override = Column(Money(), nullable=True) # Giá riêng cho đợt khởi hành nếu khác base_price
    guide_id = Column(Integer, ForeignKey("tour_guides.id"), nullable=True)
    status = Column(String(20), default="OPEN") # OPEN, FULL, COMPLETED, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tour = relationship("Tour", back_populates="departures")
    guide = relationship("TourGuide", back_populates="departures")
    bookings = relationship("Booking", back_populates="departure", cascade="all, delete-orphan")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=True)
    id_card = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bookings = relationship("Booking", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(50), unique=True, index=True, nullable=False)
    departure_id = Column(Integer, ForeignKey("departures.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    num_people = Column(Integer, nullable=False, default=1)
    total_amount = Column(Money(), nullable=False, default=0)
    deposit_amount = Column(Money(), nullable=False, default=0)
    paid_amount = Column(Money(), nullable=False, default=0)
    status = Column(String(20), default="PENDING") # PENDING, DEPOSITED, CONFIRMED, COMPLETED, CANCELLED
    refund_amount = Column(Money(), default=0)
    cancellation_reason = Column(Text, nullable=True)
    special_requests = Column(Text, nullable=True)
    access_token = Column(String(64), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    departure = relationship("Departure", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    payment_type = Column(String(20), nullable=False) # DEPOSIT (Đặt cọc), FINAL (Thanh toán đợt cuối), FULL (Toàn bộ), REFUND (Hoàn tiền)
    amount = Column(Money(), nullable=False)
    payment_method = Column(String(30), default="BANK_TRANSFER") # BANK_TRANSFER, CASH, CREDIT_CARD, VNPAY, MOMO
    status = Column(String(20), default="COMPLETED") # COMPLETED, PENDING, FAILED
    transaction_code = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), default="Hệ thống")
    
    booking = relationship("Booking", back_populates="payments")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    customer_name = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False, default=5) # 1 - 5 sao
    comments = Column(Text, nullable=False)
    guide_rating = Column(Integer, default=5) # 1 - 5 sao
    sentiment = Column(String(20), default="POSITIVE") # POSITIVE, NEUTRAL, NEGATIVE
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tour = relationship("Tour", back_populates="feedbacks")
    booking = relationship("Booking", back_populates="feedbacks")

class AISessionLog(Base):
    __tablename__ = "ai_session_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_type = Column(String(50), nullable=False) # CONSULTATION, DESCRIPTION_GEN, FEEDBACK_SUMMARY
    input_prompt = Column(Text, nullable=False)
    response_content = Column(Text, nullable=False)
    model_name = Column(String(50), default="local-grounded-engine")
    created_at = Column(DateTime, default=datetime.utcnow)


class BookingRequestKey(Base):
    __tablename__ = "booking_request_keys"
    key = Column(String(64), primary_key=True)
    fingerprint = Column(String(64), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
