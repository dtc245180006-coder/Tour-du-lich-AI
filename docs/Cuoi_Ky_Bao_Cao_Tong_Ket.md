# BÁO CÁO TỔNG KẾT CUỐI KỲ DỰ ÁN
# HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)

---

## 1. TỔNG QUAN DỰ ÁN

Dự án **VietJourney AI** là giải pháp phần mềm quản lý điều hành tour du lịch hiện đại, tích hợp công nghệ Trí tuệ Nhân tạo thế hệ mới (Generative AI) vào toàn bộ vòng đời phát triển phần mềm (SDLC) và quy trình vận hành thực tế.

- **Đơn vị phát triển**: Nhóm nghiên cứu & ứng dụng AI Du lịch
- **Công nghệ chính**: 
  - Backend: **FastAPI** (Python 3.14), SQLAlchemy ORM, Pydantic v2, SQLite.
  - Frontend: Single-Page Application chuẩn Responsive, Tailwind CSS, FontAwesome 6, Chart.js.
  - AI Engine: Google Gemini 1.5 Flash / OpenAI / Local Grounded Rule Engine.

---

## 2. KẾT QUẢ ĐẠT ĐƯỢC ĐỐI CHIẾU VỚI YÊU CẦU

### 2.1. Nhóm Chức năng Quản lý (Đạt 100%)
1. **Đăng nhập & Phân quyền**: Đã xây dựng RBAC 3 vai trò: Quản lý (Admin), Nhân viên tư vấn (Consultant), Kế toán (Accountant), kèm tính năng chuyển đổi quyền nhanh (`Role Switcher`) trực tiếp trên thanh công cụ.
2. **Quản lý Tour & Lịch trình**: Quản lý điểm đến, thời lượng, bảng giá, mô tả và lịch trình chi tiết.
3. **Quản lý Lịch khởi hành & Số chỗ**: Giám sát thời gian thực số lượng ghế trống (`available_slots`), tự động khóa đợt đi khi hết chỗ (`FULL`).
4. **Quản lý Khách hàng & Đặt chỗ**: Đặt tour theo đoàn/khách lẻ, chống bán vượt số chỗ (**Overbooking**).
5. **Kế toán & Đặt cọc**: Theo dõi đặt cọc 30%, thanh toán đợt cuối và quy tắc hoàn tiền tự động theo số ngày hủy tour.
6. **Hướng dẫn viên**: Quản lý hồ sơ, kinh nghiệm, ngoại ngữ và phân công dẫn tour.
7. **Phản hồi du khách**: Thu thập review, đánh giá sao chất lượng dịch vụ và hướng dẫn viên.
8. **Thống kê báo cáo**: Biểu đồ doanh thu trực quan, đo lường tỷ lệ lấp đầy chỗ ngồi (Occupancy Rate).

### 2.2. Nhóm Chức năng AI (Đạt 100%)
1. **AI Tư vấn tour**: Chatbot tương tác tự nhiên, gợi ý tối đa 3 tour phù hợp với ngân sách, thời gian và sở thích của khách; **neo chặt dữ liệu thực tế** (grounded) vào các tour đang còn chỗ mở bán trong CSDL.
2. **AI Sinh mô tả & Lịch trình**: Tự động viết bài quảng bá cuốn hút, tạo slogan truyền thông và lịch trình chi tiết từng ngày, có nút chuyển trực tiếp nội dung vào Form thêm tour mới.
3. **AI Tóm tắt phản hồi**: Phân tích cảm xúc, trích xuất điểm nổi bật khách khen, điểm cần cải thiện và đưa ra đề xuất hành động cho ban giám đốc.

---

## 3. DÀN Ý SLIDE THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN (PRESENTATION SLIDES)

Dưới đây là dàn ý slide được chuẩn hóa sẵn sàng cho buổi báo cáo cuối kỳ:

- **Slide 1: Trang bìa**
  - Tên đề tài: "Hệ thống Quản lý Tour Du lịch có tích hợp AI - VietJourney AI"
  - Học viên / Nhóm thực hiện & Giảng viên hướng dẫn.
- **Slide 2: Đặt vấn đề & Mục tiêu**
  - Thực trạng: Xung đột overbooking, nhân viên quá tải tư vấn và viết nội dung tour.
  - Mục tiêu: Tự động hóa quản lý điều hành tour và tích hợp AI hỗ trợ người dùng.
- **Slide 3: Kiến trúc Hệ thống & Công nghệ**
  - Mô hình Client-Server: Frontend SPA + FastAPI RESTful Backend + SQLite.
  - Kiến trúc phân lớp: Router -> CRUD / Service -> Database / AI Engine.
- **Slide 4: Nghiệp vụ Cốt lõi & Xử lý Số chỗ**
  - Thuật toán trừ chỗ nguyên tử (Atomic Slot Decrement).
  - Chính sách hủy tour và tỷ lệ hoàn tiền tự động (100% - 70% - 50% - 0%).
- **Slide 5: Đột phá AI: Giải pháp Chống Ảo Giác (Anti-Hallucination)**
  - Phương pháp Grounded Prompting: Kẹp dữ liệu tour còn chỗ vào System Context.
  - Đảm bảo AI không tự bịa đặt giá hoặc lịch khởi hành ảo.
- **Slide 6: Minh họa Giao diện (Demo Live)**
  - Giao diện Dashboard hiện đại theo ảnh tham khảo.
  - Trải nghiệm Chatbot tư vấn, Đặt tour nhanh và Sinh mô tả tour 1 chạm.
- **Slide 7: Kết quả Kiểm thử & Đánh giá**
  - Bộ kiểm thử tự động `pytest`: 9/9 tests passed (100%).
- **Slide 8: Kết luận & Hướng phát triển**
  - Tích hợp cổng thanh toán VNPay/Momo tự động.
  - Mở rộng ứng dụng di động (Mobile App) cho Hướng dẫn viên điểm danh du khách.

---

## 4. HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH

### 4.1. Khởi động nhanh với 1 chạm (Windows)
Chỉ cần nhấp đúp chuột vào file `start.bat` tại thư mục gốc của dự án. File sẽ tự động kiểm tra thư viện và khởi chạy máy chủ FastAPI tại:
👉 **http://localhost:8000**

### 4.2. Khởi chạy bằng dòng lệnh
```powershell
# Di chuyển vào thư mục dự án
cd c:\Users\Admin\Desktop\pj\tourdulichAI

# Khởi chạy backend & frontend
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 4.3. Chạy kiểm thử tự động
```powershell
python -m pytest backend/tests -v
```

### 4.4. Tài khoản đăng nhập mẫu
| Vai trò | Tên đăng nhập | Mật khẩu | Chức năng chính |
|---|---|---|---|
| **Quản trị viên (Admin)** | `admin` | `admin123` | Toàn quyền cấu hình tour, xem thống kê doanh thu |
| **Tư vấn viên (Consultant)** | `tuvan` | `tuvan123` | Tư vấn AI, tạo booking, giữ chỗ |
| **Kế toán viên (Accountant)** | `ketoan` | `ketoan123` | Thu tiền cọc, xác nhận thanh toán, hoàn tiền hủy tour |
*(Lưu ý: Bạn cũng có thể dùng nút chuyển đổi quyền nhanh ngay trên giao diện Web mà không cần đăng xuất).*
