# ĐẶC TẢ YÊU CẦU BÀI TOÁN & TỔNG QUAN HỆ THỐNG VIETJOURNEY AI
## (SYSTEM REQUIREMENTS SPECIFICATION & PROBLEM STATEMENT)

---

## 1. Mô Tả Bài Toán & Bối Cảnh Thực Tế

Trong ngành du lịch lữ hành, các công ty vừa và nhỏ (SMEs) thường gặp phải các vấn đề vận hành nghiêm trọng:
1. **Kiểm soát chỗ ngồi thủ công**: Quản lý lịch khởi hành bằng Excel hoặc sổ sách dễ dẫn đến sự cố **bán vượt số chỗ (Overbooking)** hoặc thông tin sai lệch giữa nhân viên tư vấn và khách hàng.
2. **Tư vấn chậm trễ**: Khách hàng cần được tư vấn tour phù hợp với ngân sách, thời gian rảnh và sở thích cá nhân, nhưng nhân viên tư vấn thường quá tải vào giờ cao điểm hoặc ngoài giờ hành chính.
3. **Mất nhiều thời gian biên soạn nội dung**: Nhân viên kinh doanh tốn hàng giờ đồng hồ để viết bài mô tả quảng bá, nghĩ câu slogan và lập lịch trình tóm tắt cho từng tour mới mở bán.
4. **Tranh chấp cọc và hoàn hủy**: Thiếu quy trình tự động hóa cho chính sách đặt cọc (30%) và hoàn hủy bậc thang, gây nhầm lẫn công nợ kế toán.
5. **Đánh giá sau tour bị bỏ quên**: Phản hồi của khách hàng sau chuyến đi không được tổng hợp, phân tích kịp thời để cải thiện chất lượng phục vụ.

**Hệ thống VietJourney AI** được thiết kế nhằm giải quyết triệt để các bài toán trên thông qua việc số hóa toàn diện quy trình lữ hành và tích hợp trí tuệ nhân tạo (GenAI) có kiểm soát chặt chẽ.

---

## 2. Mục Tiêu Dự Án

- **Vận hành thương mại chuẩn xác**: Quản trị danh mục tour, lịch khởi hành, khách hàng, vòng đời đơn đặt chỗ, kế toán thu chi và phân công hướng dẫn viên.
- **Tích hợp Trí tuệ Nhân tạo thực tế (Compound AI System)**:
  - Trợ lý AI tư vấn tour 24/7 có ràng buộc CSDL (Grounding), chống bịa giá, bịa lịch khởi hành (Anti-Hallucination).
  - Tự động sinh mô tả tour và timeline lịch trình chuẩn SEO định dạng JSON có cấu trúc.
  - Phân tích cảm xúc và tổng hợp chất lượng dịch vụ từ phản hồi thực tế của khách hàng.
- **Áp dụng AI trong toàn bộ vòng đời phát triển phần mềm (GenAI SDLC)**:
  - Khảo sát & Phân tích yêu cầu (KT1).
  - Thiết kế CSDL & Xây dựng nghiệp vụ backend (KT2).
  - Prompt Engineering, Chống ảo giác & Kiểm thử tự động (KT3).
  - Đóng gói tài liệu, báo cáo nghiệm thu và triển khai thực tế (Cuối kỳ).

---

## 3. Danh Sách Yêu Cầu Chức Năng (Functional Requirements)

### 3.1. Các Phân Hệ Quản Trị Nghiệp Vụ Cốt Lõi (8 Modules)

1. **Module 1: Đăng Nhập & Phân Quyền Vai Trò (RBAC)**:
   - Hỗ trợ các vai trò: Quản trị viên (`ADMIN`), Nhân viên tư vấn (`CONSULTANT`), Kế toán (`ACCOUNTANT`), Hướng dẫn viên (`GUIDE`).
   - Xác thực an toàn bằng JWT Bearer Token, băm mật khẩu với salt ngẫu nhiên (PBKDF2/bcrypt).
   - Có cơ chế Quick Role Switcher để phục vụ kiểm thử và demo nhanh.

