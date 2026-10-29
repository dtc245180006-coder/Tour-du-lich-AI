# Kiến Trúc Hệ Thống VietJourney AI (ARCHITECTURE.md)

VietJourney AI được xây dựng theo mô hình **Compound AI System (Hệ thống AI Phức hợp)** kết hợp giữa ứng dụng Web quản lý nghiệp vụ lữ hành truyền thống và Trợ lý Trí tuệ Nhân tạo hỗ trợ tư vấn, vận hành.

---

## 1. Sơ Đồ Kiến Trúc Tổng Thể

```mermaid
flowchart TD
    User["Khách Hàng / Nhân Viên / Quản Trị Viên"] --> Browser["Giao diện Trình duyệt (SPA Frontend)"]

    subgraph ClientLayer["Tầng Giao Diện (Frontend)"]
        Browser --> Pages["HTML5 Templates (Home, Bookings, AI, Tours, Admin)"]
        Browser --> AppJS["Frontend Controller (app.js)"]
        Browser --> Vendor["Local Vendor Assets (TailwindCSS, Chart.js, Lucide)"]
    end

    subgraph APILayer["Tầng Dịch Vụ & API (FastAPI Backend)"]
        AppJS <--> Gateway["FastAPI Server (Port 8000)"]
        Gateway --> AuthMiddleware["JWT Auth & Role-Based Access Control"]
        Gateway --> Routers["API Routers (Tours, Bookings, Payments, AI, Guides)"]
        Routers --> CRUD["Core Business Logic (crud.py)"]
    end

    subgraph ProcessingLayer["Tầng Xử Lý Nghiệp Vụ & Nền"]
        CRUD --> TransactionMgr["SQLAlchemy ORM (Unit of Work, Transactional)"]
        CRUD --> EmailSvc["Email Service (Background Thread, RFC Compliant)"]
        Routers --> AIAssistant["AI Assistant Service (Gemini API / Rule-based Fallback)"]
    end

    subgraph PersistenceLayer["Tầng Dữ Liệu & Bên Thứ Ba"]
        TransactionMgr <--> DB[("Cơ Sở Dữ Liệu\n(SQLite / MySQL)")]
        EmailSvc --> SMTP["Google SMTP Server (smtp.gmail.com:587)"]
        EmailSvc -.-> VietQR["VietQR API (img.vietqr.io)"]
        AIAssistant <--> Gemini["Google Gemini Flash API"]
    end
```

---

## 2. Luồng Nghiệp Vụ Đặt Tour & Thanh Toán Cọc (Booking & Deposit Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Guest as Khách Hàng (Chưa Đăng Nhập)
    participant Web as Web Frontend (Home/Tracking)
    participant API as FastAPI Backend
    participant DB as Database (SQLite/MySQL)
    participant SMTP as Google SMTP Service
    actor Staff as Tư Vấn Viên / Kế Toán

    Guest->>Web: Điền thông tin đặt tour (Tên, SĐT, Email, Số chỗ)
    Web->>API: POST /api/v1/bookings/guest
    API->>DB: Lưu đơn hàng (Trạng thái: WAITING_CONFIRM, Sinh access_token)
    API-->>Web: Trả về mã đơn (ví dụ: REQ-20261029-XXXX)
    
    Note over Staff,API: Tư vấn viên liên hệ xác nhận & duyệt đơn
    Staff->>API: POST /api/v1/bookings/{id}/confirm
    API->>DB: Trừ chỗ available_slots, chuyển sang PENDING (chờ cọc)
    API->>SMTP: Bắn email xác nhận + VietQR cọc 30% + Magic Link tra cứu
    SMTP-->>Guest: Email đến hòm thư khách hàng
    
    Guest->>Web: Bấm vào Magic Link trong email (?track_code=...&token=...)
    Web->>API: GET /api/v1/bookings/magic-track?code=...&token=...
    API-->>Web: Trả về hóa đơn chi tiết, mã VietQR cọc & tiến độ thanh toán
    
    Guest->>Staff: Khách quét QR chuyển khoản MB Bank
    Staff->>API: POST /api/v1/payments (Ghi nhận thanh toán)
    API->>DB: Cập nhật paid_amount, chuyển sang DEPOSITED hoặc CONFIRMED
    API->>SMTP: Bắn email biên lai thanh toán tự động đến khách hàng
```

---

## 3. Các Phân Hệ Dữ Liệu Chính

| Bảng dữ liệu | Mục đích | Ràng buộc chính |
| :--- | :--- | :--- |
| **`tours`** | Danh mục tuyến tour | `code` UNIQUE, `base_price` >= 0 |
| **`departures`** | Lịch khởi hành theo ngày | `available_slots` <= `total_seats`, trạng thái `OPEN / FULL / RUNNING / COMPLETED / CANCELLED` |
| **`customers`** | Hồ sơ khách hàng | `phone` UNIQUE, tự động cập nhật `email` và `full_name` khi đặt tour mới |
| **`bookings`** | Đơn đặt tour | `booking_code` UNIQUE, `access_token` UNIQUE 64-char dùng cho Magic Link, `deposit_amount` = 30% |
| **`payments`** | Sổ cái thanh toán | `amount` > 0, `transaction_code` UNIQUE per booking |
| **`users`** | Tài khoản nhân sự | Mật khẩu hash bcrypt, phân quyền `admin / consultant / accountant / guide` |
