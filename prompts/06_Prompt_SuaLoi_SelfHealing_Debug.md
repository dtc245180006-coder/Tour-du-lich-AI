# PROMPT 06: BỘ PROMPT TỰ SỬA LỖI & XỬ LÝ SỰ CỐ THỰC CHIẾN (SELF-HEALING)
## (BATTLE-TESTED BUG FIXING PROMPTS FOR COMMON PRODUCTION FAILURES)

> **Mục đích**: Khi phát triển hệ thống bằng AI, các mô hình ngôn ngữ lớn (LLM) thường mắc phải 6 nhóm lỗi kinh điển về tranh chấp chỗ, logic kế toán, định dạng ngày tháng, parse JSON của AI và DOM Modal của frontend. Dưới đây là các prompt đặc trị đã được kiểm chứng để gửi ngay cho AI sửa lỗi khi gặp sự cố tương ứng.

---

### CASE 1: LỖI BÁN VƯỢT CHỖ (OVERBOOKING) & AVAILABLE_SLOTS BỊ ÂM

```markdown
[ROLE: Senior Backend Engineer & Database Specialist]
HỆ THỐNG ĐANG BỊ LỖI NGHIỆP VỤ: Đặt tour bị quá tải (Overbooking) và `available_slots` bị tụt xuống số âm khi có nhiều yêu cầu đặt chỗ đồng thời.

YÊU CẦU SỬA LỖI:
1. Mở file `backend/app/crud.py` tại hàm `create_booking` và `confirm_guest_booking`.
2. Kiểm tra điều kiện ngặt nghèo trước khi trừ chỗ:
   - Nếu `departure.available_slots < booking_in.num_people` hoặc `departure.status == 'FULL'`:
     Ngay lập tức ném `HTTPException(status_code=400, detail="Chuyến đi đã hết chỗ hoặc không đủ số lượng vé yêu cầu!")`.
3. Chỉ thực hiện trừ chỗ khi và chỉ khi còn đủ vé: `departure.available_slots -= booking_in.num_people`.
4. Nếu `departure.available_slots == 0`, cập nhật ngay `departure.status = 'FULL'`.
5. Đảm bảo toàn bộ luồng tạo Khách hàng, Booking và trừ chỗ nằm trong 1 khối `try...except`, nếu có bất kỳ lỗi nào xảy ra phải gọi `db.rollback()` và tuyệt đối không làm sai lệch số chỗ trong CSDL.
Hãy kiểm tra lại logic và xuất ra code hoàn chỉnh đã khắc phục triệt để.
```

---

### CASE 2: LỖI HƯỚNG DẪN VIÊN TỰ BÁO TRÙNG LỊCH VỚI CHÍNH MÌNH KHI SỬA TOUR

```markdown
[ROLE: Senior Backend Engineer]
HỆ THỐNG ĐANG BỊ LỖI LOGIC: Hàm kiểm tra trùng lịch Hướng dẫn viên (Guide Schedule Conflict) đang tự báo trùng lịch với chính đợt tour đang được chỉnh sửa.

YÊU CẦU SỬA LỖI:
1. Mở `backend/app/crud.py` tại hàm `check_guide_schedule_conflict` và `update_departure`.
2. Bổ sung tham số `exclude_departure_id: Optional[int] = None` vào hàm kiểm tra trùng lịch.
3. Trong câu query lọc các đợt khởi hành của HDV, thêm điều kiện loại trừ đợt tour hiện tại:
   `if exclude_departure_id: query = query.filter(models.Departure.id != exclude_departure_id)`.
4. Đảm bảo chỉ kiểm tra trùng trên các đợt tour có trạng thái còn hiệu lực (loại trừ các đợt đã `CANCELLED` hoặc `COMPLETED`).
5. Kiểm tra giao thoa khoảng ngày chuẩn xác:
   `models.Departure.departure_date <= target_return_date` VÀ `models.Departure.return_date >= target_departure_date`.
Hãy cập nhật lại code của cả 2 hàm trên để khi Edit không còn bị lỗi tự trùng lịch.
```

---

### CASE 3: LỖI TÍNH TOÁN HOÀN TIỀN KHI HỦY TOUR (REFUND CALCULATION ENGINE)

```markdown
[ROLE: Business Logic & Accounting Specialist]
HỆ THỐNG ĐANG BỊ LỖI TÍNH TOÁN HOÀN TIỀN (REFUND ENGINE):
1. Tiền hoàn đang bị tính sai trên Tổng giá trị đơn (`total_amount`) thay vì Số tiền khách thực tế đã thanh toán (`paid_amount`).
2. Số ngày còn lại (`days_left`) bị lỗi định dạng ngày tháng hoặc chênh lệch múi giờ.

YÊU CẦU SỬA LỖI:
1. Mở hàm `cancel_booking` trong `backend/app/crud.py`.
2. Chuẩn hóa việc tính số ngày còn lại bằng đối tượng `date`:
   `today = date.today()`
   `dep_date = departure.departure_date if isinstance(departure.departure_date, date) else datetime.strptime(departure.departure_date, "%Y-%m-%d").date()`
   `days_left = (dep_date - today).days`
3. Áp dụng chính xác tỷ lệ hoàn tiền nhân với `booking.paid_amount`:
   - Nếu `days_left >= 15`: hoàn 100% * paid_amount
   - Nếu `7 <= days_left < 15`: hoàn 70% * paid_amount
   - Nếu `3 <= days_left < 7`: hoàn 50% * paid_amount
   - Nếu `days_left < 3` hoặc đã qua ngày đi: hoàn 0 VNĐ.
4. Tự động phục hồi lại số chỗ cho tour: `departure.available_slots += booking.num_people`. Nếu đợt tour đang `FULL`, phải mở lại thành `OPEN`.
5. Tạo bản ghi giao dịch trong bảng `Payment` với `payment_type = 'REFUND'` và lưu đúng số tiền `refund_amount`.
Hãy sửa lại hàm này một cách chặt chẽ nhất.
```

