"""
Script render toàn bộ 21 ảnh sơ đồ UML chất lượng cao (PNG) cho VietJourney AI.
"""

import os
import sys
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from diagram_renderers import (
    get_html_01, get_html_02, get_html_03, get_html_04, get_html_05,
    get_activity_html, get_sequence_html
)

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT_DIR = os.path.abspath("docs/diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

from build_all_images import COMMON_HEAD

def export_png(filename, html_body, width=1600, height=1050):
    output_png = os.path.join(OUT_DIR, f"{filename}.png")
    tmp_html = os.path.join(OUT_DIR, f"{filename}_tmp.html")
    full_html = f"<!DOCTYPE html><html><head>{COMMON_HEAD}</head><body><div class='canvas'>{html_body}</div></body></html>"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        f"--screenshot={output_png}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        f"file:///{tmp_html.replace(chr(92), '/')}"
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    print(f"✓ [{os.path.basename(output_png)}] ({os.path.getsize(output_png):,} bytes)")

def main():
    print("================================================================")
    print("BẮT ĐẦU XUẤT 21 ẢNH SƠ ĐỒ UML CHUẨN CHO VIETJOURNEY AI...")
    print("================================================================")

    # 01 - 05: Sơ đồ kiến trúc tổng quan
    export_png("01_So_do_Use_Case_Tong_quat", get_html_01())
    export_png("02_Phan_cap_chuc_nang", get_html_02())
    export_png("03_So_do_Lop_Class_Diagram", get_html_03())
    export_png("04_So_do_CSDL_ERD_10_Bang", get_html_04())
    export_png("05_So_do_Luong_man_hinh_Screen_Flow", get_html_05())

    # 06 - 07: UC001
    act_06 = """
    <div class="act-node" style="width:380px;">1. Người dùng nhập Tên đăng nhập và Mật khẩu</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:380px;">2. Kiểm tra tính hợp lệ dữ liệu (không bỏ trống form)</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:380px;">3. Gửi yêu cầu POST /auth/login tới Backend FastAPI</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">4. Truy vấn CSDL Users & Xác minh mật khẩu PBKDF2-SHA256</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Mật khẩu khớp?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Sai] Báo lỗi 'Tài khoản hoặc mật khẩu không chính xác'</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Đúng] Sinh mã định danh JWT Access Token</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:480px; background:#f0fdf4; border-color:#16a34a; color:#15803d;">
      5. Lưu Token vào localStorage & Điều hướng theo Role:<br/>
      • <b>ADMIN</b>: Toàn bộ menu quản trị, tour, đợt khởi hành, HDV, tài khoản<br/>
      • <b>CONSULTANT</b>: Hàng chờ tư vấn, xác nhận giữ chỗ, quản lý đặt chỗ<br/>
      • <b>ACCOUNTANT</b>: Lịch sử thu tiền, phiếu thu, thống kê doanh thu
    </div>
    """
    export_png("06_UC001_Dang_nhap_Activity", get_activity_html("UC001", "Đăng nhập & Phân quyền RBAC", act_06, "Mật khẩu băm PBKDF2; Token cấp phát theo chuẩn OAuth2 Password Bearer"))

    seq_07_lifelines = [
        ("User", "Actor", "#0284c7"),
        ("LoginForm", "Frontend", "#475569"),
        ("AuthRouter", "FastAPI", "#16a34a"),
        ("AuthService", "PBKDF2 / JWT", "#d97706"),
        ("UsersTable", "Database", "#dc2626")
    ]
    seq_07_msgs = [
        ("User", "LoginForm", "1. Nhập username, password -> Nhấn 'Đăng nhập'", False),
        ("LoginForm", "AuthRouter", "2. POST /auth/login {username, password}", False),
        ("AuthRouter", "UsersTable", "3. get_user_by_username(username)", False),
        ("UsersTable", "AuthRouter", "4. Trả về bản ghi User (id, hashed_password, role, is_active)", True),
        ("AuthRouter", "AuthService", "5. verify_password(plain_password, hashed_password)", False),
        ("AuthService", "AuthRouter", "6. Xác thực thành công (True) -> Cấp token", True),
        ("AuthRouter", "AuthService", "7. create_access_token(data={'sub': username, 'role': role})", False),
        ("AuthService", "AuthRouter", "8. Trả về JWT Access Token", True),
        ("AuthRouter", "LoginForm", "9. 200 OK {access_token, token_type: 'bearer', role, full_name}", True),
        ("LoginForm", "User", "10. Lưu Token vào localStorage -> Chuyển hướng Dashboard theo Role", True)
    ]
    export_png("07_UC001_Dang_nhap_Sequence", get_sequence_html("UC001", "Đăng nhập & Phân quyền RBAC", seq_07_lifelines, seq_07_msgs, "JWT xác thực trạng thái phiên và phân quyền trên mọi API"))

    # 08 - 09: UC002
    act_08 = """
    <div class="act-node" style="width:380px;">1. Quản trị viên truy cập màn hình Quản lý Tour</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">2. Chọn '+ Thêm tour mới' hoặc 'Cập nhật' tour hiện có</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">3. Nhập dữ liệu cơ bản: Tên tour, Điểm đến, Thời lượng, Giá gốc</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Dùng AI?</span></div>
    <div style="display:flex; justify-content:space-between; width:600px; margin-top:10px;">
      <div style="background:#faf5ff; border:1px solid #9333ea; border-radius:6px; padding:8px 12px; font-size:11px; color:#6b21a8; width:280px; text-align:center;">
        [Có] Bấm 'AI Viết mô tả tour' &rarr; Gửi prompt sang Gemini AI &rarr; Điền tự động nội dung & lịch trình tóm tắt
      </div>
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:8px 12px; font-size:11px; color:#475569; width:280px; text-align:center;">
        [Không] Admin tự biên soạn nội dung mô tả thủ công vào form
      </div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">4. Admin rà soát, tinh chỉnh nội dung và bấm 'Lưu Tour'</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">5. Backend xác thực (mã tour duy nhất, giá > 0) -> Ghi vào bảng Tours</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div style="background:#fee2e2; border:1px solid #dc2626; border-radius:6px; padding:6px 12px; font-size:11px; color:#991b1b; text-align:center; width:520px;">
      Lưu ý nghiệp vụ Xóa: Hệ thống chặn xóa nếu tour đã phát sinh lịch khởi hành hoặc booking giao dịch!
    </div>
    """
    export_png("08_UC002_Quan_ly_Tour_AI_Activity", get_activity_html("UC002", "Quản lý Tour & AI sinh mô tả", act_08, "AI Gemini hỗ trợ sinh văn bản nháp; Admin giữ vai trò phê duyệt cuối cùng"))

    seq_09_lifelines = [
        ("Admin", "Actor", "#dc2626"),
        ("TourAdminView", "Frontend", "#475569"),
        ("TourRouter", "FastAPI", "#16a34a"),
        ("AIService", "Gemini Client", "#9333ea"),
        ("GoogleGeminiAPI", "Cloud AI", "#7e22ce"),
        ("ToursTable", "Database", "#0284c7")
    ]
    seq_09_msgs = [
        ("Admin", "TourAdminView", "1. Nhập tiêu đề, điểm đến, thời lượng -> Bấm 'AI Viết mô tả tour'", False),
        ("TourAdminView", "TourRouter", "2. POST /ai/generate-tour-description {title, destination, days}", False),
        ("TourRouter", "AIService", "3. generate_tour_description(prompt)", False),
        ("AIService", "GoogleGeminiAPI", "4. Gọi API Google Gemini Flash/Pro với prompt chuẩn hóa", False),
        ("GoogleGeminiAPI", "AIService", "5. Trả về đoạn văn giới thiệu du lịch hấp dẫn & tóm tắt lịch trình", True),
        ("AIService", "TourRouter", "6. Log phiên tương tác vào ai_session_logs & trả nội dung", True),
        ("TourRouter", "TourAdminView", "7. 200 OK -> Tự động điền văn bản vào khung mô tả", True),
        ("Admin", "TourAdminView", "8. Rà soát, chỉnh sửa nội dung hoàn thiện -> Nhấn 'Lưu Tour'", False),
        ("TourAdminView", "TourRouter", "9. POST /tours (Payload đầy đủ thuộc tính tour)", False),
        ("TourRouter", "ToursTable", "10. INSERT INTO tours VALUES (...) -> COMMIT", False),
        ("TourRouter", "TourAdminView", "11. 201 Created -> Thêm mới dòng tour trên bảng hiển thị", True)
    ]
    export_png("09_UC002_Quan_ly_Tour_AI_Sequence", get_sequence_html("UC002", "Quản lý Tour & AI sinh mô tả", seq_09_lifelines, seq_09_msgs, "Tích hợp Gemini AI an toàn; Quản trị viên duyệt trước khi lưu CSDL"))

    # 10 - 11: UC003
    act_10 = """
    <div class="act-node" style="width:380px;">1. Admin truy cập màn hình Lịch Khởi Hành & Chỗ</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">2. Bấm '+ Mở đợt khởi hành mới' -> Chọn Tour, Ngày đi, Ngày về, Tổng số chỗ</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">3. Chọn Hướng dẫn viên phụ trách từ danh sách nhân sự</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Trùng lịch?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Trùng] Cảnh báo HDV đã bận -> Yêu cầu chọn HDV khác</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Không] available_slots = total_slots, status = 'OPEN'</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">4. Lưu bản ghi vào bảng Departures -> Mở bán thành công</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:520px; background:#fffbeb; border-color:#d97706; color:#92400e;">
      5. Quản lý vòng đời chuyến đi:<br/>
      • Đến ngày đi: Admin bấm <b>'Bắt đầu'</b> &rarr; status='RUNNING', HDV chuyển 'ON_TOUR'<br/>
      • Khi kết thúc: Admin bấm <b>'Hoàn tất'</b> &rarr; status='COMPLETED', HDV chuyển 'AVAILABLE'
    </div>
    """
    export_png("10_UC003_Lich_khoi_hanh_Activity", get_activity_html("UC003", "Quản lý Lịch khởi hành & Điều phối HDV", act_10, "Kiểm soát số chỗ trống chặt chẽ; Tự động đồng bộ trạng thái công tác của HDV"))

    seq_11_lifelines = [
        ("Admin", "Actor", "#dc2626"),
        ("DepartureView", "Frontend", "#475569"),
        ("DepartureRouter", "FastAPI", "#16a34a"),
        ("GuideCRUD", "Service", "#d97706"),
        ("DeparturesTable", "Database", "#0284c7")
    ]
    seq_11_msgs = [
        ("Admin", "DepartureView", "1. Điền form mở đợt mới (tour_id, dates, total_slots, guide_id)", False),
        ("DepartureView", "DepartureRouter", "2. GET /departures/check-conflict?guide_id=...&from=...&to=...", False),
        ("DepartureRouter", "GuideCRUD", "3. check_schedule_conflict(guide_id, start_date, end_date)", False),
        ("GuideCRUD", "DepartureRouter", "4. Trả về: {conflict: false, message: 'HDV sẵn sàng'}", True),
        ("DepartureView", "DepartureRouter", "5. POST /departures (Payload đợt khởi hành)", False),
        ("DepartureRouter", "DeparturesTable", "6. INSERT INTO departures (available_slots=total_slots, status='OPEN')", False),
        ("DepartureRouter", "DepartureView", "7. 201 Created -> Hiển thị thêm dòng đợt khởi hành mới", True),
        ("Admin", "DepartureView", "8. Khi đến ngày đi -> Admin bấm 'Bắt đầu chuyến đi'", False),
        ("DepartureView", "DepartureRouter", "9. POST /departures/{id}/start", False),
        ("DepartureRouter", "DeparturesTable", "10. UPDATE status='RUNNING', đồng bộ HDV='ON_TOUR' -> COMMIT", False)
    ]
    export_png("11_UC003_Lich_khoi_hanh_Sequence", get_sequence_html("UC003", "Quản lý Lịch khởi hành & Điều phối HDV", seq_11_lifelines, seq_11_msgs, "Kiểm tra trùng lịch tự động; Quản lý vòng đời chuyến đi: OPEN -> RUNNING -> COMPLETED"))

    # 12 - 13: UC004
    act_12 = """
    <div style="display:flex; justify-content:space-between; width:680px;">
      <div class="act-node" style="width:320px; background:#e0f2fe; border-color:#0284c7; color:#0369a1;">
        <b>Khách vãng lai gửi yêu cầu:</b><br/>Lưu đơn ở trạng thái 'WAITING_CONFIRM'<br/>(<b>Tuyệt đối chưa trừ số chỗ trống!</b>)
      </div>
      <div class="act-node" style="width:320px; background:#dcfce7; border-color:#16a34a; color:#15803d;">
        <b>Tư vấn viên tiếp nhận:</b><br/>Kiểm tra thông tin liên lạc khách hàng &<br/>Tra cứu hồ sơ hoặc tạo mới Customer
      </div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Khách đồng ý?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Không/Đổi ý] Bấm 'Từ chối' &rarr; status='CANCELLED'</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Đồng ý] Bấm 'Xác Nhận Giữ Chỗ' (kèm Idempotency-Key)</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:480px;">Khóa dòng dữ liệu đợt khởi hành (SELECT ... FOR UPDATE)</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Đủ chỗ?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Thiếu] Rollback Transaction &rarr; Báo lỗi hết chỗ!</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Đủ] available_slots -= num_people</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:500px; background:#f0fdf4; border-color:#16a34a; color:#15803d;">
      Cập nhật Booking: status = 'PENDING', sinh mã BK-...<br/>
      Lưu Idempotency Key &rarr; Commit Transaction &rarr; Xuất mã đặt chỗ thành công!
    </div>
    """
    export_png("12_UC004_Dat_cho_Idempotency_Activity", get_activity_html("UC004", "Khách hàng & Đặt chỗ (Idempotency & Khóa ghế)", act_12, "Cơ chế Pessimistic Lock chống race condition khi nhiều người cùng đặt 1 chuyến"))

    seq_13_lifelines = [
        ("Consultant", "Actor", "#16a34a"),
        ("BookingUI", "Frontend", "#475569"),
        ("BookingRouter", "FastAPI", "#0284c7"),
        ("IdempotencyService", "Security", "#d97706"),
        ("BookingCRUD", "Transaction", "#dc2626"),
        ("Database", "dep, bookings", "#7e22ce")
    ]
    seq_13_msgs = [
        ("Consultant", "BookingUI", "1. Bấm 'Xác Nhận Giữ Chỗ' cho yêu cầu REQ-...", False),
        ("BookingUI", "BookingRouter", "2. POST /bookings/{id}/confirm (Header: Idempotency-Key: abc-123)", False),
        ("BookingRouter", "IdempotencyService", "3. check_duplicate_key('abc-123')", False),
        ("IdempotencyService", "BookingRouter", "4. Key hợp lệ (chưa xử lý trong hệ thống)", True),
        ("BookingRouter", "BookingCRUD", "5. confirm_booking_with_lock(booking_id, db)", False),
        ("BookingCRUD", "Database", "6. BEGIN TRANSACTION -> SELECT available_slots FROM departures FOR UPDATE", False),
        ("BookingCRUD", "Database", "7. Kiểm tra available_slots >= num_people -> UPDATE available_slots -= num_people", False),
        ("BookingCRUD", "Database", "8. UPDATE bookings SET status='PENDING' & INSERT booking_request_keys -> COMMIT", False),
        ("BookingCRUD", "BookingRouter", "9. Trả về BookingOut {booking_code: 'BK-...', status: 'PENDING'}", True),
        ("BookingRouter", "BookingUI", "10. 200 OK -> Giữ chỗ thành công! Chuyển trạng thái sang Chờ thanh toán", True)
    ]
    export_png("13_UC004_Dat_cho_Idempotency_Sequence", get_sequence_html("UC004", "Khách hàng & Đặt chỗ (Idempotency & Khóa ghế)", seq_13_lifelines, seq_13_msgs, "Khóa bi quan (SELECT FOR UPDATE) và Khóa Idempotency đảm bảo toàn vẹn dữ liệu tuyệt đối"))

    # 14 - 15: UC005
    act_14 = """
    <div class="act-node" style="width:400px;">1. Kế toán/Admin vào menu 'Kế toán & Thu tiền' -> Chọn đơn Booking</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">2. Mở modal 'Thu tiền' -> Nhập số tiền thu thực tế & Phương thức thanh toán</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Hợp lệ?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Sai] Tiền <= 0 hoặc vượt quá dư nợ -> Báo lỗi dữ liệu</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Đúng] Ghi bản ghi Payments (transaction_code, created_by)</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:440px;">3. Cộng dồn số tiền đã đóng: paid_amount += amount</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div style="display:flex; justify-content:space-between; width:620px;">
      <div style="background:#dcfce7; border:1.5px solid #16a34a; border-radius:8px; padding:8px 12px; font-size:11px; width:290px; color:#15803d; text-align:center;">
        <b>Đạt 100% tổng tiền:</b><br/>Cập nhật status = 'CONFIRMED' (Xác nhận đi)
      </div>
      <div style="background:#e0f2fe; border:1.5px solid #0284c7; border-radius:8px; padding:8px 12px; font-size:11px; width:290px; color:#0369a1; text-align:center;">
        <b>Đạt >= 30% (< 100%):</b><br/>Cập nhật status = 'DEPOSITED' (Đã cọc)
      </div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div style="background:#fee2e2; border:1px solid #dc2626; border-radius:6px; padding:8px 14px; font-size:11.5px; color:#991b1b; width:580px; text-align:center;">
      <b>Trường hợp Hủy tour:</b> Kiểm tra hủy trước ngày khởi hành &rarr; Tính % hoàn tiền hợp lệ theo số ngày báo trước &rarr; Lập phiếu chi REFUND &rarr; Hoàn trả lại ghế trống cho đợt khởi hành!
    </div>
    """
    export_png("14_UC005_Thanh_toan_Dat_coc_Activity", get_activity_html("UC005", "Quản lý Thanh toán, Đặt cọc & Hoàn tiền", act_14, "Consultant không có quyền thu tiền; Chỉ Kế toán và Admin mới được lập phiếu thu/chi"))

    seq_15_lifelines = [
        ("Accountant", "Actor", "#d97706"),
        ("PaymentUI", "Frontend", "#475569"),
        ("PaymentRouter", "FastAPI", "#16a34a"),
        ("PaymentService", "Accounting", "#0284c7"),
        ("Database", "payments, bookings", "#dc2626")
    ]
    seq_15_msgs = [
        ("Accountant", "PaymentUI", "1. Chọn đơn booking -> Bấm 'Thu tiền' -> Nhập số tiền thu", False),
        ("PaymentUI", "PaymentRouter", "2. POST /payments {booking_id, amount, payment_method, payment_type}", False),
        ("PaymentRouter", "PaymentService", "3. record_payment_and_update_status(db, payment_data)", False),
        ("PaymentService", "Database", "4. INSERT INTO payments (transaction_code, amount, status='SUCCESS')", False),
        ("PaymentService", "Database", "5. UPDATE bookings SET paid_amount += amount, status='CONFIRMED' / 'DEPOSITED'", False),
        ("PaymentService", "Database", "6. COMMIT TRANSACTION", False),
        ("PaymentService", "PaymentRouter", "7. Trả về PaymentReceiptOut {transaction_code: 'PAY-...', status: 'SUCCESS'}", True),
        ("PaymentRouter", "PaymentUI", "8. 201 Created -> Cập nhật số tiền đã đóng & Đổi nhãn trạng thái trực quan", True)
    ]
    export_png("15_UC005_Thanh_toan_Dat_coc_Sequence", get_sequence_html("UC005", "Ghi nhận Thanh toán & Cập nhật trạng thái", seq_15_lifelines, seq_15_msgs, "Tự động phân loại cọc (>=30%) và thanh toán đủ (100%); Lưu vết người thực hiện created_by"))

    # 16 - 17: UC006
    act_16 = """
    <div class="act-node" style="width:420px;">1. Khách hàng gửi đánh giá sau tour (Sao tour 1-5, Sao HDV 1-5, Nhận xét)</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">2. CSDL lưu bản ghi mới vào bảng Feedbacks</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:460px;">3. Admin/Consultant vào menu 'Phản Hồi' -> Bấm 'AI Tóm tắt phản hồi theo Tour'</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-decision"><span>Có review?</span></div>
    <div style="display:flex; justify-content:space-between; width:520px; margin-top:10px;">
      <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:6px; padding:6px 10px; font-size:11px; color:#991b1b;">[Chưa có] Báo lỗi 'Chưa có dữ liệu phản hồi để AI phân tích'</div>
      <div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:6px 10px; font-size:11px; color:#166534;">[Đã có] Backend gom text phản hồi gửi sang Google Gemini AI</div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:520px; background:#faf5ff; border-color:#9333ea; color:#6b21a8;">
      4. Gemini AI phân tích Sentiment (Tích cực/Tiêu cực/Trung lập)<br/>
      Trích xuất: <b>Điểm khen ngợi</b> | <b>Điểm cần khắc phục</b> | <b>Đánh giá chất lượng HDV</b> | <b>Đề xuất cải tiến</b>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:480px;">5. Ghi nhật ký vào ai_session_logs & Hiển thị Dashboard AI tóm tắt cho Ban Giám Đốc</div>
    """
    export_png("16_UC006_Phan_hoi_AI_Summary_Activity", get_activity_html("UC006", "Quản lý Phản hồi & AI Tóm tắt Sentiment", act_16, "Mô hình ngôn ngữ lớn xử lý NLP; Phân loại sắc thái cảm xúc và trích xuất điểm cốt lõi"))

    seq_17_lifelines = [
        ("Admin/User", "Actor", "#dc2626"),
        ("FeedbackUI", "Frontend", "#475569"),
        ("AIRouter", "FastAPI", "#16a34a"),
        ("AIService", "Gemini Client", "#9333ea"),
        ("GoogleGeminiAPI", "Cloud AI", "#7e22ce"),
        ("Database", "feedbacks, ai_logs", "#0284c7")
    ]
    seq_17_msgs = [
        ("Admin/User", "FeedbackUI", "1. Chọn Tour du lịch -> Nhấn nút 'Bắt Đầu Phân Tích & Tóm Tắt AI'", False),
        ("FeedbackUI", "AIRouter", "2. POST /ai/summarize-feedbacks?tour_id=...", False),
        ("AIRouter", "Database", "3. SELECT * FROM feedbacks WHERE tour_id=...", False),
        ("Database", "AIRouter", "4. Trả về danh sách feedbacks (comments, rating, guide_rating)", True),
        ("AIRouter", "AIService", "5. summarize_feedbacks(feedbacks_data)", False),
        ("AIService", "GoogleGeminiAPI", "6. Request Gemini Engine: Phân tích sentiment & trích xuất ý chính", False),
        ("GoogleGeminiAPI", "AIService", "7. Trả về JSON: {sentiment, strengths, weaknesses, guide_eval, suggestions}", True),
        ("AIService", "Database", "8. INSERT INTO ai_session_logs (feature_type='FEEDBACK_SUMMARY')", False),
        ("AIService", "AIRouter", "9. Trả kết quả tóm tắt phân tích đã làm sạch", True),
        ("AIRouter", "FeedbackUI", "10. 200 OK -> Hiển thị 4 thẻ thông tin trực quan cho Ban Giám Đốc", True)
    ]
    export_png("17_UC006_Phan_hoi_AI_Summary_Sequence", get_sequence_html("UC006", "AI Phân tích cảm xúc & Tóm tắt phản hồi", seq_17_lifelines, seq_17_msgs, "Pipeline AI tóm tắt tự động; Giúp nâng cao chất lượng dịch vụ du lịch dựa trên dữ liệu khách"))

    # 18 - 19: UC007
    act_18 = """
    <div class="act-node" style="width:380px;">1. Admin truy cập màn hình Quản lý Hướng Dẫn Viên</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">2. Chọn '+ Thêm HDV mới' hoặc 'Chỉnh sửa' hồ sơ nhân sự</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">3. Nhập: Họ tên, Số điện thoại, Email, Ngôn ngữ, Thâm niên kinh nghiệm</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:420px;">4. Kiểm tra hợp lệ dữ liệu -> Lưu vào bảng tour_guides trong CSDL</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:500px; background:#fffbeb; border-color:#d97706; color:#92400e;">
      5. Giám sát trạng thái công tác:<br/>
      • <b>AVAILABLE</b>: Sẵn sàng điều phối dẫn tour<br/>
      • <b>ON_TOUR</b>: Đang phụ trách đoàn (tự động kích hoạt khi departure RUNNING)<br/>
      • <b>OFF</b>: Đang nghỉ phép / tạm dừng công tác
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div style="background:#fee2e2; border:1px solid #dc2626; border-radius:6px; padding:8px 14px; font-size:11.5px; color:#991b1b; width:520px; text-align:center;">
      Nghiệp vụ Xóa: Kiểm tra nếu HDV đang có lịch dẫn tour sắp diễn ra &rarr; Hệ thống cảnh báo và ngăn chặn xóa!
    </div>
    """
    export_png("18_UC007_Huong_dan_vien_Activity", get_activity_html("UC007", "Quản lý Hướng dẫn viên & Điều hành tour", act_18, "Hồ sơ HDV gắn liền với lịch khởi hành; Kiểm soát trùng lịch tự động"))

    seq_19_lifelines = [
        ("Admin", "Actor", "#dc2626"),
        ("GuideView", "Frontend", "#475569"),
        ("GuideRouter", "FastAPI", "#16a34a"),
        ("GuideCRUD", "Repository", "#d97706"),
        ("Database", "tour_guides", "#0284c7")
    ]
    seq_19_msgs = [
        ("Admin", "GuideView", "1. Điền form tạo mới HDV (họ tên, phone, languages, exp_years)", False),
        ("GuideView", "GuideRouter", "2. POST /guides (Payload GuideCreate)", False),
        ("GuideRouter", "GuideCRUD", "3. create_guide(db, guide_data)", False),
        ("GuideCRUD", "Database", "4. INSERT INTO tour_guides (status='AVAILABLE', rating=5.0) -> COMMIT", False),
        ("GuideCRUD", "GuideRouter", "5. Trả về GuideOut (id, full_name, phone, status)", True),
        ("GuideRouter", "GuideView", "6. 201 Created -> Cập nhật bảng danh sách HDV", True),
        ("Admin", "GuideView", "7. Xóa HDV -> Bấm nút 'Xóa'", False),
        ("GuideView", "GuideRouter", "8. DELETE /guides/{id}", False),
        ("GuideRouter", "Database", "9. Kiểm tra đợt khởi hành liên quan -> Cho phép xóa hoặc chặn nếu có lịch", False)
    ]
    export_png("19_UC007_Huong_dan_vien_Sequence", get_sequence_html("UC007", "Quản lý Hướng dẫn viên & Điều hành tour", seq_19_lifelines, seq_19_msgs, "Bảo đảm toàn vẹn tham chiếu giữa Hướng dẫn viên và các chuyến đi"))

    # 20 - 21: UC008
    act_20 = """
    <div class="act-node" style="width:400px;">1. Admin/Kế toán truy cập màn hình 'Thống Kê Doanh Thu'</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:460px;">2. Hệ thống tổng hợp dữ liệu từ các bảng: Payments, Bookings, Departures, Tours</div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div style="display:flex; justify-content:space-between; width:640px;">
      <div style="background:#e0f2fe; border:1.5px solid #0284c7; border-radius:8px; padding:10px; font-size:11px; width:200px; color:#0369a1; text-align:center;">
        <b>Doanh thu Top Tour:</b><br/>SUM(payments.amount) - refunds<br/>Xếp hạng theo từng tuyến tour
      </div>
      <div style="background:#dcfce7; border:1.5px solid #16a34a; border-radius:8px; padding:10px; font-size:11px; width:200px; color:#15803d; text-align:center;">
        <b>Tỷ lệ lấp đầy ghế:</b><br/>(Tổng ghế đã bán / Tổng ghế mở bán) * 100%<br/>Tỷ lệ % đã đặt vs còn trống
      </div>
      <div style="background:#fef3c7; border:1.5px solid #d97706; border-radius:8px; padding:10px; font-size:11px; width:200px; color:#b45309; text-align:center;">
        <b>Dòng tiền tổng thể:</b><br/>Tổng thực thu toàn hệ thống &<br/>Doanh thu dự kiến từ đơn PENDING
      </div>
    </div>
    <div style="width:2px; height:15px; background:#3b82f6;"></div>
    <div class="act-node" style="width:480px; background:#f0fdf4; border-color:#16a34a; color:#15803d;">
      3. Render Dashboard Chart.js:<br/>
      • Biểu đồ cột: 'Top Tour Đóng Góp Doanh Thu Cao Nhất' (Hover tooltip hiển thị số tiền)<br/>
      • Biểu đồ tròn: 'Tỷ Lệ Lấp Đầy Chỗ Ngồi' (Doughnut chart trực quan)
    </div>
    """
    export_png("20_UC008_Thong_ke_Bao_cao_Activity", get_activity_html("UC008", "Thống kê Doanh thu & Tỷ lệ lấp đầy", act_20, "Trực quan hóa chỉ số tài chính phục vụ Ban Giám Đốc ra quyết định kinh doanh"))

    seq_21_lifelines = [
        ("Accountant/Admin", "Actor", "#d97706"),
        ("StatsView", "Frontend", "#475569"),
        ("StatsRouter", "FastAPI", "#16a34a"),
        ("Database", "payments, dep, tours", "#dc2626"),
        ("ChartService", "Chart.js", "#0284c7")
    ]
    seq_21_msgs = [
        ("Accountant/Admin", "StatsView", "1. Bấm menu 'Thống Kê Doanh Thu'", False),
        ("StatsView", "StatsRouter", "2. Gửi request: GET /stats/summary & GET /stats/revenue-by-tour", False),
        ("StatsRouter", "Database", "3. Truy vấn tổng hợp: SELECT tour, SUM(amount) FROM payments...", False),
        ("StatsRouter", "Database", "4. Truy vấn số ghế: SELECT SUM(total_slots), SUM(available_slots) FROM departures", False),
        ("Database", "StatsRouter", "5. Trả về kết quả JSON {total_revenue, top_tours, occupancy_rate}", True),
        ("StatsRouter", "StatsView", "6. 200 OK -> Dữ liệu thống kê doanh thu và tỷ lệ lấp đầy", True),
        ("StatsView", "ChartService", "7. renderTopToursChart(top_tours) & renderOccupancy(occupancy_rate)", False),
        ("ChartService", "StatsView", "8. Vẽ biểu đồ cột và biểu đồ tròn hoàn tất", True),
        ("StatsView", "Accountant/Admin", "9. Hiển thị Dashboard hoàn chỉnh, hỗ trợ rê chuột (hover) xem tooltip", True)
    ]
    export_png("21_UC008_Thong_ke_Bao_cao_Sequence", get_sequence_html("UC008", "Truy vấn dữ liệu & Vẽ biểu đồ báo cáo", seq_21_lifelines, seq_21_msgs, "Chart.js vẽ biểu đồ động mượt mà; Đồng bộ dữ liệu kế toán chuẩn xác"))

    print("================================================================")
    print("HOÀN TẤT XUẤT 21 ẢNH SƠ ĐỒ UML TẠI docs/diagrams/")
    print("================================================================")

if __name__ == "__main__":
    main()
