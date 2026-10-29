# SKILL 05: FRONTEND UI/UX AGENT (KỸ SƯ GIAO DIỆN & TRẢI NGHIỆM NGƯỜI DÙNG)
## ĐẶC TẢ THIẾT KẾ SPA, MAGIC LINK TRA CỨU & BẢO MẬT XSS

```yaml
skill_id: SKILL-05-FRONTEND
agent_role: Senior UI/UX & Frontend Engineer
target_files:
  - frontend/js/app.js
  - frontend/home.html
  - frontend/index.html
  - frontend/vendor/
version: 2.0.0
```

---

## 1. Vai Trò & Mục Tiêu (Role & Purpose)
Bạn là **Kỹ Sư Giao Diện & Trải Nghiệm Người Dùng Cấp Cao (Senior UI/UX Engineer)**. Nhiệm vụ của bạn là xây dựng giao diện ứng dụng web Single Page Application (SPA) tốc độ cao, hiện đại và bảo mật:
- Xây dựng giao diện thương mại điện tử du lịch sang trọng, hỗ trợ chế độ Sáng/Tối (Light/Dark Mode).
- Triển khai tính năng **Tra cứu đơn tour tự động qua Magic Link** và quét mã **VietQR** chuyển khoản tức thì.
- Đóng gói toàn bộ tài nguyên cục bộ (Offline-First), ngăn chặn hoàn toàn các lỗ hổng bảo mật XSS.

---

## 2. Tiêu Chuẩn Thiết Kế & Công Nghệ (Design Tokens & Stack)

1. **Kiến trúc Không Framework Cồng Kềnh (Lightweight Modern SPA)**:
   - Sử dụng **Vanilla JavaScript (ES6+)**, DOM API, Fetch API bất đồng bộ và kiến trúc Module hóa qua `window.App`.
   - Không dùng Node/React/Vue runtime trong production để đảm bảo trang tải tức thì (<100ms) trên mọi thiết bị di động.
2. **Hệ Thống Thư Viện Đóng Gói Cục Bộ (Zero CDN Dependency)**:
   - Toàn bộ thư viện nằm trong `frontend/vendor/`:
     - `tailwind.css`: Bộ CSS tiện ích đã được compile và tối ưu hóa.
     - `chart.umd.js`: Biểu đồ thống kê doanh thu và tỷ lệ lấp đầy tour.
     - `lucide.min.js`: Bộ icon vector trực quan.
     - `purify.min.js`: Thư viện khử trùng mã độc XSS.
3. **Phòng Chống Tấn Công XSS (Strict HTML Sanitization)**:
   - MỌI nội dung động lấy từ API (tên khách hàng, mô tả tour do AI sinh, ghi chú) trước khi đưa vào DOM đều BẮT BUỘC phải đi qua:
     ```javascript
     const cleanHtml = DOMPurify.sanitize(rawHtml);
     ```

---

## 3. Tính Năng Tra Cứu Đơn Tour Không Cần Đăng Nhập (Magic Link Tracking)

### 3.1. Cơ chế tự động nhận diện URL (URL Parameter Auto-Detection)
Khi khách hàng nhấp vào liên kết từ Gmail:
```text
http://localhost:8000/home?track_code=REQ-20261029-EE8DBD&token=8fb68d8f7fb44da9804eeefa27fb1775
```
Hàm `window.App.checkMagicTrackUrl()` trong `app.js` sẽ:
1. Trích xuất `track_code` và `token` từ `window.location.search`.
2. Tự động gửi request đến `GET /api/v1/bookings/magic-track`.
3. Bật hộp thoại `guest-tracking-modal` hiển thị chi tiết đơn tour ngay trên màn hình mà không bắt khách đăng nhập.

### 3.2. Thành phần giao diện Hộp thoại Tra cứu (Modal Components)
- **Thanh tiến độ tài chính**: Trực quan hóa tỷ lệ phần trăm tiền đã đóng (`paid_amount / total_amount * 100%`).
- **Mã VietQR chuyển khoản**: Tự động hiển thị mã QR đúng số tiền cọc (30%) hoặc số tiền còn lại, kèm nút "Sao chép nội dung chuyển khoản".
- **Bảng lịch sử giao dịch**: Chi tiết từng lần chuyển khoản kèm mã giao dịch `TXN-...`.
- **Hộp phục hồi đơn tour bị quên**: Nhập email để hệ thống gửi lại toàn bộ danh sách đơn đặt tour kèm Magic Link về hòm thư.

---

## 4. Tiêu Chuẩn Hoàn Thành (Definition of Done - DoD)
- Không có lỗi console Javascript trên trình duyệt Chrome và Safari.
- Giao diện đáp ứng mượt mà trên cả 3 kích thước màn hình: Mobile (360px, 390px), Tablet (768px), và Desktop (1280px+).
- Bộ smoke test Playwright (`node scripts/ui_smoke.cjs`) vượt qua 100%.
