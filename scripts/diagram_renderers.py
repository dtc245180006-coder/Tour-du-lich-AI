"""
Bộ định nghĩa HTML/SVG cho 21 sơ đồ chuẩn UML của dự án VietJourney AI.
"""

def actor_svg(fill="#e0f2fe", stroke="#0284c7"):
    return f"""
    <svg viewBox="0 0 40 70" class="actor-icon">
      <circle cx="20" cy="12" r="10" fill="{fill}" stroke="{stroke}" stroke-width="2.5" />
      <line x1="20" y1="22" x2="20" y2="45" stroke="{stroke}" stroke-width="2.5" />
      <line x1="5" y1="30" x2="35" y2="30" stroke="{stroke}" stroke-width="2.5" />
      <line x1="20" y1="45" x2="6" y2="68" stroke="{stroke}" stroke-width="2.5" />
      <line x1="20" y1="45" x2="34" y2="68" stroke="{stroke}" stroke-width="2.5" />
    </svg>
    """

# -----------------------------------------------------------------------------
# 01. USE CASE TỔNG QUÁT
# -----------------------------------------------------------------------------
def get_html_01():
    return f"""
    <div class="header">
      <div>
        <h1>01. Sơ Đồ Use Case Tổng Quát (General Use Case Diagram)</h1>
        <div class="sub">Hệ thống Quản lý Tour Du Lịch có tích hợp AI - VietJourney AI | Chuẩn UML 2.5</div>
      </div>
      <div class="badge">UC001 - UC008</div>
    </div>
    <div style="display:flex; justify-content:space-between; height:780px; position:relative; margin-top:20px;">
      <!-- Left Actors -->
      <div style="width:160px; display:flex; flex-direction:column; justify-content:space-around;">
        <div class="actor-box">
          {actor_svg("#e0f2fe", "#0284c7")}
          <div>Khách vãng lai<br/><span style="font-weight:normal;color:#64748b;">(Guest)</span></div>
        </div>
        <div class="actor-box">
          {actor_svg("#dcfce7", "#16a34a")}
          <div>Nhân viên tư vấn<br/><span style="font-weight:normal;color:#64748b;">(Consultant)</span></div>
        </div>
      </div>

      <!-- System Boundary -->
      <div class="boundary" style="flex:1; margin:0 30px; padding:30px 20px; display:flex; flex-direction:column; justify-content:space-between;">
        <div class="boundary-title">Hệ thống Quản lý Tour Du Lịch VietJourney AI</div>
        
        <div style="display:flex; justify-content:center;">
          <div class="usecase" style="width:360px;">UC001: Đăng nhập & Xác thực phân quyền (RBAC)</div>
        </div>

        <div style="display:flex; justify-content:space-around; align-items:center;">
          <div class="usecase" style="width:280px;">UC002: Quản lý danh mục Tour (CRUD)</div>
          <div style="color:#0284c7; font-size:11px; font-weight:bold;">&laquo;include&raquo; &rarr;</div>
          <div class="usecase sub" style="width:280px;">UC002.1: AI sinh mô tả & tóm tắt lịch trình</div>
        </div>

        <div style="display:flex; justify-content:center;">
          <div class="usecase" style="width:360px;">UC003: Quản lý Lịch khởi hành & Chỗ trống</div>
        </div>

        <div style="display:flex; justify-content:space-around; align-items:center;">
          <div class="usecase" style="width:280px;">UC004: Khách hàng & Quản lý Đặt chỗ</div>
          <div style="display:flex; flex-direction:column; gap:6px;">
            <div style="color:#0284c7; font-size:11px; font-weight:bold;">&laquo;include&raquo; &rarr; UC004.1 Xử lý hàng chờ tư vấn</div>
            <div style="color:#d97706; font-size:11px; font-weight:bold;">&laquo;extend&raquo; &larr; UC004.2 AI tư vấn tour thông minh (RAG)</div>
          </div>
        </div>

        <div style="display:flex; justify-content:space-around; align-items:center;">
          <div class="usecase" style="width:280px;">UC005: Quản lý Thanh toán & Đặt cọc</div>
          <div style="color:#d97706; font-size:11px; font-weight:bold;">&laquo;extend&raquo; &larr;</div>
          <div class="usecase sub" style="width:280px;">UC005.1: Xử lý hoàn tiền khi hủy tour (REFUND)</div>
        </div>

        <div style="display:flex; justify-content:space-around; align-items:center;">
          <div class="usecase" style="width:280px;">UC006: Quản lý Đánh giá & Phản hồi</div>
          <div style="color:#0284c7; font-size:11px; font-weight:bold;">&laquo;include&raquo; &rarr;</div>
          <div class="usecase sub" style="width:280px;">UC006.1: AI phân tích cảm xúc & Tóm tắt review</div>
        </div>

        <div style="display:flex; justify-content:space-around;">
          <div class="usecase" style="width:280px;">UC007: Quản lý Hướng dẫn viên</div>
          <div class="usecase" style="width:280px;">UC008: Thống kê & Báo cáo doanh thu</div>
        </div>
      </div>

      <!-- Right Actors -->
      <div style="width:160px; display:flex; flex-direction:column; justify-content:space-around;">
        <div class="actor-box">
          {actor_svg("#fee2e2", "#dc2626")}
          <div>Quản trị viên<br/><span style="font-weight:normal;color:#64748b;">(Admin)</span></div>
        </div>
        <div class="actor-box">
          {actor_svg("#fef3c7", "#d97706")}
          <div>Kế toán<br/><span style="font-weight:normal;color:#64748b;">(Accountant)</span></div>
        </div>
        <div style="border:2px solid #9333ea; border-radius:10px; background:#faf5ff; padding:8px 4px; text-align:center; font-size:11px; font-weight:bold; color:#6b21a8;">
          &laquo;External System&raquo;<br/>
          <b>Google Gemini AI Engine</b>
        </div>
      </div>
    </div>
    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>Ghi chú: Consultant không thu tiền; Kế toán & Admin xử lý tài chính; Khách vãng lai gửi yêu cầu ở trạng thái WAITING_CONFIRM</div>
    </div>
    """

