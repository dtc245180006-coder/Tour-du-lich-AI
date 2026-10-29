# PROMPT 05: KIỂM THỬ TỰ ĐỘNG HÓA & TRUY VẤN XÁC MINH CSDL
## (PYTEST AUTOMATION SUITE, CONCURRENCY TESTS & SQL AUDIT QUERIES)

---

### BỐI CẢNH & VAI TRÒ CỦA AI:
Bạn là **Kỹ Sư Kiểm Thử Tự Động Hóa Cấp Cao (Lead QA & Test Automation Engineer)**.
Nhiệm vụ của bạn là xây dựng bộ kiểm thử tự động toàn diện bằng **Pytest** và **FastAPI TestClient** cho dự án VietJourney AI, đảm bảo đạt tỷ lệ **100% Passed** cho toàn bộ 48+ ca kiểm thử nghiệp vụ, bảo mật, đồng thời và tính toàn vẹn dữ liệu.

---

### DANH MỤC TEST CASES BẮT BUỘC PHẢI XÂY DỰNG:

#### 1. Nhóm Kiểm Thử Xác Thực & Phân Quyền Vai Trò (RBAC & Security)
- `test_admin_user_crud`: Kiểm tra Admin tạo, cập nhật, đổi mật khẩu và vô hiệu hóa tài khoản nhân viên.
- `test_consultant_cannot_modify_tours`: Đăng nhập vai trò `CONSULTANT` và gọi API sửa/xóa Tour -> Phải bị chặn với lỗi HTTP `403 Forbidden`.
- `test_consultant_cannot_modify_departures`: Kiểm tra Tư vấn viên không có quyền can thiệp giá sàn hoặc xóa lịch khởi hành của Admin.
- `test_guest_and_consultant_cannot_view_revenue`: Kiểm tra chỉ có `ADMIN` và `ACCOUNTANT` mới được xem thống kê doanh thu và quỹ kế toán.
- `test_file_handler_rejects_paths_outside_frontend`: Thử nghiệm tấn công Directory Traversal (`../.env`, `../../requirements.txt`) -> Phải bị chặn đứng với mã lỗi `403` hoặc `404`.
- `test_password_hashes_use_random_salts`: Kiểm tra mật khẩu được băm với salt ngẫu nhiên, không bị trùng chuỗi băm khi hai tài khoản dùng cùng mật khẩu.

#### 2. Nhóm Kiểm Thử Đặt Tour & Chống Bán Vượt Chỗ (Overbooking & Concurrency)
- `test_booking_reduces_available_slots`: Tạo chuyến 10 chỗ, đặt 3 chỗ -> Kiểm tra `available_slots` giảm chính xác về 7.
- `test_prevent_overbooking`:
  - Tạo chuyến có 5 chỗ trống.
  - Khách 1 đặt 4 chỗ -> Thành công, còn 1 chỗ.
  - Khách 2 cố tình đặt 2 chỗ -> Phải ném lỗi `400 Bad Request` ("Không đủ số lượng vé yêu cầu").
  - Khách 3 đặt đúng 1 chỗ -> Thành công, số chỗ còn 0 và trạng thái chuyến tự đổi thành `FULL`.
- `test_concurrent_booking_preserves_capacity`: Mô phỏng nhiều luồng (Threads) cùng lúc đặt chỗ cuối cùng của một chuyến đi -> Đảm bảo số chỗ còn lại không bao giờ bị âm (`available_slots >= 0`).

#### 3. Nhóm Kiểm Thử Hủy Tour & Chính Sách Hoàn Tiền (Refund Matrix)
- `test_cancellation_restores_slots_and_refunds`:
  - Tạo booking với số tiền khách đã đóng là 1,000,000 VNĐ.
  - Mô phỏng hủy trước 20 ngày -> Số tiền hoàn đúng **100%** (1,000,000 VNĐ).
  - Mô phỏng hủy trước 10 ngày -> Số tiền hoàn đúng **70%** (700,000 VNĐ).
  - Mô phỏng hủy trước 4 ngày -> Số tiền hoàn đúng **50%** (500,000 VNĐ).
  - Mô phỏng hủy trước 1 ngày -> Số tiền hoàn đúng **0 VNĐ**.
  - Kiểm tra xem sau khi hủy, `available_slots` của đợt khởi hành có được cộng hoàn trả nguyên vẹn hay không.
