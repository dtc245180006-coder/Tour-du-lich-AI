from datetime import datetime, date
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator

# ==================== USER & AUTH ====================
Role = Literal["ADMIN", "CONSULTANT", "ACCOUNTANT"]
DepartureStatus = Literal["OPEN", "FULL", "RUNNING", "ON_TOUR", "COMPLETED", "CANCELLED"]

class InputModel(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_explicit_null(self):
        required = {'title', 'destination', 'code', 'full_name', 'role', 'status', 'duration_days', 'duration_nights', 'base_price', 'total_slots', 'available_slots', 'departure_date', 'return_date', 'is_active'}
        for name in self.model_fields_set & required:
            if getattr(self, name, None) is None:
                raise ValueError(f"{name} không được null.")
        return self

    @field_validator("*", mode="after")
    @classmethod
    def validate_text(cls, value, info):
        if isinstance(value, str):
            if info.field_name != "password":
                value = value.strip()
            limits = {'username':50, 'full_name':100, 'customer_name':100, 'title':200, 'code':30, 'destination':100, 'email':100, 'customer_email':100, 'phone':20, 'customer_phone':20, 'transaction_code':100}
            if len(value) > limits.get(info.field_name, 10000):
                raise ValueError("Nội dung quá dài.")
            if any(c in value for c in ("\x00", "\r", "\n")) and info.field_name in ("api_key", "model_name"):
                raise ValueError("Cấu hình không được chứa ký tự xuống dòng.")
            if info.field_name in ("customer_name", "customer_phone", "full_name", "username", "title", "code", "destination", "reason", "query") and not value:
                raise ValueError("Thông tin này không được để trống.")
            if info.field_name in ("phone", "customer_phone"):
                import re
                if not re.fullmatch(r"[+()0-9 .-]{8,20}", value):
                    raise ValueError("Số điện thoại không hợp lệ.")
            if info.field_name in ("email", "customer_email") and value:
                import re
                if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
                    raise ValueError("Email không hợp lệ.")
        if info.field_name in ('amount', 'initial_payment', 'base_price', 'price_override', 'deposit_amount') and value is not None:
            if value != int(value) or abs(value) > 1_000_000_000_000:
                raise ValueError("Số tiền phải là số nguyên VNĐ, tối đa 1.000 tỷ.")
        return value

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(InputModel):
    username: str
    password: str = Field(min_length=8, max_length=256)
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Role = "CONSULTANT"

class UserUpdateAdmin(InputModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[Role] = None # ADMIN, CONSULTANT, ACCOUNTANT
    password: Optional[str] = Field(default=None, min_length=8, max_length=256)
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# ==================== TOUR ====================
class TourBase(InputModel):
    code: str
    title: str
    destination: str
    category: str = "BIEN_DAO"
    duration_days: int = Field(default=3, ge=1)
    duration_nights: int = Field(default=2, ge=0)
    base_price: float = Field(ge=0, allow_inf_nan=False)
    description: Optional[str] = None
    itinerary_summary: Optional[str] = None
    highlights: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class TourCreate(TourBase):
    pass

class TourUpdate(InputModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    category: Optional[str] = None
    duration_days: Optional[int] = Field(default=None, ge=1)
    duration_nights: Optional[int] = Field(default=None, ge=0)
    base_price: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    description: Optional[str] = None
    itinerary_summary: Optional[str] = None
    highlights: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class TourOut(TourBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==================== TOUR GUIDE ====================
class TourGuideBase(InputModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    languages: str = "Tiếng Việt"
    experience_years: int = Field(default=3, ge=0)
    status: Literal["AVAILABLE", "ON_TOUR", "OFF"] = "AVAILABLE"
    rating: float = Field(default=4.8, ge=0, le=5)
    notes: Optional[str] = None

class TourGuideCreate(TourGuideBase):
    pass

class TourGuideUpdate(InputModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    languages: Optional[str] = None
    experience_years: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    notes: Optional[str] = None

class TourGuideOut(TourGuideBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# ==================== DEPARTURE ====================
class DepartureBase(InputModel):
    tour_id: int
    departure_date: date
    return_date: date
    total_slots: int = Field(default=25, ge=1)
    available_slots: Optional[int] = Field(default=None, ge=0)
    price_override: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    guide_id: Optional[int] = None
    status: DepartureStatus = "OPEN"
    notes: Optional[str] = None

class DepartureCreate(DepartureBase):
    @model_validator(mode="after")
    def validate_capacity(self):
        if self.return_date < self.departure_date:
            raise ValueError("Ngày về phải từ ngày khởi hành trở đi.")
        if self.available_slots is not None and self.available_slots > self.total_slots:
            raise ValueError("Chỗ còn lại không được vượt sức chứa.")
        return self

class DepartureUpdate(InputModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    total_slots: Optional[int] = Field(default=None, ge=1)
    available_slots: Optional[int] = Field(default=None, ge=0)
    price_override: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    guide_id: Optional[int] = None
    status: Optional[DepartureStatus] = None
    notes: Optional[str] = None

class DepartureOut(DepartureBase):
    id: int
    available_slots: int
    created_at: datetime
    tour_title: Optional[str] = None
    tour_code: Optional[str] = None
    guide_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== CUSTOMER ====================
class CustomerBase(InputModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==================== PAYMENT ====================
class PaymentCreate(InputModel):
    booking_id: int
    payment_type: Literal["DEPOSIT", "FINAL", "FULL", "REFUND"] = "DEPOSIT" # DEPOSIT, FINAL, FULL, REFUND
    amount: float = Field(gt=0, allow_inf_nan=False)
    payment_method: str = "BANK_TRANSFER" # BANK_TRANSFER, CASH, CREDIT_CARD
    transaction_code: Optional[str] = None
    note: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    booking_id: int
    payment_type: str
    amount: float
    payment_method: str
    status: str
    transaction_code: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    created_by: str
    
    model_config = ConfigDict(from_attributes=True)

# ==================== BOOKING ====================
class BookingCreate(InputModel):
    departure_id: int
    # Thông tin khách hàng đặt
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_id_card: Optional[str] = None
    customer_address: Optional[str] = None
    # Chi tiết đặt chỗ
    num_people: int = Field(gt=0, description="Số lượng người lớn/chỗ ngồi")
    special_requests: Optional[str] = None
    # Tùy chọn thanh toán đợt đầu (đặt cọc hoặc toàn bộ)
    initial_payment: float = Field(default=0.0, ge=0, allow_inf_nan=False)
    payment_method: Optional[str] = "BANK_TRANSFER"

class GuestBookingCreate(InputModel):
    departure_id: int
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    num_people: int = Field(default=1, gt=0)
    special_requests: Optional[str] = None

class BookingConfirmRequest(BaseModel):
    deposit_amount: Optional[float] = None
    note: Optional[str] = None

class BookingCancel(InputModel):
    reason: str
    refund_percentage: Optional[float] = Field(default=None, ge=0, le=100, allow_inf_nan=False) # Nếu None, hệ thống tự tính dựa vào số ngày trước khởi hành

class BookingTrackRequest(InputModel):
    booking_code: str
    contact: str  # Số điện thoại hoặc email đăng ký

class ResendTrackRequest(InputModel):
    email: str  # Địa chỉ Gmail/Email cần tìm lại đơn hàng

class BookingOut(BaseModel):
    id: int
    booking_code: str
    departure_id: int
    customer_id: int
    num_people: int
    total_amount: float
    deposit_amount: float
    paid_amount: float
    status: str
    refund_amount: float
    cancellation_reason: Optional[str] = None
    special_requests: Optional[str] = None
    created_at: datetime
    
    # Nested info
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    tour_title: Optional[str] = None
    departure_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== FEEDBACK ====================
class FeedbackCreate(InputModel):
    tour_id: int
    booking_id: Optional[int] = None
    customer_name: str
    rating: int = Field(ge=1, le=5)
    comments: str
    guide_rating: int = Field(default=5, ge=1, le=5)

class FeedbackOut(BaseModel):
    id: int
    tour_id: int
    booking_id: Optional[int] = None
    customer_name: str
    rating: int
    comments: str
    guide_rating: int
    sentiment: str
    created_at: datetime
    tour_title: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== AI SCHEMAS ====================
class AIConsultRequest(InputModel):
    query: str = Field(..., description="Câu hỏi hoặc yêu cầu của khách (ngân sách, số ngày, sở thích)")
    budget: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    days: Optional[int] = Field(default=None, ge=1, le=365)
    preferred_destination: Optional[str] = None

class RecommendedTourItem(BaseModel):
    tour_id: int
    departure_id: Optional[int] = None
    code: str
    title: str
    destination: str
    duration: str
    price: float
    available_slots: int
    next_departure_date: Optional[str] = None
    match_reason: str

class AIConsultResponse(BaseModel):
    advice_text: str
    recommended_tours: List[RecommendedTourItem] = []
    engine_used: str

class AIDescriptionRequest(InputModel):
    tour_title: str
    destination: Optional[str] = "" 
    duration_days: int = Field(default=3, ge=1)
    duration_nights: int = Field(default=2, ge=0)
    highlights: Optional[str] = None
    target_audience: Optional[str] = "Gia đình, bạn bè hoặc khách lẻ"

class AIDescriptionResponse(BaseModel):
    description: str
    itinerary_summary: str
    marketing_slogan: str
    packing_tips: str
    engine_used: str

class AIFeedbackSummaryRequest(BaseModel):
    tour_id: Optional[int] = None # None: tóm tắt tất cả phản hồi

class AIFeedbackSummaryResponse(BaseModel):
    total_feedbacks: int
    average_rating: float
    sentiment_breakdown: dict
    positive_highlights: List[str]
    improvement_areas: List[str]
    guide_performance_summary: str
    executive_recommendation: str
    engine_used: str

class AIStatusResponse(BaseModel):
    is_gemini_active: bool
    masked_key: Optional[str] = None
    active_engine: str
    model_name: str
    mode: str
    description: str

class AIConfigureKeyRequest(InputModel):
    api_key: str
    model_name: Optional[str] = "gemini-1.5-flash"

# ==================== DASHBOARD STATS ====================
class DashboardStats(BaseModel):
    total_tours: int
    active_departures: int
    total_bookings: int
    total_revenue: float
    total_collected: float
    average_occupancy_rate: float
    top_tours: List[dict]
    recent_bookings: List[dict]