# -----------------------------------------------------------------------------
# 02. PHÂN CẤP CHỨC NĂNG
# -----------------------------------------------------------------------------
def get_html_02():
    return f"""
    <div class="header">
      <div>
        <h1>02. Sơ Đồ Phân Cấp Chức Năng (Functional Decomposition Diagram)</h1>
        <div class="sub">Cấu trúc phân rã chức năng toàn diện của hệ thống VietJourney AI</div>
      </div>
      <div class="badge">4 Phân hệ chính</div>
    </div>
    <div style="display:flex; flex-direction:column; align-items:center; height:800px; padding-top:10px;">
      <!-- Root Box -->
      <div style="background:#0f172a; color:#ffffff; padding:16px 36px; border-radius:10px; font-size:16px; font-weight:bold; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.15);">
        HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)
      </div>
      <div style="width:2px; height:30px; background:#64748b;"></div>
      <div style="width:1150px; height:2px; background:#64748b;"></div>

      <!-- 4 Columns -->
      <div style="display:flex; justify-content:space-between; width:1250px; margin-top:0;">
        <!-- Col 1 -->
        <div style="display:flex; flex-direction:column; align-items:center; width:285px;">
          <div style="width:2px; height:25px; background:#64748b;"></div>
          <div style="background:#e0f2fe; border:2px solid #0284c7; color:#0369a1; padding:10px 14px; border-radius:8px; font-weight:bold; font-size:12.5px; text-align:center; width:100%;">
            1. PHÂN HỆ KHÁCH HÀNG & BÁN LẺ<br/><span style="font-size:11px;font-weight:normal;color:#0284c7;">(Khách vãng lai)</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; margin-top:14px; width:100%;">
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #0284c7; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">1.1 Tra cứu danh mục tour & lộ trình</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #9333ea; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">1.2 Trợ lý AI tư vấn thông minh (RAG)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #0284c7; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">1.3 Gửi yêu cầu đặt tour (WAITING_CONFIRM)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #0284c7; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">1.4 Gửi phản hồi & đánh giá chuyến đi</div>
          </div>
        </div>

        <!-- Col 2 -->
        <div style="display:flex; flex-direction:column; align-items:center; width:285px;">
          <div style="width:2px; height:25px; background:#64748b;"></div>
          <div style="background:#dcfce7; border:2px solid #16a34a; color:#15803d; padding:10px 14px; border-radius:8px; font-weight:bold; font-size:12.5px; text-align:center; width:100%;">
            2. PHÂN HỆ TƯ VẤN & BÁN HÀNG<br/><span style="font-size:11px;font-weight:normal;color:#16a34a;">(Nhân viên tư vấn)</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; margin-top:14px; width:100%;">
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #16a34a; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">2.1 Tiếp nhận & duyệt hàng chờ tư vấn</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #16a34a; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">2.2 Quản lý hồ sơ khách hàng & lịch sử</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #16a34a; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">2.3 Giữ chỗ & Khóa ghế (Pessimistic Lock)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #ef4444; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">2.4 Hủy booking & Hoàn trả số chỗ trống</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #16a34a; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">2.5 Giám sát lịch khởi hành & chỗ trống</div>
          </div>
        </div>

        <!-- Col 3 -->
        <div style="display:flex; flex-direction:column; align-items:center; width:285px;">
          <div style="width:2px; height:25px; background:#64748b;"></div>
          <div style="background:#fee2e2; border:2px solid #dc2626; color:#b91c1c; padding:10px 14px; border-radius:8px; font-weight:bold; font-size:12.5px; text-align:center; width:100%;">
            3. PHÂN HỆ QUẢN TRỊ VẬN HÀNH<br/><span style="font-size:11px;font-weight:normal;color:#dc2626;">(Quản trị viên Admin)</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; margin-top:14px; width:100%;">
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #dc2626; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.1 Quản lý Tour (CRUD) & Điểm đến</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #9333ea; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.2 AI Gemini tự động sinh mô tả tour</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #dc2626; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.3 Quản lý Lịch khởi hành & Gán HDV</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #dc2626; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.4 Quản lý hồ sơ Hướng dẫn viên</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #dc2626; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.5 Phân quyền tài khoản bảo mật (RBAC)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #9333ea; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">3.6 AI phân tích & tóm tắt phản hồi du khách</div>
          </div>
        </div>

        <!-- Col 4 -->
        <div style="display:flex; flex-direction:column; align-items:center; width:285px;">
          <div style="width:2px; height:25px; background:#64748b;"></div>
          <div style="background:#fef3c7; border:2px solid #d97706; color:#b45309; padding:10px 14px; border-radius:8px; font-weight:bold; font-size:12.5px; text-align:center; width:100%;">
            4. PHÂN HỆ KẾ TOÁN & TÀI CHÍNH<br/><span style="font-size:11px;font-weight:normal;color:#d97706;">(Kế toán & Ban Quản lý)</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; margin-top:14px; width:100%;">
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #d97706; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.1 Lập phiếu thu & Quản lý giao dịch</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #d97706; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.2 Thu tiền cọc (>= 30% -> DEPOSITED)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #16a34a; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.3 Thu đủ 100% vé (-> CONFIRMED)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #ef4444; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.4 Xử lý hoàn tiền khi hủy (REFUND)</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #d97706; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.5 Báo cáo Top Tour doanh thu cao nhất</div>
            <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-left:4px solid #d97706; padding:9px 12px; border-radius:6px; font-size:11.5px; color:#334155;">4.6 Thống kê Tỷ lệ lấp đầy chỗ ngồi</div>
          </div>
        </div>
      </div>
    </div>
    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>Phân định rõ ràng: Consultant KHÔNG thu tiền; Tài chính hoàn toàn thuộc Kế toán và Admin</div>
    </div>
    """