2. **Module 2: Quản Lý Tour & Điểm Đến**:
   - Quản lý mã tour duy nhất, tiêu đề, điểm đến, phân loại, thời lượng (ngày/đêm), giá sàn (`base_price`), điểm nhấn (`highlights`) và hình ảnh.
   - Hỗ trợ tìm kiếm đa trường: theo tên tour, điểm đến, mã tour, phân loại.

3. **Module 3: Quản Lý Lịch Khởi Hành & Chỗ Trống (Departures)**:
   - Thiết lập ngày đi, ngày về, tổng số chỗ (`total_seats`), giá điều chỉnh (`price_override`).
   - Quản lý số chỗ còn lại (`available_slots`) thời gian thực với khóa giao dịch nguyên khối (Atomic Transaction), tự động chuyển trạng thái `FULL` khi hết chỗ.

4. **Module 4: Quản Lý Khách Hàng & Đơn Đặt Chỗ (Bookings)**:
   - Tiếp nhận khách vãng lai qua form đặt tour nhanh: Đưa vào hàng chờ `WAITING_CONFIRM` (chưa trừ chỗ).
   - Tư vấn viên duyệt yêu cầu: Hệ thống trừ chỗ thực tế và chuyển sang `PENDING`.
   - Sinh mã đơn hàng ngẫu nhiên (`booking_code`) và token bảo mật (`access_token`) phục vụ tính năng **Magic Link** cho khách tự tra cứu đơn hàng mà không cần đăng nhập.

5. **Module 5: Kế Toán Thu Chi, Đặt Cọc & Hoàn Hủy**:
   - **Quy tắc cọc 30%**: Bắt buộc đóng tối thiểu 30% tổng tiền đơn tour để giữ chỗ chắc chắn (`DEPOSITED`).
   - **Tích hợp VietQR**: Tự động sinh mã QR chuyển khoản ngân hàng gắn liền với nội dung thanh toán mã đơn hàng.
   - **Chính sách hoàn tiền bậc thang**:
     - Hủy trước $\ge 15$ ngày: Hoàn 100% số tiền đã đóng.
     - Hủy trước từ $7$ đến $14$ ngày: Hoàn 70% số tiền đã đóng.
     - Hủy trước từ $3$ đến $6$ ngày: Hoàn 50% số tiền đã đóng.
     - Hủy dưới $3$ ngày: Hoàn 0 VNĐ.
     - Tự động cộng lại số chỗ trống cho đợt khởi hành sau khi hủy.

6. **Module 6: Quản Lý Hướng Dẫn Viên & Chống Trùng Lịch**:
   - Quản lý hồ sơ HDV, ngoại ngữ, năm kinh nghiệm, đánh giá sao.
   - Khi phân công HDV cho đợt khởi hành, hệ thống tự động kiểm tra giao thoa ngày đi và ngày về; chặn đứng và cảnh báo nếu HDV đã có lịch tour trùng lặp.

7. **Module 7: Thu Thập & Đánh Giá Phản Hồi Sau Tour**:
   - Tiếp nhận nhận xét và chấm điểm dịch vụ (1 - 5 sao) của khách hàng sau khi hoàn thành chuyến đi.
   - Hỗ trợ khách gửi phản hồi trực tiếp qua Magic Link tra cứu đơn tour.

8. **Module 8: Thống Kê & Phân Tích KPI Doanh Thu**:
   - Bảng điều khiển (Dashboard) KPI trực quan: Doanh thu thực tế, doanh thu dự tính, tỷ lệ lấp đầy chỗ (Occupancy Rate), đơn chờ duyệt, đánh giá trung bình.
   - Biểu đồ Chart.js trực quan hóa doanh thu theo tháng và Top các tour bán chạy nhất.

---

