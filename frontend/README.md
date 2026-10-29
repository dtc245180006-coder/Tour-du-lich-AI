# VietJourney AI — Frontend Architecture & UI Components

Giao diện người dùng của VietJourney AI được thiết kế theo mô hình **Single Page Application (SPA)** hiện đại, không phụ thuộc vào các framework nặng (như React/Vue) để đảm bảo tốc độ tải tức thì (<100ms), dễ bảo trì và hoạt động ổn định hoàn toàn offline.

---

## 1. Cấu Trúc Mã Nguồn

```
frontend/
├── assets/            # Hình ảnh tĩnh và biểu tượng hệ thống
├── css/               # Tailwind input CSS và tùy biến giao diện
├── js/
│   └── app.js         # Client Controller chính (Quản lý State, Auth, API, Modals)
├── vendor/            # Thư viện đóng gói cục bộ chạy offline
│   ├── tailwind.css   # Bộ class CSS tiện ích đã được compile và tối ưu
│   ├── chart.umd.js   # Vẽ biểu đồ thống kê doanh thu và phân bổ tour
│   ├── lucide.min.js  # Hệ thống icon vector sắc nét
│   └── purify.min.js  # Khử trùng dữ liệu HTML đầu vào chống lỗi XSS
└── *.html             # Các trang nghiệp vụ
    ├── home.html      # Trang chủ khách hàng, banner tour, tra cứu đơn tour
    ├── index.html     # Cổng chuyển hướng hệ thống
    ├── tours.html     # Quản lý danh mục tour dành cho nhân viên
    ├── departures.html# Quản lý lịch khởi hành và giữ chỗ
    ├── bookings.html  # Quản lý đơn đặt tour và duyệt trạng thái
    ├── payments.html  # Sổ cái kế toán và lịch sử giao dịch
    ├── ai.html        # Trợ lý AI tư vấn và phân tích vận hành
    ├── analytics.html # Báo cáo số liệu kinh doanh
    ├── guides.html    # Danh sách và phân công hướng dẫn viên
    └── users.html     # Phân quyền nhân sự nội bộ
```

---

## 2. Các Tính Năng Nổi Bật

1. **Tra Cứu Đơn Tour Không Cần Đăng Nhập (Magic Link)**:
   - Khách hàng có thể tra cứu đơn hàng bằng Mã đơn + SĐT/Email hoặc nhấp trực tiếp vào liên kết được gửi về Gmail:
     `/home?track_code={code}&token={access_token}`.
   - Hộp thoại tra cứu tự động hiển thị tiến độ thanh toán cọc (30%), mã VietQR chuyển khoản nhanh và lịch sử đóng tiền.
2. **Bảo Mật Đầu Vào**:
   - Mọi nội dung hiển thị động từ API đều được lọc qua `DOMPurify.sanitize()` trước khi chèn vào DOM.
3. **Responsive & Offline-First**:
   - Giao diện tương thích hoàn toàn trên cả máy tính để bàn (Desktop) và điện thoại di động (Mobile). Toàn bộ thư viện đều nằm trong `vendor/`, không phụ thuộc vào CDN bên ngoài.