# -----------------------------------------------------------------------------
# 03. SƠ ĐỒ LỚP (CLASS DIAGRAM)
# -----------------------------------------------------------------------------
def get_html_03():
    return f"""
    <div class="header">
      <div>
        <h1>03. Sơ Đồ Lớp Chi Tiết (UML Class Diagram - Chuẩn OOP 3 Lớp)</h1>
        <div class="sub">10 Thực thể CSDL, Enums, Controller Routers và Logic Services</div>
      </div>
      <div class="badge">models.py & schemas.py</div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:14px; margin-top:10px;">
      
      <!-- Tour -->
      <div class="uml-class">
        <div class="c-head">Tour</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ code</b>: str [UK]<br/>
          + title: str<br/>
          + destination: str<br/>
          + category: str<br/>
          + duration_days: int<br/>
          + duration_nights: int<br/>
          + base_price: Decimal<br/>
          + description: str<br/>
          + is_active: bool
        </div>
        <div class="c-methods">
          + create()<br/>
          + update()<br/>
          + generate_ai_desc()
        </div>
      </div>

      <!-- Departure -->
      <div class="uml-class">
        <div class="c-head">Departure</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ tour_id</b>: int [FK]<br/>
          + departure_date: date<br/>
          + return_date: date<br/>
          + total_slots: int<br/>
          + available_slots: int<br/>
          + price_override: Decimal<br/>
          <b>+ guide_id</b>: int [FK]<br/>
          + status: DepStatus
        </div>
        <div class="c-methods">
          + lock_slots(qty)<br/>
          + release_slots(qty)<br/>
          + start_trip()<br/>
          + complete_trip()
        </div>
      </div>

      <!-- TourGuide -->
      <div class="uml-class">
        <div class="c-head">TourGuide</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          + full_name: str<br/>
          + phone: str<br/>
          + email: str<br/>
          + languages: str<br/>
          + experience_years: int<br/>
          + status: GuideStatus<br/>
          + rating: float
        </div>
        <div class="c-methods">
          + check_conflict(d1, d2)<br/>
          + assign_to_trip()
        </div>
      </div>

      <!-- Customer -->
      <div class="uml-class">
        <div class="c-head">Customer</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          + full_name: str<br/>
          <b>+ phone</b>: str [UK]<br/>
          + email: str<br/>
          + id_card: str<br/>
          + address: str
        </div>
        <div class="c-methods">
          + get_or_create()<br/>
          + get_booking_history()
        </div>
      </div>

      <!-- Booking -->
      <div class="uml-class">
        <div class="c-head">Booking</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ booking_code</b>: str [UK]<br/>
          <b>+ departure_id</b>: int [FK]<br/>
          <b>+ customer_id</b>: int [FK]<br/>
          + num_people: int<br/>
          + total_amount: Decimal<br/>
          + deposit_amount: Decimal<br/>
          + paid_amount: Decimal<br/>
          + status: BookingStatus<br/>
          + refund_amount: Decimal
        </div>
        <div class="c-methods">
          + confirm_booking()<br/>
          + cancel_and_refund()
        </div>
      </div>

      <!-- Payment -->
      <div class="uml-class">
        <div class="c-head">Payment</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ booking_id</b>: int [FK]<br/>
          + payment_type: str<br/>
          + amount: Decimal (VNĐ)<br/>
          + payment_method: str<br/>
          + status: str<br/>
          <b>+ transaction_code</b>: str [UK]<br/>
          + created_by: str
        </div>
        <div class="c-methods">
          + record_payment()<br/>
          + print_receipt()
        </div>
      </div>

      <!-- User -->
      <div class="uml-class">
        <div class="c-head">User</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ username</b>: str [UK]<br/>
          + hashed_password: str<br/>
          + full_name: str<br/>
          + email: str<br/>
          + role: UserRole<br/>
          + is_active: bool
        </div>
        <div class="c-methods">
          + verify_password()<br/>
          + check_role(role)
        </div>
      </div>

      <!-- Feedback -->
      <div class="uml-class">
        <div class="c-head">Feedback</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          <b>+ tour_id</b>: int [FK]<br/>
          <b>+ booking_id</b>: int [FK]<br/>
          + customer_name: str<br/>
          + rating: int (1-5)<br/>
          + comments: str<br/>
          + guide_rating: int (1-5)<br/>
          + sentiment: SentimentType
        </div>
        <div class="c-methods">
          + analyze_sentiment()
        </div>
      </div>

      <!-- AISessionLog -->
      <div class="uml-class">
        <div class="c-head">AISessionLog</div>
        <div class="c-body">
          <b>+ id</b>: int [PK]<br/>
          + feature_type: str<br/>
          + input_prompt: str<br/>
          + response_content: str<br/>
          + model_name: str<br/>
          + created_at: datetime
        </div>
        <div class="c-methods">
          + log_interaction()
        </div>
      </div>

      <!-- BookingRequestKey -->
      <div class="uml-class">
        <div class="c-head">BookingRequestKey</div>
        <div class="c-body">
          <b>+ key</b>: str [PK]<br/>
          + fingerprint: str<br/>
          <b>+ booking_id</b>: int [FK]
        </div>
        <div class="c-methods">
          + check_duplicate()<br/>
          + store_idempotency()
        </div>
      </div>

    </div>

    <!-- Routers and Services Footer Box -->
    <div style="margin-top:16px; display:grid; grid-template-columns:1fr 1fr; gap:16px;">
      <div style="background:#f1f5f9; border:1.5px solid #94a3b8; border-radius:8px; padding:12px; font-size:11.5px;">
        <b style="color:#0f172a; font-size:12.5px;">API Routers (Controllers):</b><br/>
        AuthRouter (/auth), TourRouter (/tours), DepartureRouter (/departures), BookingRouter (/bookings), PaymentRouter (/payments), GuideRouter (/guides), FeedbackRouter (/feedbacks), AIRouter (/ai), StatsRouter (/stats).
      </div>
      <div style="background:#f1f5f9; border:1.5px solid #94a3b8; border-radius:8px; padding:12px; font-size:11.5px;">
        <b style="color:#0f172a; font-size:12.5px;">Service & Business Layer:</b><br/>
        <b>AIService</b> (Gemini RAG, Viết mô tả, Tóm tắt review) | <b>BookingService</b> (Khóa bi quan Pessimistic lock, Trừ ghế, Chống gửi lặp) | <b>PaymentService</b> (Tính cọc 30%, Thu đủ 100%, Hoàn tiền khi hủy).
      </div>
    </div>

    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>Quan hệ: Tour &diams;&mdash;* Departure | Departure *&mdash;1 Guide | Departure 1&mdash;* Booking &diams;&mdash;* Payment | Customer 1&mdash;* Booking</div>
    </div>
    """