- `test_concurrent_cancellation_does_not_double_refund`: Kiểm tra gọi lệnh hủy nhiều lần trên một đơn hàng -> Không được sinh ra 2 lần tiền hoàn hoặc hoàn vượt quá số tiền đã đóng.

#### 4. Nhóm Kiểm Thử Hướng Dẫn Viên & Chống Trùng Lịch
- `test_guide_schedule_conflict`:
  - Phân công Hướng dẫn viên A cho chuyến đi từ ngày 10/10 đến ngày 15/10.
  - Thử phân công tiếp HDV A cho chuyến thứ hai từ ngày 12/10 đến ngày 14/10 -> Phải bị chặn với lỗi xung đột lịch trình.
  - Cập nhật thông tin ghi chú của chính chuyến đi 10/10 -> Phải thành công, không được tự báo trùng lịch với chính mình.

#### 5. Nhóm Kiểm Thử Trí Tuệ Nhân Tạo & Fallback Engine
- `test_ai_consultation_only_suggests_available_tours`: Kiểm tra phản hồi tư vấn AI chỉ chứa các ID của tour đang `OPEN` và còn chỗ.
- `test_ai_consultation_handles_impossible_request`: Yêu cầu tour với ngân sách 100,000 VNĐ -> AI xử lý lịch sự, không bị crash hoặc sinh ảo giác.
- `test_ai_fallback_when_no_api_key`: Xóa API Key khỏi môi trường -> API `/api/ai/consult` vẫn hoạt động trơn tru qua thuật toán heuristic nội bộ.
- `test_extract_json_from_llm`: Kiểm tra hàm bóc tách JSON xử lý thành công cả JSON thuần, JSON bọc trong markdown ````json ```` và văn bản lộn xộn.

#### 6. Nhóm Kiểm Thử Tra Cứu Magic Link & Trạng Thái
- `test_guest_tracking_and_magic_link`: Khách vãng lai gửi yêu cầu -> Nhận mã `access_token` -> Dùng token này tra cứu thông tin đơn thành công mà không cần đăng nhập.
- `test_public_dashboard_does_not_disclose_recent_customers`: Kiểm tra API công khai trang chủ không làm rò rỉ số điện thoại hoặc thông tin nhạy cảm của khách hàng khác.

---

### BỘ TRUY VẤN SQL KIỂM TRA DỮ LIỆU CSDL (DATABASE SANITY AUDIT):

```sql
-- 1. Kiểm tra danh sách tài khoản và vai trò RBAC
SELECT id, username, full_name, role, email, is_active FROM users;

-- 2. Kiểm tra danh mục Tour và định dạng tiền tệ VNĐ
SELECT code, title, destination, duration_days, base_price, is_active FROM tours ORDER BY base_price DESC;

-- 3. Kiểm tra số chỗ còn lại và trạng thái lịch khởi hành (Không được âm)
SELECT d.id, t.title, d.departure_date, d.return_date, d.available_slots, d.total_seats, d.status 
FROM departures d JOIN tours t ON d.tour_id = t.id;

-- 4. Kiểm tra toàn vẹn tài chính đơn đặt tour (Cọc đúng 30%)
SELECT booking_code, num_people, total_amount, deposit_amount, paid_amount, status 
FROM bookings WHERE deposit_amount != ROUND(total_amount * 0.3);
-- (Kết quả phải trả về 0 dòng lỗi)

-- 5. Kiểm tra nhật ký giao dịch thanh toán và hoàn tiền
SELECT p.id, b.booking_code, p.payment_type, p.amount, p.payment_method, p.status, p.created_at 
FROM payments p JOIN bookings b ON p.booking_id = b.id ORDER BY p.id DESC;
```

---

### YÊU CẦU FILE ĐẦU RA (OUTPUT DELIVERABLES):

Hãy xuất ra mã nguồn hoàn chỉnh cho:
- **`backend/tests/conftest.py`**: Fixture khởi tạo SQLite in-memory/file test riêng biệt, tạo TestClient FastAPI và seed tài khoản kiểm thử.
- Toàn bộ các file kiểm thử đặt trong `backend/tests/`:
  - `test_booking_logic.py`
  - `test_booking_regressions.py`
  - `test_integrity_and_concurrency.py`
  - `test_lifecycle_regressions.py`
  - `test_payments.py`
  - `test_rbac_and_search.py`
  - `test_security_regressions.py`
  - `test_ai_prompts.py`
  - `test_users.py`
  - `test_email_and_tracking.py`
- Lệnh thực thi: Chạy lệnh `pytest -v` phải đạt kết quả **100% Passed**.

