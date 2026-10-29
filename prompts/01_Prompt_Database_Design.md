# PROMPT 01: THIẾT KẾ CƠ SỞ DỮ LIỆU & QUẢN TRỊ MÔ HÌNH DỮ LIỆU
## (DATABASE ARCHITECTURE, MODELS & SEED DATA SPECIFICATION)

---

### BỐI CẢNH & VAI TRÒ CỦA AI:
Bạn là **Kiến Trúc Sư Hệ Thống kiêm Chuyên Gia Cơ Sở Dữ Liệu Cấp Cao (Lead System & Database Architect)**.
Nhiệm vụ của bạn là tiếp nhận tài liệu đặc tả bài toán của hệ thống **"VietJourney AI"** và thiết kế toàn diện tầng dữ liệu (Data Persistence Layer) sử dụng Python 3.10+ và SQLAlchemy 2.0 ORM.

---

### YÊU CẦU KỸ THUẬT & QUY TẮC BẤT BIẾN (STRICT INVARIANTS):

1. **Chuẩn Hóa Tiền Tệ Số Nguyên VNĐ (Monetary Precision)**:
   - Toàn bộ các cột tiền tệ (`base_price`, `total_amount`, `deposit_amount`, `paid_amount`, `refund_amount`, `amount`) PHẢI được định nghĩa kiểu **Số nguyên `Integer`** hoặc `DECIMAL(18, 0)`.
   - TUYỆT ĐỐI KHÔNG dùng kiểu số thực (`Float`, `Real`) để tính toán tiền tệ nhằm triệt tiêu hoàn toàn lỗi sai số dấu phẩy động trong kế toán.

2. **Khóa Định Danh Tra Cứu Đơn Hàng (Public Magic Link Token)**:
   - Bảng `bookings` bắt buộc phải có cột `access_token = Column(String(64), unique=True, index=True, nullable=False)`.
   - Token này được sinh ngẫu nhiên an toàn bằng `uuid.uuid4().hex` khi tạo đơn để khách hàng có thể tra cứu đơn tour trực tiếp không cần mật khẩu.

3. **Ràng Buộc Sức Chứa & Số Chỗ Còn (Slot Constraints)**:
   - Bảng `departures`: Cột `available_slots` không bao giờ được phép âm (`available_slots >= 0`) và không được vượt quá `total_seats`.

4. **Toàn Vẹn Khóa Ngoại & Hành Vi Xóa (Foreign Key Cascades)**:
   - Xóa `Tour` -> Xóa các `Departures` tương ứng (`cascade="all, delete-orphan"`).
   - Xóa `Booking` -> Xóa các `Payments` liên kết.
   - Khi đã phát sinh `Bookings`, CẤM xóa cứng `Tour` hoặc `Departure` (phải chặn bằng nghiệp vụ hoặc chuyển trạng thái sang `CANCELLED`).

---

### DANH SÁCH 9 BẢNG DỮ LIỆU CẦN ĐỊNH NGHĨA TRONG `backend/app/models.py`:

1. **`users`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `username`: String(50), Unique, index, not null.
   - `hashed_password`: String(255), not null.
   - `full_name`: String(100), not null.
   - `email`: String(100), nullable.
   - `phone`: String(20), nullable.
   - `role`: String(20), not null (Hỗ trợ: `ADMIN`, `CONSULTANT`, `ACCOUNTANT`, `GUIDE`).
   - `is_active`: Boolean, default=True.
   - `created_at`: DateTime, default=datetime.utcnow.

2. **`tours`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `code`: String(30), Unique, index, not null (ví dụ: `TOUR-PQ-3N2D`).
   - `title`: String(200), not null.
   - `destination`: String(100), not null.
   - `category`: String(50), default="Nội địa".
   - `duration_days`: Integer, not null.
   - `duration_nights`: Integer, not null.
   - `base_price`: Integer, not null (Số nguyên VNĐ, ví dụ: 4500000).
   - `description`: Text, nullable.
   - `itinerary_summary`: Text, nullable.
   - `highlights`: Text, nullable.
   - `image_url`: String(255), nullable.
   - `is_active`: Boolean, default=True.
   - `created_at`: DateTime, default=datetime.utcnow.

3. **`departures`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `tour_id`: Integer, ForeignKey('tours.id'), not null.
   - `departure_date`: Date, not null.
   - `return_date`: Date, not null.
   - `total_seats`: Integer, not null.
   - `available_slots`: Integer, not null.
   - `price_override`: Integer, nullable (Giá ưu đãi nếu có, tính bằng VNĐ).
   - `status`: String(20), default='OPEN' (Giá trị: `OPEN`, `FULL`, `RUNNING`, `COMPLETED`, `CANCELLED`).
   - `notes`: Text, nullable.
   - `created_at`: DateTime, default=datetime.utcnow.

4. **`customers`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `full_name`: String(100), not null.
   - `phone`: String(20), Unique, index, not null.
   - `email`: String(100), index, nullable.
   - `id_card`: String(25), nullable.
   - `address`: String(255), nullable.
   - `notes`: Text, nullable.
   - `created_at`: DateTime, default=datetime.utcnow.

