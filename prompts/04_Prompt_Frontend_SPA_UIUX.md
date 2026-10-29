# PROMPT 04: XÂY DỰNG GIAO DIỆN NGƯỜI DÙNG SINGLE PAGE APPLICATION (SPA)
## (VANILLA JAVASCRIPT, MODERN DARK/LIGHT THEME, MAGIC LINK & XSS DEFENSE)

---

### BỐI CẢNH & VAI TRÒ CỦA AI:
Bạn là **Chuyên Gia Thiết Kế Giao Diện & Kỹ Sư Frontend Cấp Cao (Senior UI/UX & Frontend Engineer)**.
Nhiệm vụ của bạn là xây dựng toàn bộ hệ thống giao diện Web tương tác cho VietJourney AI theo phong cách Cổng thông tin điều hành (Smart Travel Portal / Dark-Light Theme), tối ưu trải nghiệm người dùng, mượt mà và an toàn tuyệt đối.

---

### NGUYÊN TẮC CÔNG NGHỆ & THIẾT KẾ:

1. **Kiến Trúc Không Phụ Thuộc Framework (Zero-Heavy-Framework)**:
   - Sử dụng **HTML5 ngữ nghĩa**, **CSS3 hiện đại** (CSS Variables, Flexbox, Grid, Glassmorphism) và **JavaScript ES6+ thuần** (Fetch API, async/await, Custom Events).
   - Tự động định tuyến điều hướng mượt mà, chuyển trang không cần tải lại toàn bộ trình duyệt (SPA Navigation).

2. **Hệ Thống Giao Diện Dark / Light Mode Thời Thượng**:
   - Mặc định nền tối công nghệ cao (`#0f172a` / `#1e293b`), viền mảnh tinh tế (`border-slate-800`), gradient ánh sáng Neon Cyan (`#38bdf8`) và Emerald (`#10b981`).
   - Có công tắc chuyển đổi Dark / Light Mode mượt mà lưu trạng thái vào `localStorage`.

3. **Cơ Chế Quick Role Switcher (Chuyển Vai Trò Tức Thì Phục Vụ Demo)**:
   - Trên đầu thanh Sidebar, bố trí thanh chuyển đổi nhanh 3 vai trò:
     - **Quản Trị Viên (Admin)**: Toàn quyền truy cập mọi tính năng, biểu đồ doanh thu và phân tích AI.
     - **Tư Vấn Viên (Consultant)**: Quản lý tour, duyệt hàng chờ khách vãng lai, tạo đơn tour.
     - **Kế Toán (Accountant)**: Ghi nhận thanh toán, xử lý hoàn tiền hủy tour, theo dõi quỹ.
   - Bấm vào icon vai trò nào sẽ cập nhật ngay Token / Role tương ứng mà không cần phải gõ form đăng nhập thủ công.

4. **Thanh Tiến Trình Lấp Đầy Chỗ Linh Hoạt (Seat Occupancy Bar)**:
   - Trên mỗi thẻ tour và bảng lịch khởi hành, hiển thị thanh tiến trình trực quan:
     - **Xanh lá cây** khi tỷ lệ lấp đầy $< 60\%$.
     - **Màu cam cảnh báo** khi tỷ lệ lấp đầy từ $60\% - 90\%$.
     - **Màu đỏ Neon nhấp nháy kèm chữ "GẦN KÍN / HẾT CHỖ"** khi tỷ lệ $\ge 90\%$.

5. **Phân Hệ Tra Cứu Đơn Tour Bằng Magic Link (`tracking.html`)**:
   - Khách hàng không cần đăng ký tài khoản. Khi đặt tour thành công, hệ thống gửi email chứa Magic Link: `http://localhost:8000/tracking.html?token=<ACCESS_TOKEN>`.
   - Trang này tự động đọc token từ URL, gọi API `/api/bookings/track/{access_token}`, hiển thị chi tiết hành trình, mã QR VietQR để thanh toán và form gửi đánh giá sau tour.

6. **Phòng Vệ Bảo Mật Giao Diện (UI Security & Robustness)**:
   - **Chống Stored XSS**: Tích hợp thư viện **DOMPurify** cục bộ để làm sạch toàn bộ dữ liệu phản hồi từ người dùng (nhận xét, ghi chú) trước khi hiển thị ra màn hình.
   - **Chống gửi đúp (Double-submission)**: Mọi nút bấm Submit (Đặt tour, Thanh toán, Duyệt đơn) phải tự động vô hiệu hóa (`btn.disabled = true`) và hiển thị biểu tượng Loading spinner trong lúc chờ Backend phản hồi.
   - **Xử lý Modal chuẩn chỉ**: Bấm phím `Escape` hoặc click ra ngoài vùng backdrop phải tự đóng modal và khôi phục thanh cuộn `document.body.style.overflow = 'auto'`.

