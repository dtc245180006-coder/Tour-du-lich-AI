# TÀI LIỆU KHẢO SÁT HIỆN TRẠNG & PHÂN TÍCH NHU CẦU NGƯỜI DÙNG
## HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)

---

## 1. Mục Đích & Phạm Vi Khảo Sát
- **Mục tiêu**: Thu thập yêu cầu thực tế, xác định các điểm nghẽn (Pain points) trong vận hành tour du lịch, đánh giá sự cần thiết và tính khả thi khi ứng dụng Trí tuệ Nhân tạo (AI).
- **Đối tượng khảo sát**:
  1. **Khách hàng (Du khách)**: Tìm kiếm tour, xem lịch trình, đặt chỗ, đặt cọc và để lại phản hồi.
  2. **Nhân viên tư vấn (Sales/Consultant)**: Tiếp nhận khách, tư vấn tour theo ngân sách, giữ chỗ.
  3. **Kế toán & Điều hành (Accountant/Operator)**: Thu cọc 30%, xử lý tất toán, hoàn tiền khi hủy tour.
  4. **Ban giám đốc (Admin/Manager)**: Theo dõi doanh thu, tỷ lệ lấp đầy ghế (Occupancy Rate), kiểm soát chất lượng dịch vụ.

---

## 2. Phương Pháp Khảo Sát Thực Hiện
1. **Khảo sát định lượng qua bảng hỏi trực tuyến (Google Forms)**:
   - 120 phiếu khảo sát từ khách du lịch.
   - 30 phiếu khảo sát từ nhân sự các công ty lữ hành vừa và nhỏ.
2. **Phỏng vấn sâu định tính (In-depth Interview)**:
   - Phỏng vấn Giám đốc điều hành, Trưởng phòng Sales, Kế toán trưởng, Hướng dẫn viên du lịch và Du khách thường xuyên.
3. **Quan sát thực tế quy trình nghiệp vụ (Observation)**:
   - Quan sát quy trình tiếp nhận thông tin, tra cứu chỗ trống trên file Excel/sổ sách, tạo booking, thu tiền cọc và thủ tục hủy tour hoàn cọc.

---

## 3. Kết Quả Khảo Sát & Các Điểm Nghẽn (Pain Points)

### 3.1. Đối với Khách Du Lịch
- gặp khó khăn trong việc tự tìm tour vừa vặn với ngân sách và số ngày nghỉ dự kiến.
-  bức xúc vì thông tin chỗ trống trên website không chính xác (bị thông báo hết chỗ sau khi đã chọn xong).
-  phàn nàn về tốc độ tư vấn chậm vào giờ cao điểm hoặc buổi tối.
-  mong muốn có trợ lý AI tư vấn tự động 24/7 theo đúng nhu cầu (ngân sách, số ngày, địa điểm).
-  yêu cầu chính sách đặt cọc (30%) và hoàn tiền khi hủy tour phải rõ ràng, minh bạch.

### 3.2. Đối với Doanh Nghiệp Lữ Hành
-  từng gặp sự cố bán vượt số chỗ cho phép (**Overbooking**) do kiểm soát số ghế thủ công bằng Excel.
-  nhân viên kinh doanh tốn từ 15 – 30 phút cho mỗi lượt tư vấn khách hàng.
-  nhân viên nội dung mất 2 – 3 tiếng để viết bài mô tả và tóm tắt lịch trình chi tiết cho mỗi tour mới.
-  gặp sai sót trong việc theo dõi tiền cọc 30% và tính toán tiền phạt/hoàn cọc khi khách hủy tour.
-  không đo lường được mức độ hài lòng (CSAT) do phản hồi sau tour bằng giấy hoặc tin nhắn không được tổng hợp tập trung.

---

## 4. Ma Trận Chuyển Hóa: Pain Points -> Tính Năng Hệ Thống

| Điểm nghẽn thực tế (Pain Point) | Nhu cầu người dùng | Giải pháp & Tính năng VietJourney AI |
| :--- | :--- | :--- |
| **Bán vượt số chỗ (Overbooking)** | Quản lý chỗ trống thời gian thực, chặn khi hết chỗ | **Quản lý lịch khởi hành với Atomic Booking**, trừ chỗ tự động, khóa khi đạt `max_slots`. |
| **Tư vấn tour lâu, thiếu thông tin** | Muốn được gợi ý tour nhanh theo ngân sách & ngày | **AI Chatbot Grounded CSDL**: Lọc tour CÒN CHỖ, gợi ý tối đa 3 tour phù hợp, bấm đặt ngay. |
| **Mất nhiều thời gian viết bài quảng bá** | Tự động hóa sáng tạo nội dung tour | **AI Content Generator**: Nhập thông số cơ bản -> Sinh bài viết quảng cáo, slogan và timeline lịch trình. |
| **Tranh chấp tiền cọc & hủy tour** | Chính sách cọc và hoàn hủy minh bạch | **Module Kế toán**: Thu cọc 30%, tính hoàn tiền lũy tiến tự động theo số ngày hủy (100% $\to$ 70% $\to$ 50% $\to$ 0%). |
| **Đánh giá sau tour bị bỏ quên** | Đo lường chất lượng dịch vụ & cải thiện tour | **AI Feedback Analytics**: Đọc đánh giá, phân loại cảm xúc tích cực/tiêu cực, đề xuất cải tiến cho Ban giám đốc. |

---

## 5. Kết Luận & Đánh Giá Tính Khả Thi
- **Tính khả thi Kỹ thuật**: Rất cao. Kiến trúc FastAPI + CSDL SQLite/MySQL + Trí tuệ nhân tạo Gemini 2.5 Flash / Fallback Engine đáp ứng hoàn hảo các yêu cầu trên.
- **Tính khả thi Vận hành**: Rất cao. Phù hợp chính xác với mô hình quản trị lữ hành thực tế.
- **Kết nối SDLC**: Kết quả khảo sát này là đầu vào trực tiếp cho:
  - Báo cáo **KT1** (Phân tích Yêu cầu & Thiết kế Hệ thống).
  - Báo cáo **KT2** (Xây dựng Nghiệp vụ & API Backend).
  - Báo cáo **KT3** (Thiết kế Prompt AI & Kiểm thử Chống ảo giác).
  - Báo cáo **Cuối Kỳ** (Tổng kết & Triển khai toàn diện).
