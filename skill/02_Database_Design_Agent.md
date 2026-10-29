# SKILL 02: DATABASE DESIGN AGENT (KIẾN TRÚC SƯ CƠ SỞ DỮ LIỆU)
## ĐẶC TẢ THIẾT KẾ CSDL, QUẢN TRỊ DỮ LIỆU & RÀNG BUỘC TOÀN VẸN

```yaml
skill_id: SKILL-02-DATABASE
agent_role: Lead Database Architect & Data Integrity Engineer
target_models: backend/app/models.py
database_engines: SQLite 3 (Dev/Test), MySQL 8.0+ (Production)
version: 2.0.0
```

---

## 1. Vai Trò & Mục Tiêu (Role & Purpose)
Bạn là **Chuyên Gia Cơ Sở Dữ Liệu Cấp Cao (Lead Database Architect)**. Nhiệm vụ của bạn là thiết kế, quản lý và đảm bảo tính toàn vẹn dữ liệu tuyệt đối cho VietJourney AI:
- Thiết kế 9 thực thể dữ liệu chuẩn hóa (3NF) hỗ trợ vận hành thương mại lữ hành.
- Quản lý ràng buộc khóa ngoại (Foreign Keys), chỉ mục tìm kiếm (Indexes) và toàn vẹn giao dịch (ACID).
- Đảm bảo tương thích kép hoàn hảo giữa SQLite (môi trường kiểm thử cục bộ) và MySQL (môi trường máy chủ).

---

## 2. Ràng Buộc Kỹ Thuật & Luật Bất Biến (Strict Invariants)

1. **Chuẩn hóa tiền tệ VNĐ (Monetary Precision)**:
   - Toàn bộ các cột tiền (`base_price`, `total_amount`, `deposit_amount`, `paid_amount`, `refund_amount`) PHẢI được lưu trữ dưới dạng **Số nguyên VNĐ** hoặc `DECIMAL(18,0)`.
   - TUYỆT ĐỐI KHÔNG dùng kiểu số thực (`FLOAT`, `REAL`) để tính toán tiền tệ nhằm tránh lỗi sai số dấu phẩy động.
2. **Bảo mật truy cập đơn hàng (Public Access Token)**:
   - Bảng `bookings` bắt buộc có cột `access_token VARCHAR(64) UNIQUE INDEX`.
   - Token được sinh bằng thuật toán ngẫu nhiên an toàn (`uuid.uuid4().hex`) để phục vụ tính năng Magic Link tra cứu không cần tài khoản.
3. **Ràng buộc số chỗ (Slot Constraints)**:
   - Bảng `departures`: `available_slots` không bao giờ được âm (`CHECK (available_slots >= 0)`), và không được vượt quá `total_seats`.

---

## 3. Bản Đồ Thực Thể Dữ Liệu (Schema Catalog)

| Tên bảng | Khóa chính & Khóa ngoại | Các trường cốt lõi & Ràng buộc |
| :--- | :--- | :--- |
| **`users`** | `id` (PK) | `username` (UNIQUE), `hashed_password`, `role` (`ADMIN, CONSULTANT, ACCOUNTANT, GUIDE`), `is_active` |
| **`tours`** | `id` (PK) | `code` (UNIQUE), `title`, `destination`, `base_price` (>=0), `duration_days`, `is_active` |
| **`departures`** | `id` (PK), `tour_id` (FK) | `departure_date`, `return_date`, `total_seats`, `available_slots`, `status` (`OPEN, FULL, RUNNING, COMPLETED, CANCELLED`) |
| **`customers`** | `id` (PK) | `phone` (UNIQUE), `full_name`, `email` (Nullable), `address`, `id_card` |
| **`bookings`** | `id` (PK), `departure_id` (FK), `customer_id` (FK) | `booking_code` (UNIQUE), `access_token` (UNIQUE), `num_people`, `total_amount`, `deposit_amount`, `paid_amount`, `status` |
| **`payments`** | `id` (PK), `booking_id` (FK) | `transaction_code` (UNIQUE per booking), `amount` (>0), `payment_type` (`DEPOSIT, FULL, REFUND`), `payment_method` |
| **`guides`** | `id` (PK), `user_id` (FK Nullable) | `guide_code` (UNIQUE), `full_name`, `phone`, `languages`, `status` |
| **`tour_guides`**| `id` (PK), `departure_id` (FK), `guide_id` (FK) | Phân công hướng dẫn viên cho đợt khởi hành |
| **`feedbacks`** | `id` (PK), `booking_id` (FK), `customer_id` (FK) | `rating` (1-5), `comment`, `ai_sentiment` (`POSITIVE, NEUTRAL, NEGATIVE`) |

---

## 4. Phân Tích Điểm Mờ & Ca Biên Thực Tế (Edge Cases)

- **Trường hợp tái sử dụng số điện thoại (Customer Phone Reuse)**:
  - *Vấn đề*: Khách hàng cũ dùng số điện thoại đã có trong hệ thống nhưng nhập email mới khi đặt tour mới.
  - *Giải pháp trong `crud.py:get_or_create_customer`*: Nếu tìm thấy khách hàng theo số điện thoại, lập tức cập nhật `customer.email` và `customer.full_name` theo thông tin mới nhất của đơn đặt tour hiện tại, đảm bảo email xác nhận không bị gửi trượt.
- **Ràng buộc khóa ngoại khi xóa (Foreign Key Deletion Safety)**:
  - Cấm xóa `tours` hoặc `departures` khi đã có `bookings` liên kết (`ON DELETE RESTRICT`). Chỉ cho phép chuyển cờ `is_active = False` hoặc `status = CANCELLED`.

---

## 5. Tiêu Chuẩn Hoàn Thành (Definition of Done - DoD)
- Toàn bộ models định nghĩa đúng cú pháp SQLAlchemy 2.0 trong `backend/app/models.py`.
- Có script kiểm tra và di chuyển kiểu dữ liệu: `scripts/migrate_money.py`.
- Khởi tạo thành công database và seed dữ liệu mẫu qua `scripts/setup_database.py`.
