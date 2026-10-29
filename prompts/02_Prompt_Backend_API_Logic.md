# PROMPT 02: XÂY DỰNG BACKEND API & LOGIC NGHIỆP VỤ LỮ HÀNH
## (FASTAPI RESTFUL API, ATOMIC BOOKINGS, VIETQR & SMTP MAILER)

---

### BỐI CẢNH & VAI TRÒ CỦA AI:
Bạn là **Lập Trình Viên Backend Cấp Cao (Senior FastAPI Backend Engineer)**.
Nhiệm vụ của bạn là hiện thực hóa toàn bộ tầng nghiệp vụ cốt lõi (Core Business Logic) và hệ thống RESTful API cho dự án VietJourney AI dựa trên CSDL SQLAlchemy đã được thiết kế ở Prompt 01.

---

### CÁC NGUYÊN TẮC NGHIỆP VỤ BẮT BUỘC PHẢI THỰC THI CHÍNH XÁC:

#### 1. Nghiệp Vụ Đặt Tour & Chống Bán Vượt Chỗ (Prevent Overbooking)
- Hàm `crud.create_booking`:
  - Tiếp nhận `departure_id`, thông tin khách hàng và số vé (`num_people`).
  - Kiểm tra đợt tour phải tồn tại và đang ở trạng thái `OPEN`.
  - Kiểm tra điều kiện ngặt nghèo: `departure.available_slots >= num_people`. Nếu thiếu chỗ, ném ngay `HTTPException(status_code=400, detail="Chuyến đi đã hết chỗ hoặc không đủ số lượng vé yêu cầu!")`.
  - **Trừ chỗ nguyên tử**: `departure.available_slots -= num_people`. Nếu `departure.available_slots == 0`, tự động cập nhật `departure.status = 'FULL'`.
  - Tự động gọi `get_or_create_customer(db, customer_in)`: Tìm khách hàng theo số điện thoại, nếu đã tồn tại thì cập nhật email và tên mới nhất; nếu chưa có thì tạo mới.
  - Tính toán tài chính:
    - `total_amount = num_people * (departure.price_override if departure.price_override else tour.base_price)`
    - `deposit_amount = round(total_amount * 0.3)` (Đúng chuẩn 30% tiền cọc).
  - Sinh mã đơn hàng ngẫu nhiên: `VJ-YYYYMM-XXXX` và sinh token bảo mật `access_token = uuid.uuid4().hex`.
  - Nếu có thanh toán ban đầu (`initial_payment > 0`), tự động tạo bản ghi trong `payments` và cập nhật `paid_amount`.

#### 2. Luồng Xử Lý Hàng Chờ Khách Vãng Lai (Guest Booking Queue)
- `crud.create_guest_booking`:
  - Khách vãng lai gửi yêu cầu từ trang chủ hoặc chatbot.
  - Tạo đơn booking với `status = 'WAITING_CONFIRM'`.
  - **LUẬT TUYỆT ĐỐI**: Trạng thái `WAITING_CONFIRM` KHÔNG ĐƯỢC PHÉP TRỪ `available_slots` trong CSDL.
- `crud.confirm_guest_booking`:
  - Khi nhân viên tư vấn bấm nút "Duyệt yêu cầu":
  - Kiểm tra lại `departure.available_slots >= booking.num_people`. Nếu còn đủ chỗ mới trừ ghế, đổi trạng thái booking thành `PENDING`, sinh mã VietQR và gửi email hướng dẫn cọc.
- `crud.reject_guest_booking`:
  - Nhân viên từ chối đơn không hợp lệ: Chuyển `status = 'REJECTED'`, lưu lý do từ chối. Không hoàn trả chỗ (vì chưa từng trừ chỗ).

#### 3. Nghiệp Vụ Hủy Tour & Hoàn Tiền Bậc Thang (Tiered Refund Policy)
- Hàm `crud.cancel_booking`:
  - Tính số ngày còn lại đến ngày khởi hành bằng đối tượng `date`:
    ```python
    today = date.today()
    dep_date = departure.departure_date if isinstance(departure.departure_date, date) else datetime.strptime(departure.departure_date, "%Y-%m-%d").date()
    days_left = (dep_date - today).days
    ```
  - **Công thức hoàn tiền tính trên số tiền thực tế khách đã đóng (`paid_amount`)**:
    - `days_left >= 15`: Hoàn lại **100%** $\times$ `paid_amount`.
    - `7 <= days_left < 15`: Hoàn lại **70%** $\times$ `paid_amount`.
    - `3 <= days_left < 7`: Hoàn lại **50%** $\times$ `paid_amount`.
    - `days_left < 3` hoặc đã qua ngày đi: Hoàn lại **0 VNĐ**.
  - **Phục hồi số chỗ**: `departure.available_slots += booking.num_people`. Nếu đợt tour đang là `FULL`, tự động mở lại thành `OPEN`.
  - Cập nhật `booking.status = 'CANCELLED'`, ghi nhận `booking.refund_amount`.
  - Nếu `refund_amount > 0`, tự động tạo bản ghi giao dịch trong bảng `payments` với `payment_type = 'REFUND'`.

