# VietJourney AI — Backend Architecture & API Service

Phân hệ Backend được xây dựng trên nền tảng **FastAPI** và **SQLAlchemy 2.0**, tuân thủ kiến trúc phân tầng (Layered Architecture) với các nguyên tắc Clean Code và tính toàn vẹn giao dịch cao.

---

## 1. Cấu Trúc Mã Nguồn

```
backend/
├── app/
│   ├── config.py          # Quản lý biến môi trường (.env) bằng Pydantic BaseSettings
│   ├── database.py        # Cấu hình SQLAlchemy Engine, SessionLocal và Base
│   ├── models.py          # Định nghĩa các bảng dữ liệu, khóa ngoại và quan hệ
│   ├── schemas.py         # Định nghĩa Pydantic Request/Response DTOs
│   ├── crud.py            # Logic nghiệp vụ cốt lõi (bọc decorator @_transactional)
│   ├── auth.py            # Xác thực JWT, băm mật khẩu bcrypt, RBAC middleware
│   ├── email_service.py   # Dịch vụ gửi email SMTP nền, sinh VietQR và Magic Link
│   ├── seed_data.py       # Dữ liệu mẫu (Tour, Lịch trình, Tài khoản demo)
│   ├── main.py            # Điểm khởi chạy ứng dụng FastAPI, đăng ký routers, CORS
│   └── routers/           # Các endpoint RESTful theo từng phân hệ nghiệp vụ
│       ├── auth_router.py       # Đăng nhập, cấp JWT token
│       ├── tour_router.py       # Quản lý danh mục tuyến tour
│       ├── departure_router.py  # Lịch khởi hành và quản lý số chỗ (slots)
│       ├── booking_router.py    # Đặt tour, duyệt chỗ, tra cứu Magic Link
│       ├── payment_router.py    # Ghi nhận thanh toán cọc và hoàn tất
│       ├── ai_router.py         # Trợ lý ảo tư vấn và phân tích dữ liệu
│       ├── guide_router.py      # Điều phối hướng dẫn viên du lịch
│       ├── feedback_router.py   # Đánh giá và khảo sát khách hàng
│       ├── stats_router.py      # Thống kê doanh thu và công nợ
│       └── user_router.py       # Quản trị người dùng nội bộ
└── tests/                 # Bộ kiểm thử tự động toàn diện (Pytest)
```

---

## 2. Hướng Dẫn Kiểm Thử Backend

Chạy toàn bộ test suites kiểm tra phân quyền, xử lý tiền tệ, đặt chỗ đồng thời và xác thực token:
```powershell
.venv\Scripts\python.exe -m pytest backend/tests -q
```