# -----------------------------------------------------------------------------
# 04. SƠ ĐỒ CSDL ERD (10 BẢNG)
# -----------------------------------------------------------------------------
def get_html_04():
    return f"""
    <div class="header">
      <div>
        <h1>04. Sơ Đồ Thực Thể Liên Kết CSDL (ERD - 10 Bảng Chuẩn Hóa 3NF)</h1>
        <div class="sub">Quan hệ chuẩn Crow's Foot - Khóa chính (PK), Khóa ngoại (FK), Khóa duy nhất (UK)</div>
      </div>
      <div class="badge">SQLite / MySQL</div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; margin-top:10px;">
      
      <!-- Users -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">users</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#0284c7;">UK</b> username: VARCHAR(50)<br/>
          hashed_password: VARCHAR(255)<br/>
          full_name: VARCHAR(100)<br/>
          email: VARCHAR(100)<br/>
          phone: VARCHAR(20)<br/>
          role: VARCHAR(20)<br/>
          is_active: BOOLEAN<br/>
          created_at: DATETIME
        </div>
      </div>

      <!-- Tours -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">tours</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#0284c7;">UK</b> code: VARCHAR(20)<br/>
          title: VARCHAR(255)<br/>
          destination: VARCHAR(100)<br/>
          category: VARCHAR(50)<br/>
          duration_days: INTEGER<br/>
          duration_nights: INTEGER<br/>
          base_price: DECIMAL(18,0)<br/>
          description: TEXT<br/>
          itinerary_summary: TEXT<br/>
          is_active: BOOLEAN
        </div>
      </div>

      <!-- Departures -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">departures</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#16a34a;">FK</b> tour_id: INTEGER<br/>
          departure_date: DATE<br/>
          return_date: DATE<br/>
          total_slots: INTEGER<br/>
          available_slots: INTEGER<br/>
          price_override: DECIMAL<br/>
          <b style="color:#16a34a;">FK</b> guide_id: INTEGER<br/>
          status: VARCHAR(20)<br/>
          notes: TEXT
        </div>
      </div>

      <!-- TourGuides -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">tour_guides</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          full_name: VARCHAR(100)<br/>
          phone: VARCHAR(20)<br/>
          email: VARCHAR(100)<br/>
          languages: VARCHAR(100)<br/>
          experience_years: INTEGER<br/>
          status: VARCHAR(20)<br/>
          rating: FLOAT<br/>
          notes: TEXT
        </div>
      </div>

      <!-- Customers -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">customers</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          full_name: VARCHAR(100)<br/>
          <b style="color:#0284c7;">UK</b> phone: VARCHAR(20)<br/>
          email: VARCHAR(100)<br/>
          id_card: VARCHAR(20)<br/>
          address: VARCHAR(255)<br/>
          notes: TEXT<br/>
          created_at: DATETIME
        </div>
      </div>

      <!-- Bookings -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">bookings</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#0284c7;">UK</b> booking_code: VARCHAR(30)<br/>
          <b style="color:#16a34a;">FK</b> departure_id: INTEGER<br/>
          <b style="color:#16a34a;">FK</b> customer_id: INTEGER<br/>
          num_people: INTEGER<br/>
          total_amount: DECIMAL(18,0)<br/>
          deposit_amount: DECIMAL(18,0)<br/>
          paid_amount: DECIMAL(18,0)<br/>
          status: VARCHAR(20)<br/>
          refund_amount: DECIMAL(18,0)
        </div>
      </div>

      <!-- Payments -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">payments</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#16a34a;">FK</b> booking_id: INTEGER<br/>
          payment_type: VARCHAR(30)<br/>
          amount: DECIMAL(18,0)<br/>
          payment_method: VARCHAR(30)<br/>
          status: VARCHAR(20)<br/>
          <b style="color:#0284c7;">UK</b> transaction_code: VARCHAR(50)<br/>
          note: TEXT<br/>
          created_by: VARCHAR(100)
        </div>
      </div>

      <!-- Feedbacks -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">feedbacks</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          <b style="color:#16a34a;">FK</b> tour_id: INTEGER<br/>
          <b style="color:#16a34a;">FK</b> booking_id: INTEGER<br/>
          customer_name: VARCHAR(100)<br/>
          rating: INTEGER (1-5)<br/>
          comments: TEXT<br/>
          guide_rating: INTEGER (1-5)<br/>
          sentiment: VARCHAR(20)
        </div>
      </div>

      <!-- AISessionLogs -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">ai_session_logs</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> id: INTEGER<br/>
          feature_type: VARCHAR(50)<br/>
          input_prompt: TEXT<br/>
          response_content: TEXT<br/>
          model_name: VARCHAR(50)<br/>
          created_at: DATETIME
        </div>
      </div>

      <!-- BookingRequestKeys -->
      <div class="uml-class" style="border-color:#334155;">
        <div class="c-head" style="background:#f1f5f9; color:#0f172a; border-color:#334155;">booking_request_keys</div>
        <div class="c-body" style="font-size:10.5px;">
          <b style="color:#dc2626;">PK</b> key: VARCHAR(64)<br/>
          fingerprint: VARCHAR(128)<br/>
          <b style="color:#16a34a;">FK</b> booking_id: INTEGER
        </div>
      </div>

    </div>

    <!-- Cardinality relationships footer -->
    <div style="margin-top:20px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; font-size:11.5px; line-height:1.6;">
      <b>Bản đồ quan hệ & Ràng buộc toàn vẹn (Cardinalities):</b><br/>
      • <b>tours (1) &mdash;&lt; departures (N)</b>: Khóa ngoại departures.tour_id &rarr; tours.id (ON DELETE RESTRICT)<br/>
      • <b>tour_guides (1) &mdash;&lt; departures (N)</b>: Khóa ngoại departures.guide_id &rarr; tour_guides.id<br/>
      • <b>departures (1) &mdash;&lt; bookings (N)</b>: Khóa ngoại bookings.departure_id &rarr; departures.id<br/>
      • <b>customers (1) &mdash;&lt; bookings (N)</b>: Khóa ngoại bookings.customer_id &rarr; customers.id (phone định danh duy nhất UK)<br/>
      • <b>bookings (1) &mdash;&lt; payments (N)</b>: Khóa ngoại payments.booking_id &rarr; bookings.id<br/>
      • <b>tours (1) &mdash;&lt; feedbacks (N)</b> & <b>bookings (1) &mdash;&lt; feedbacks (N)</b>: Đánh giá gắn liền với tour và chuyến đi<br/>
      • <b>bookings (1) &mdash; (1) booking_request_keys</b>: Chống race condition & trùng lặp khi đặt chỗ
    </div>

    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>Đầy đủ 10 bảng dữ liệu cốt lõi đã kiểm chứng trực tiếp trong backend/app/models.py</div>
    </div>
    """