---

### CASE 4: LỖI BACKEND CRASH DO LLM TRẢ VỀ JSON HỎNG (`JSONDecodeError`)

```markdown
[ROLE: Senior AI Integration Engineer]
HỆ THỐNG ĐANG BỊ CRASH BACKEND: Hàm gọi mô hình AI (Gemini/OpenAI) trong `backend/app/ai_service.py` bị lỗi `JSONDecodeError` khi parse kết quả trả về từ LLM (do AI bọc markdown ```json ... ``` hoặc trả văn bản kèm theo).

YÊU CẦU SỬA LỖI:
1. Viết một hàm tiện ích bóc tách JSON siêu bền bỉ: `_extract_json_from_llm(raw_text: str) -> Optional[dict]`.
2. Hàm này phải xử lý các trường hợp:
   - Dùng Regex tìm khối mã markdown: `re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)`
   - Nếu không có markdown codeblock, dùng Regex tìm từ dấu ngoặc nhọn `{` đầu tiên đến dấu `}` cuối cùng trong văn bản.
   - Thử `json.loads()` và bọc trong khối `try...except`.
3. Nếu LLM vẫn trả về dữ liệu hỏng hoặc rỗng, PHẢI kích hoạt cơ chế Fallback (dùng dữ liệu mẫu hoặc bộ quy tắc sinh tự động nội bộ) để trả về đúng cấu trúc Schema mà Frontend đang chờ, TUYỆT ĐỐI không để Backend văng exception 500 ra ngoài.
Hãy cập nhật lại toàn bộ các hàm gọi AI trong `ai_service.py`.
```

---

### CASE 5: LỖI GIAO DIỆN BỊ TREO / KẸT BACKDROP KHI ĐÓNG MODAL (MODAL FREEZE)

```markdown
[ROLE: Senior Frontend UI/UX Engineer]
GIAO DIỆN ĐANG BỊ LỖI MODAL: Khi đóng modal, lớp màn mờ (backdrop/overlay) không biến mất hoặc thẻ `<body>` vẫn bị gán thuộc tính `overflow: hidden`, khiến toàn bộ trang web bị đơ không thao tác được.

YÊU CẦU SỬA LỖI:
1. Mở file CSS chung và các file JS quản lý Modal:
2. Đảm bảo hàm `closeModal(modalId)` thực hiện đầy đủ 3 bước:
   - Gỡ bỏ class `active` hoặc `show` khỏi modal tương ứng: `document.getElementById(modalId).classList.remove('active')`.
   - Nếu có tạo backdrop động (`.modal-backdrop`), phải tìm và gọi `.remove()` để xóa hẳn khỏi DOM.
   - Luôn đặt lại thuộc tính cuộn trang: `document.body.style.overflow = 'auto'`.
3. Bổ sung sự kiện bấm phím `Escape (Esc)` và sự kiện click ra ngoài vùng nội dung modal (`modal-container`) thì tự động gọi `closeModal`.
4. Khi form trong modal submit, hãy chắc chắn có `event.preventDefault()` để tránh trình duyệt reload lại trang đột ngột làm mất trạng thái.
Hãy kiểm tra và cập nhật lại toàn bộ cơ chế đóng/mở modal trên giao diện.
```

---

### CASE 6: LỖI GIAO DIỆN SÁNG TỐI (DARK/LIGHT MODE) BỊ KẸT MÀU HOẶC KHÓ ĐỌC

```markdown
[ROLE: Senior UI/UX Designer]
GIAO DIỆN ĐANG BỊ LỖI HIỂN THỊ SÁNG TỐI:
1. Bảng điều khiển bị kẹt ở chế độ Dark Mode hoặc một số chữ bị chìm màu khó đọc khi chuyển sang Light Mode.
2. Cần bổ sung thanh Quick Login chuyển nhanh giữa các vai trò (Admin, Tư vấn, Kế toán) để test nhanh giao diện.

YÊU CẦU CẢI TIẾN:
1. Mở file CSS chủ đạo (`style.css` / `app.css`):
   - Chuẩn hóa CSS Variables cho cả `:root` (Light mode) và `[data-theme="dark"]` (Dark mode): `--bg-primary`, `--bg-card`, `--text-primary`, `--text-muted`, `--border-color`.
   - Đảm bảo tất cả bảng biểu, thẻ card, modal và thanh bên đều dùng biến màu thay vì hardcode mã hex `#000` hoặc `#fff`.
2. Trong JS, lưu lựa chọn theme vào `localStorage.getItem('theme')` và kích hoạt ngay khi tải trang (`DOMContentLoaded`) để tránh hiện tượng nháy màu (FOUC).
3. Đặt thanh Quick Role Switcher lên góc phải hoặc đầu Sidebar để click 1 chạm là đổi quyền demo ngay lập tức.
```