### 3.2. Bộ 3 Tính Năng Trí Tuệ Nhân Tạo (AI Features)

1. **AI Feature 1: Trợ Lý Tư Vấn Tour Grounded CSDL (Tour Consultation Chatbot)**:
   - **Nguyên lý Grounding**: AI chỉ được tư vấn dựa trên danh sách các tour CÒN CHỖ VÀ ĐANG MỞ BÁN được trích xuất thời gian thực từ CSDL.
   - **Chống ảo giác (Anti-Hallucination)**: Tuyệt đối không tự bịa giá vé, ngày khởi hành hoặc địa điểm không có trong CSDL.
   - **Trích xuất thông minh**: Phản hồi kèm danh sách mã ID tour để giao diện hiển thị các thẻ tour tương tác bấm "Đặt chỗ ngay".
   - **Fallback Engine**: Nếu mất kết nối Internet hoặc không có API Key, hệ thống tự kích hoạt thuật toán heuristic nội bộ bằng Python để lọc tour theo ngân sách mà không bao giờ báo lỗi hệ thống.

2. **AI Feature 2: Tự Động Sinh Nội Dung Tour & Lịch Trình (Tour Content Generator)**:
   - Tiếp nhận thông số tour cơ bản (tên, điểm đến, số ngày, điểm nhấn).
   - Tự động sinh tiêu đề quảng cáo chuẩn SEO, câu slogan truyền cảm hứng, bài mô tả chi tiết và timeline lịch trình từng ngày.
   - Định dạng đầu ra JSON nghiêm ngặt, có bộ lọc Regex bóc tách an toàn xử lý cả trường hợp LLM bọc markdown codeblock.

3. **AI Feature 3: Phân Tích Cảm Xúc & Chất Lượng Dịch Vụ (Feedback Quality Analytics)**:
   - Đọc toàn bộ phản hồi từ khách hàng, phân loại tỷ lệ tích cực/tiêu cực/trung lập.
   - Tổng hợp Top 3 điểm khách hài lòng nhất và Top các điểm cần cải thiện ngay, đưa ra khuyến nghị thực tế cho Giám đốc điều hành.

---

## 4. Yêu Cầu Kỹ Thuật Cốt Lõi (Technical Constraints)

- **Ngôn ngữ & Nền tảng**: Python 3.10+ (Backend), HTML5/CSS3/Vanilla JavaScript ES6+ (Frontend).
- **Backend Framework**: **FastAPI** hiệu năng cao, tài liệu hóa tự động qua Swagger UI (`/docs`).
- **ORM & CSDL**: **SQLAlchemy 2.0**. Mặc định sử dụng SQLite 3 (`tour_management.db`) cho môi trường phát triển/kiểm thử cục bộ; sẵn sàng chuyển đổi MySQL 8.0+ cho production.
- **Quy chuẩn Tiền tệ**: Bắt buộc lưu trữ dưới dạng **Số nguyên VNĐ** hoặc `DECIMAL(18,0)`, tuyệt đối không dùng số thực `FLOAT` để tránh sai số kế toán.
- **AI Model**: **Google Gemini 2.5 Flash** (thông qua Google GenAI SDK) kết hợp Fallback Heuristics.
- **Frontend Architecture**: Single Page Application (SPA), Dark Mode / Light Mode, tương thích Responsive Mobile (360px, 390px, 768px) và Desktop.
- **Bảo mật**:
  - Không lộ ID/dữ liệu nhạy cảm của khách hàng qua endpoint công khai.
  - Sử dụng DOMPurify lọc sạch mã độc XSS trước khi chèn HTML động.
  - Chống Directory Traversal trên route tĩnh.
  - Chống tấn công gửi yêu cầu trùng lặp (Double-submission Prevention).
- **Kiểm thử tự động**: 100% các ca kiểm thử nghiệp vụ then chốt (ít nhất 40+ tests) phải vượt qua bằng **Pytest**.