---

### DANH SÁCH CÁC TRANG & MÀN HÌNH CẦN XÂY DỰNG:

1. **`home.html` (Cổng Thông Tin Du Khách)**:
   - Banner hero quảng bá du lịch Việt Nam kèm thanh tìm kiếm tour nhanh.
   - Lưới danh sách tour nổi bật với giá sàn và điểm nhấn.
   - Modal đặt tour nhanh cho khách vãng lai (nhập tên, SĐT, số khách, chọn ngày đi) đưa vào hàng chờ duyệt.
2. **`index.html` (Dashboard Tổng Quan Quản Trị)**:
   - 4 KPI cards: Doanh thu thực tế, Doanh thu dự kiến, Đơn chờ duyệt, Tỷ lệ lấp đầy ghế.
   - Bảng 5 đơn đặt chỗ mới nhất và 5 đợt khởi hành sắp tới.
3. **`tours.html` (Quản Lý Danh Mục Tour)**:
   - Bảng danh sách tour, tìm kiếm lọc theo điểm đến.
   - Modal thêm/sửa tour có nút **"Dán từ AI"** (Tự động điền mô tả, slogan và lịch trình do AI sinh ra).
4. **`departures.html` (Quản Lý Lịch Khởi Hành & Phân Bổ Ghế)**:
   - Quản lý ngày đi, ngày về, tổng ghế, chỗ còn trống, chọn hướng dẫn viên phụ trách.
5. **`queue.html` (Hàng Chờ Duyệt Yêu Cầu Khách Vãng Lai)**:
   - Hiển thị danh sách các đơn `WAITING_CONFIRM` kèm badge đỏ đếm số lượng trên menu.
   - Nút hành động: "Duyệt giữ chỗ" (gọi API trừ chỗ) hoặc "Từ chối" (nhập lý do).
6. **`bookings.html` (Quản Lý Vòng Đời Đơn Đặt Tour)**:
   - Danh sách đơn hàng với đầy đủ bộ lọc trạng thái.
   - Modal "Thu tiền / Xác nhận cọc": Nhập số tiền, phương thức, tự động tính dư nợ.
   - Modal "Hủy tour": Tự động tính số ngày còn lại và hiển thị số tiền hoàn theo chính sách bậc thang.
7. **`payments.html` (Sổ Nhật Ký Kế Toán)**:
   - Bảng kê các giao dịch cọc, thanh toán đủ và hoàn tiền.
8. **`guides.html` (Quản Lý Hướng Dẫn Viên)**:
   - Danh sách HDV, ngoại ngữ, đánh giá sao, trạng thái đang rảnh hoặc đang đi tour.
9. **`feedbacks.html` (Quản Lý Phản Hồi Khách Hàng)**:
   - Danh sách nhận xét của khách sau chuyến đi kèm nhãn cảm xúc AI (Tích cực/Tiêu cực).
10. **`ai.html` (Trung Tâm Trí Tuệ Nhân Tạo AI Hub)**:
    - Tab 1: Khung Chatbot tư vấn tour trực tiếp (Gợi ý các thẻ tour bấm "Đặt ngay").
    - Tab 2: Công cụ AI sinh nội dung bài viết và lịch trình tour.
    - Tab 3: Bảng phân tích cảm xúc phản hồi và đề xuất cải tiến dịch vụ.
11. **`analytics.html` (Biểu Đồ Doanh Thu & Thống Kê)**:
    - Biểu đồ cột Chart.js thể hiện doanh thu theo tháng và Top các tour đắt khách nhất.
12. **`tracking.html` (Cổng Tra Cứu Đơn Tour Magic Link)**:
    - Tra cứu tiến độ đơn, xem mã VietQR và gửi feedback.

---

### YÊU CẦU FILE ĐẦU RA (OUTPUT DELIVERABLES):

Hãy xuất ra mã nguồn hoàn chỉnh cho:
- **`frontend/css/style.css`**: Hệ thống biến màu, utility classes, Glassmorphism, Modal, Toast animation.
- **`frontend/js/app.js`**: Core Controller xử lý định tuyến SPA, xác thực JWT, gọi API, quản lý Modal, Quick Role Switcher và DOMPurify.
- **`frontend/js/ai_hub.js`**: Logic giao tiếp Chatbot tư vấn, sinh nội dung và vẽ biểu đồ cảm xúc.
- Toàn bộ các trang HTML độc lập hoạt động kết nối với API Backend (`http://localhost:8000/api/...`).