# -----------------------------------------------------------------------------
# 05. LUỒNG MÀN HÌNH (SCREEN FLOW)
# -----------------------------------------------------------------------------
def get_html_05():
    return f"""
    <div class="header">
      <div>
        <h1>05. Sơ Đồ Phân Luồng Màn Hình (Screen Flow Diagram)</h1>
        <div class="sub">Hành trình giao diện từ Khách vãng lai đến 3 vai trò phân quyền (RBAC)</div>
      </div>
      <div class="badge">Frontend UI Architecture</div>
    </div>
    <div style="display:flex; justify-content:space-between; height:780px; margin-top:20px;">
      
      <!-- Guest UI -->
      <div style="width:260px; display:flex; flex-direction:column; gap:16px;">
        <div style="font-weight:bold; color:#0369a1; border-bottom:2px solid #0284c7; padding-bottom:4px;">1. GIAO DIỆN KHÁCH VÃNG LAI</div>
        <div style="background:#ffffff; border:2px solid #0284c7; border-radius:10px; padding:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
          <b style="color:#0284c7;">Trang chủ Tour (tours.html)</b><br/>
          <span style="font-size:11px;color:#64748b;">Xem danh mục tour, tìm kiếm điểm đến, xem bảng giá niêm yết</span>
        </div>
        <div style="background:#ffffff; border:2px solid #9333ea; border-radius:10px; padding:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
          <b style="color:#9333ea;">Trợ lý AI Gemini (Drawer)</b><br/>
          <span style="font-size:11px;color:#64748b;">Chat tư vấn tour thông minh theo số ngày và ngân sách</span>
        </div>
        <div style="background:#ffffff; border:2px solid #d97706; border-radius:10px; padding:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
          <b style="color:#d97706;">Modal Đặt Tour Nhanh</b><br/>
          <span style="font-size:11px;color:#64748b;">Gửi yêu cầu tour &rarr; Lưu đơn WAITING_CONFIRM (Chưa giữ chỗ)</span>
        </div>
        <div style="background:#ffffff; border:2px solid #dc2626; border-radius:10px; padding:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
          <b style="color:#dc2626;">Màn hình Đăng Nhập (login.html)</b><br/>
          <span style="font-size:11px;color:#64748b;">Nhập tài khoản nhân viên &rarr; Xác thực cấp JWT Token</span>
        </div>
      </div>

      <!-- Arrow middle -->
      <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; width:80px;">
        <div style="background:#1e293b; color:#ffffff; padding:10px; border-radius:50%; font-size:16px;">&rarr;</div>
        <div style="font-size:11px; font-weight:bold; color:#475569; margin-top:8px; text-align:center;">Phân quyền RBAC</div>
      </div>

      <!-- 3 RBAC Branches -->
      <div style="flex:1; display:flex; flex-direction:column; gap:16px;">
        
        <!-- Consultant -->
        <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:10px; padding:14px;">
          <b style="color:#15803d; font-size:13px;">NHÂN VIÊN TƯ VẤN (CONSULTANT)</b>
          <div style="display:flex; gap:12px; margin-top:8px;">
            <div style="background:#ffffff; border:1px solid #86efac; border-radius:6px; padding:8px 12px; flex:1; font-size:11.5px;">
              <b>Hàng Chờ Tư Vấn (consultations.html)</b><br/>
              Xem đơn chờ duyệt &rarr; Bấm "Xác nhận giữ chỗ" (chuyển PENDING, trừ số ghế) hoặc "Từ chối"
            </div>
            <div style="background:#ffffff; border:1px solid #86efac; border-radius:6px; padding:8px 12px; flex:1; font-size:11.5px;">
              <b>Quản lý Đặt Chỗ (bookings.html)</b><br/>
              Theo dõi tình trạng đơn hàng; Thao tác "Hủy đơn" (hoàn lại ghế trống). <i>Không có nút thu tiền!</i>
            </div>
          </div>
        </div>

        <!-- Accountant -->
        <div style="background:#fffbeb; border:2px solid #d97706; border-radius:10px; padding:14px;">
          <b style="color:#b45309; font-size:13px;">KẾ TOÁN (ACCOUNTANT)</b>
          <div style="display:flex; gap:12px; margin-top:8px;">
            <div style="background:#ffffff; border:1px solid #fde68a; border-radius:6px; padding:8px 12px; flex:1; font-size:11.5px;">
              <b>Kế Toán & Thu Tiền (payments.html)</b><br/>
              Mở modal "Thu tiền" &rarr; Nhập số tiền, cọc (&ge;30% &rarr; DEPOSITED), thu đủ (100% &rarr; CONFIRMED), lập phiếu hoàn tiền khi hủy
            </div>
            <div style="background:#ffffff; border:1px solid #fde68a; border-radius:6px; padding:8px 12px; flex:1; font-size:11.5px;">
              <b>Thống Kê Doanh Thu (stats.html)</b><br/>
              Biểu đồ cột Top Tour, Biểu đồ tròn Tỷ lệ lấp đầy ghế ngồi, Đối soát dòng tiền thực thu
            </div>
          </div>
        </div>

        <!-- Admin -->
        <div style="background:#fef2f2; border:2px solid #dc2626; border-radius:10px; padding:14px;">
          <b style="color:#b91c1c; font-size:13px;">QUẢN TRỊ VIÊN (ADMIN - TOÀN QUYỀN)</b>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:8px;">
            <div style="background:#ffffff; border:1px solid #fca5a5; border-radius:6px; padding:8px 12px; font-size:11px;">
              <b>Quản lý Tour (tours_admin.html)</b>: Thêm/Sửa/Xóa tour; Kích hoạt AI viết mô tả
            </div>
            <div style="background:#ffffff; border:1px solid #fca5a5; border-radius:6px; padding:8px 12px; font-size:11px;">
              <b>Lịch Khởi Hành (departures.html)</b>: Mở đợt mới, Start (RUNNING), Complete chuyến đi
            </div>
            <div style="background:#ffffff; border:1px solid #fca5a5; border-radius:6px; padding:8px 12px; font-size:11px;">
              <b>Hướng Dẫn Viên (guides.html)</b>: Quản lý hồ sơ, điều phối nhân sự, thẻ HDV
            </div>
            <div style="background:#ffffff; border:1px solid #fca5a5; border-radius:6px; padding:8px 12px; font-size:11px;">
              <b>AI Hub & Phản hồi (ai_hub.html)</b>: AI tóm tắt đánh giá, phân tích cảm xúc sentiment
            </div>
          </div>
        </div>

      </div>
    </div>
    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>Khách gửi yêu cầu chưa giữ chỗ; Nhân viên duyệt mới trừ ghế; Kế toán thu tiền độc lập</div>
    </div>
    """