5. **`bookings`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `booking_code`: String(40), Unique, index, not null (ví dụ: `VJ-202610-8912`).
   - `access_token`: String(64), Unique, index, not null.
   - `departure_id`: Integer, ForeignKey('departures.id'), not null.
   - `customer_id`: Integer, ForeignKey('customers.id'), not null.
   - `num_people`: Integer, not null.
   - `total_amount`: Integer, not null (VNĐ).
   - `deposit_amount`: Integer, not null (Chuẩn hóa đúng 30% total_amount).
   - `paid_amount`: Integer, default=0 (VNĐ).
   - `refund_amount`: Integer, default=0 (VNĐ).
   - `status`: String(30), default='WAITING_CONFIRM' (Hỗ trợ: `WAITING_CONFIRM`, `PENDING`, `DEPOSITED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`, `REJECTED`).
   - `cancellation_reason`: Text, nullable.
   - `special_requests`: Text, nullable.
   - `created_at`: DateTime, default=datetime.utcnow.
   - `updated_at`: DateTime, default=datetime.utcnow, onupdate=datetime.utcnow.

6. **`payments`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `booking_id`: Integer, ForeignKey('bookings.id'), not null.
   - `transaction_code`: String(60), Unique, index, not null.
   - `payment_type`: String(20), not null (`DEPOSIT`, `FINAL`, `FULL`, `REFUND`).
   - `amount`: Integer, not null (VNĐ).
   - `payment_method`: String(30), default='BANK_TRANSFER' (Hỗ trợ: `BANK_TRANSFER`, `VIETQR`, `CASH`, `CREDIT_CARD`).
   - `status`: String(20), default='SUCCESS'.
   - `note`: Text, nullable.
   - `created_by`: String(50), nullable.
   - `created_at`: DateTime, default=datetime.utcnow.

7. **`guides`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `guide_code`: String(30), Unique, index, not null.
   - `full_name`: String(100), not null.
   - `phone`: String(20), not null.
   - `email`: String(100), nullable.
   - `languages`: String(100), default='Tiếng Việt'.
   - `experience_years`: Integer, default=1.
   - `rating`: Float, default=5.0.
   - `status`: String(20), default='AVAILABLE' (`AVAILABLE`, `ON_TOUR`, `OFF`).
   - `notes`: Text, nullable.

8. **`tour_guides`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `departure_id`: Integer, ForeignKey('departures.id'), not null.
   - `guide_id`: Integer, ForeignKey('guides.id'), not null.
   - `assigned_role`: String(50), default='LEAD_GUIDE'.
   - `assigned_at`: DateTime, default=datetime.utcnow.

9. **`feedbacks`**:
   - `id`: Integer, Primary Key, autoincrement.
   - `booking_id`: Integer, ForeignKey('bookings.id'), not null.
   - `customer_id`: Integer, ForeignKey('customers.id'), not null.
   - `rating`: Integer, not null (1 đến 5 sao).
   - `guide_rating`: Integer, nullable (1 đến 5 sao).
   - `comments`: Text, not null.
   - `ai_sentiment`: String(20), default='NEUTRAL' (`POSITIVE`, `NEUTRAL`, `NEGATIVE`).
   - `created_at`: DateTime, default=datetime.utcnow.

---

### YÊU CẦU FILE ĐẦU RA (OUTPUT DELIVERABLES):

Hãy xuất ra mã nguồn Python hoàn chỉnh và chuẩn mực cho 3 file sau:

1. **`backend/app/database.py`**:
   - Cấu hình SQLAlchemy `create_engine`, `sessionmaker(autocommit=False, autoflush=False)`.
   - Kết nối SQLite mặc định với cờ `check_same_thread=False` và hỗ trợ biến môi trường `DATABASE_URL` cho MySQL.
   - Khởi tạo `Base = declarative_base()`.
   - Cung cấp hàm generator dependency `get_db()`.

2. **`backend/app/models.py`**:
   - Định nghĩa đầy đủ 9 Class Models tương ứng với 9 bảng trên.
   - Khai báo đầy đủ quan hệ hai chiều `relationship(..., back_populates=...)`.

3. **`backend/app/seed_data.py`**:
   - Khởi tạo dữ liệu mẫu thực tế tại Việt Nam:
     - 3 tài khoản mẫu với mật khẩu đã băm: `admin` (`admin123`), `tuvan` (`tuvan123`), `ketoan` (`ketoan123`).
     - Ít nhất 6 tour du lịch nổi tiếng: Phú Quốc, Sapa - Fansipan, Đà Nẵng - Hội An, Miền Tây sông nước, Nha Trang, Vịnh Hạ Long.
     - Ít nhất 4 hướng dẫn viên chuyên nghiệp.
     - Ít nhất 10 đợt khởi hành trải dài trong tháng tới.
     - Đơn booking mẫu ở các trạng thái khác nhau (`WAITING_CONFIRM`, `PENDING`, `DEPOSITED`, `CONFIRMED`) và các feedbacks đánh giá thực tế.