#### 4. Nghiệp Vụ Chống Trùng Lịch Hướng Dẫn Viên (Guide Schedule Conflict)
- Hàm `crud.check_guide_schedule_conflict(db, guide_id, departure_date, return_date, exclude_departure_id=None)`:
  - Truy vấn các đợt khởi hành mà HDV đó đang đảm nhiệm trong khoảng `[departure_date, return_date]`.
  - Điều kiện giao thoa ngày: `Departure.departure_date <= target_return_date AND Departure.return_date >= target_departure_date`.
  - Phải có tham số `exclude_departure_id` để khi cập nhật (Edit) một đợt tour, hệ thống không tự báo trùng lịch với chính đợt tour đang sửa.
  - Chỉ kiểm tra trên các đợt tour đang hoạt động (loại trừ `CANCELLED` và `COMPLETED`).
  - Nếu phát hiện trùng lịch, ném `HTTPException(status_code=400, detail="Hướng dẫn viên này đã có lịch phụ trách một đợt tour khác trong khoảng thời gian này!")`.

#### 5. Kế Toán Thu Chi & Tích Hợp VietQR
- Hàm `crud.add_payment`:
  - Thêm bản ghi thanh toán mới và cộng dồn vào `booking.paid_amount`.
  - Nếu `paid_amount >= booking.total_amount`: Tự động cập nhật `booking.status = 'CONFIRMED'`.
  - Nếu `paid_amount >= booking.deposit_amount` (và chưa đủ 100%): Tự động cập nhật `booking.status = 'DEPOSITED'`.
- Tự động sinh link mã QR theo chuẩn **VietQR Quick Link**:
  `https://img.vietqr.io/image/<BANK_ID>-<ACCOUNT_NO>-compact2.png?amount=<AMOUNT>&addInfo=<BOOKING_CODE>`

#### 6. Dịch Vụ Gửi Email Nền (Asynchronous SMTP Mailer)
- Xây dựng module `email_service.py` sử dụng thư viện chuẩn `smtplib` và `email.mime`:
  - Gửi email xác nhận đặt tour kèm thông tin vé và link VietQR.
  - Gửi email thông báo hoàn cọc khi hủy tour.
  - Sử dụng FastAPI `BackgroundTasks` hoặc Thread riêng để gửi ngầm (Non-blocking), không làm chậm phản hồi HTTP Request của khách hàng.

---

### YÊU CẦU FILE ĐẦU RA (OUTPUT DELIVERABLES):

Hãy xuất ra mã nguồn hoàn chỉnh cho:
1. **`backend/app/schemas.py`**: Định nghĩa Pydantic v2 Schemas (Request/Response DTOs) cho toàn bộ các thực thể: User, Tour, Departure, Customer, Booking, Payment, Guide, Feedback.
2. **`backend/app/crud.py`**: Chứa toàn bộ các hàm nghiệp vụ đã nêu ở trên bọc trong khối giao dịch an toàn (`try...except db.rollback()`).
3. **`backend/app/auth.py`**: Chứa hàm băm mật khẩu, kiểm tra mật khẩu, sinh JWT Token và dependency phân quyền vai trò `require_roles(['ADMIN', ...])`.
4. **`backend/app/routers/`**:
   - `auth_router.py`: Login, me, quick demo switch.
   - `tour_router.py`: CRUD tours, tìm kiếm tour.
   - `departure_router.py`: Quản lý đợt khởi hành, kiểm tra xung đột HDV.
   - `booking_router.py`: Đặt tour, duyệt/từ chối khách vãng lai, hủy hoàn tiền, tra cứu Magic Link công khai qua `access_token`.
   - `payment_router.py`: Kế toán thu chi.
   - `guide_router.py`: Hồ sơ HDV.
   - `feedback_router.py`: Gửi và xem đánh giá.
5. **`backend/app/main.py`**: Đăng ký toàn bộ Routers, cấu hình CORS, phục vụ Static Files frontend và xử lý exception tập trung.