# -----------------------------------------------------------------------------
# HELPER CHO ACTIVITY & SEQUENCE DIAGRAMS (UC001 -> UC008)
# -----------------------------------------------------------------------------
def get_activity_html(uc_code, uc_name, steps_html, note=""):
    return f"""
    <div class="header">
      <div>
        <h1>{uc_code}: {uc_name} (Activity Diagram)</h1>
        <div class="sub">Biểu đồ hoạt động mô tả luồng điều khiển, rẽ nhánh điều kiện và xử lý ngoại lệ</div>
      </div>
      <div class="badge">UML Activity</div>
    </div>
    <div style="display:flex; flex-direction:column; align-items:center; height:780px; justify-content:space-around; padding:10px 0;">
      <div style="width:28px; height:28px; background:#0f172a; border-radius:50%;"></div>
      {steps_html}
      <div style="width:30px; height:30px; border:2.5px solid #ef4444; border-radius:50%; display:flex; align-items:center; justify-content:center;">
        <div style="width:16px; height:16px; background:#0f172a; border-radius:50%;"></div>
      </div>
    </div>
    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>{note}</div>
    </div>
    """

def get_sequence_html(uc_code, uc_name, lifelines, messages, note=""):
    lifeline_html = ""
    for name, role, color in lifelines:
        lifeline_html += f"""
        <div style="flex:1; display:flex; flex-direction:column; align-items:center; position:relative;">
          <div class="seq-head" style="border-color:{color}; color:{color}; width:160px;">{name}<br/><span style="font-size:10px;font-weight:normal;color:#64748b;">({role})</span></div>
          <div class="seq-line"></div>
        </div>
        """
    msg_html = ""
    for idx, (sender, receiver, msg, is_ret) in enumerate(messages):
        arrow = "&dash;&dash;&gt;" if is_ret else "&mdash;&mdash;&gt;"
        color = "#64748b" if is_ret else "#0f172a"
        style_font = "font-style:italic;" if is_ret else "font-weight:600;"
        msg_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:7px 16px; margin:4px 0; background:rgba(255,255,255,0.85); border:1px solid #e2e8f0; border-radius:6px; font-size:11.5px; color:{color}; {style_font}">
          <span style="font-weight:bold; color:#0369a1; width:25px;">{idx+1}.</span>
          <span style="flex:1; text-align:left; margin-left:10px;">{msg}</span>
          <span style="font-size:10.5px; color:#64748b; background:#f1f5f9; padding:2px 8px; border-radius:4px;">{sender} &rarr; {receiver}</span>
        </div>
        """

    return f"""
    <div class="header">
      <div>
        <h1>{uc_code}: {uc_name} (Sequence Diagram)</h1>
        <div class="sub">Biểu đồ tuần tự thể hiện thông điệp trao đổi giữa Actor, View, Controller và CSDL</div>
      </div>
      <div class="badge">UML Sequence</div>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom:14px; position:relative; z-index:2;">
      {lifeline_html}
    </div>
    <div style="background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:10px; padding:14px; max-height:680px; overflow-y:hidden; position:relative; z-index:10;">
      {msg_html}
    </div>
    <div class="footer">
      <div>Đồ án: Kỹ nghệ phần mềm ứng dụng AI - Nhóm 17</div>
      <div>{note}</div>
    </div>
    """
