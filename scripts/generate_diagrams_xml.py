"""
Script tạo file Draw.io Multi-page chứa toàn bộ 21 sơ đồ chuẩn UML cho dự án VietJourney AI.
Tất cả sơ đồ phản ánh chính xác 100% mã nguồn thực tế (FastAPI, 10 bảng CSDL, RBAC, Gemini AI).
"""

import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import xml.etree.ElementTree as ET
from drawio_builder import DrawioFile

def build_drawio_file():
    df = DrawioFile()

    # =========================================================================
    # 01. SƠ ĐỒ USE CASE TỔNG QUÁT
    # =========================================================================
    p1 = df.add_page("p01_use_case", "01. Sơ đồ Use Case tổng quát")
    # Title
    p1.add_vertex("t1", "<b>HỆ THỐNG QUẢN LÝ TOUR DU LỊCH VIETJOURNEY AI - USE CASE TỔNG QUÁT</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 20, 1000, 40)
    
    # Boundary
    p1.add_vertex("bound", "Hệ thống Quản lý Tour Du Lịch VietJourney AI",
                  "shape=rect;rounded=0;whiteSpace=wrap;html=1;fillColor=#f8fafc;strokeColor=#64748b;strokeWidth=2;dashed=1;verticalAlign=top;align=left;spacingLeft=20;spacingTop=12;fontStyle=1;fontSize=14;fontColor=#1e293b;",
                  220, 70, 1100, 1020)
    
    # Actors Left
    p1.add_vertex("act_guest", "Khách vãng lai<br/>(Guest)",
                  "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#e0f2fe;strokeColor=#0284c7;strokeWidth=2;fontSize=12;fontStyle=1;",
                  60, 220, 60, 110)
    
    p1.add_vertex("act_consultant", "Nhân viên tư vấn<br/>(Consultant)",
                  "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#dcfce7;strokeColor=#16a34a;strokeWidth=2;fontSize=12;fontStyle=1;",
                  60, 580, 60, 110)
    
    # Actors Right
    p1.add_vertex("act_admin", "Quản trị viên<br/>(Admin)",
                  "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#fee2e2;strokeColor=#dc2626;strokeWidth=2;fontSize=12;fontStyle=1;",
                  1420, 220, 60, 110)
    
    p1.add_vertex("act_accountant", "Kế toán<br/>(Accountant)",
                  "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=2;fontSize=12;fontStyle=1;",
                  1420, 580, 60, 110)
    
    p1.add_vertex("act_ai", "&laquo;External System&raquo;<br/><b>Google Gemini AI Engine</b>",
                  "shape=rect;rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e8ff;strokeColor=#9333ea;strokeWidth=2;fontSize=12;fontStyle=1;align=center;",
                  1370, 850, 160, 70)

    # Use cases
    uc_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0284c7;strokeWidth=2;fontSize=12;fontStyle=1;align=center;"
    uc_sub_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#f0f9ff;strokeColor=#0369a1;strokeWidth=1.5;strokeDashed=1;fontSize=11;fontStyle=2;align=center;"

    p1.add_vertex("uc1", "UC001: Đăng nhập & Xác thực phân quyền (RBAC)", uc_style, 560, 100, 260, 60)
    
    p1.add_vertex("uc2", "UC002: Quản lý danh mục Tour (CRUD)", uc_style, 400, 210, 240, 60)
    p1.add_vertex("uc2_1", "UC002.1: AI sinh mô tả & lịch trình tour", uc_sub_style, 760, 210, 230, 55)
    
    p1.add_vertex("uc3", "UC003: Quản lý Lịch khởi hành & Chỗ trống", uc_style, 400, 320, 240, 60)
    
    p1.add_vertex("uc4", "UC004: Khách hàng & Quản lý Đặt chỗ", uc_style, 400, 440, 250, 65)
    p1.add_vertex("uc4_1", "UC004.1: Xử lý hàng chờ tư vấn", uc_sub_style, 760, 420, 210, 55)
    p1.add_vertex("uc4_2", "UC004.2: AI tư vấn tour thông minh (RAG)", uc_sub_style, 760, 500, 220, 55)
    
    p1.add_vertex("uc5", "UC005: Quản lý Thanh toán & Đặt cọc", uc_style, 400, 610, 240, 60)
    p1.add_vertex("uc5_1", "UC005.1: Xử lý hoàn tiền khi hủy tour", uc_sub_style, 760, 610, 220, 55)
    
    p1.add_vertex("uc6", "UC006: Quản lý Đánh giá & Phản hồi", uc_style, 400, 740, 240, 60)
    p1.add_vertex("uc6_1", "UC006.1: AI tóm tắt phản hồi & Sentiment", uc_sub_style, 760, 740, 230, 55)
    
    p1.add_vertex("uc7", "UC007: Quản lý Hướng dẫn viên", uc_style, 400, 870, 240, 60)
    p1.add_vertex("uc8", "UC008: Thống kê & Báo cáo doanh thu", uc_style, 400, 980, 250, 65)

    # Edges - Associations
    solid_edge = "endArrow=none;html=1;strokeColor=#334155;strokeWidth=1.5;"
    inc_edge = "endArrow=open;dashed=1;html=1;strokeColor=#0284c7;strokeWidth=1.5;endFill=0;fontSize=10;fontColor=#0284c7;"
    ext_edge = "endArrow=open;dashed=1;html=1;strokeColor=#d97706;strokeWidth=1.5;endFill=0;fontSize=10;fontColor=#d97706;"
    ai_edge = "endArrow=open;dashed=1;html=1;strokeColor=#9333ea;strokeWidth=1.5;endFill=0;"

    # Guest connections
    p1.add_edge("e_g_uc4", "", solid_edge, "act_guest", "uc4")
    p1.add_edge("e_g_uc6", "", solid_edge, "act_guest", "uc6")
    p1.add_edge("e_g_uc4_2", "", solid_edge, "act_guest", "uc4_2")

    # Consultant connections
    p1.add_edge("e_c_uc1", "", solid_edge, "act_consultant", "uc1")
    p1.add_edge("e_c_uc4", "", solid_edge, "act_consultant", "uc4")
    p1.add_edge("e_c_uc4_1", "", solid_edge, "act_consultant", "uc4_1")
    p1.add_edge("e_c_uc3", "", solid_edge, "act_consultant", "uc3")
    p1.add_edge("e_c_uc7", "", solid_edge, "act_consultant", "uc7")

    # Accountant connections
    p1.add_edge("e_acc_uc1", "", solid_edge, "act_accountant", "uc1")
    p1.add_edge("e_acc_uc5", "", solid_edge, "act_accountant", "uc5")
    p1.add_edge("e_acc_uc8", "", solid_edge, "act_accountant", "uc8")

    # Admin connections
    p1.add_edge("e_adm_uc1", "", solid_edge, "act_admin", "uc1")
    p1.add_edge("e_adm_uc2", "", solid_edge, "act_admin", "uc2")
    p1.add_edge("e_adm_uc3", "", solid_edge, "act_admin", "uc3")
    p1.add_edge("e_adm_uc5", "", solid_edge, "act_admin", "uc5")
    p1.add_edge("e_adm_uc6", "", solid_edge, "act_admin", "uc6")
    p1.add_edge("e_adm_uc7", "", solid_edge, "act_admin", "uc7")
    p1.add_edge("e_adm_uc8", "", solid_edge, "act_admin", "uc8")

    # Includes & Extends
    p1.add_edge("e_inc_uc2", "&laquo;include&raquo;", inc_edge, "uc2", "uc2_1")
    p1.add_edge("e_inc_uc4", "&laquo;include&raquo;", inc_edge, "uc4", "uc4_1")
    p1.add_edge("e_ext_uc4", "&laquo;extend&raquo;", ext_edge, "uc4_2", "uc4")
    p1.add_edge("e_ext_uc5", "&laquo;extend&raquo;", ext_edge, "uc5_1", "uc5")
    p1.add_edge("e_inc_uc6", "&laquo;include&raquo;", inc_edge, "uc6", "uc6_1")

    # AI connections
    p1.add_edge("e_ai_1", "", ai_edge, "act_ai", "uc2_1")
    p1.add_edge("e_ai_2", "", ai_edge, "act_ai", "uc4_2")
    p1.add_edge("e_ai_3", "", ai_edge, "act_ai", "uc6_1")


    # =========================================================================
    # 02. SƠ ĐỒ PHÂN CẤP CHỨC NĂNG (FUNCTIONAL DECOMPOSITION)
    # =========================================================================
    p2 = df.add_page("p02_decomp", "02. Sơ đồ phân cấp chức năng")
    p2.add_vertex("p2_title", "<b>SƠ ĐỒ PHÂN CẤP CHỨC NĂNG HỆ THỐNG VIETJOURNEY AI</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  250, 20, 1100, 40)
    
    # Root
    p2.add_vertex("root", "<b>HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI</b><br/>(VIETJOURNEY AI)",
                  "rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;strokeWidth=2;fontSize=14;fontStyle=1;fontColor=#ffffff;align=center;",
                  550, 80, 450, 60)
    
    # 4 Modules
    m_style = "rounded=1;whiteSpace=wrap;html=1;strokeWidth=2;fontSize=13;fontStyle=1;align=center;fontColor=#0f172a;"
    p2.add_vertex("mod1", "<b>1. PHÂN HỆ KHÁCH HÀNG & BÁN LẺ</b><br/>(Dành cho Khách vãng lai)",
                  m_style + "fillColor=#e0f2fe;strokeColor=#0284c7;", 60, 200, 310, 55)
    
    p2.add_vertex("mod2", "<b>2. PHÂN HỆ TƯ VẤN & BÁN HÀNG</b><br/>(Dành cho Nhân viên tư vấn)",
                  m_style + "fillColor=#dcfce7;strokeColor=#16a34a;", 420, 200, 330, 55)
    
    p2.add_vertex("mod3", "<b>3. PHÂN HỆ QUẢN TRỊ VẬN HÀNH</b><br/>(Dành cho Quản trị viên Admin)",
                  m_style + "fillColor=#fee2e2;strokeColor=#dc2626;", 790, 200, 340, 55)
    
    p2.add_vertex("mod4", "<b>4. PHÂN HỆ KẾ TOÁN & TÀI CHÍNH</b><br/>(Dành cho Kế toán & Quản lý)",
                  m_style + "fillColor=#fef3c7;strokeColor=#d97706;", 1170, 200, 330, 55)

    tree_edge = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475569;strokeWidth=2;"
    p2.add_edge("e_r_m1", "", tree_edge, "root", "mod1")
    p2.add_edge("e_r_m2", "", tree_edge, "root", "mod2")
    p2.add_edge("e_r_m3", "", tree_edge, "root", "mod3")
    p2.add_edge("e_r_m4", "", tree_edge, "root", "mod4")

    # Children of Mod 1
    c_style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#94a3b8;strokeWidth=1.5;fontSize=11;align=left;spacingLeft=10;"
    p2.add_vertex("c1_1", "1.1 Tra cứu danh mục tour & lịch trình", c_style, 80, 290, 270, 40)
    p2.add_vertex("c1_2", "1.2 Trợ lý AI tư vấn thông minh (RAG)", c_style, 80, 345, 270, 40)
    p2.add_vertex("c1_3", "1.3 Gửi yêu cầu đặt tour (WAITING_CONFIRM)", c_style, 80, 400, 270, 40)
    p2.add_vertex("c1_4", "1.4 Gửi phản hồi & đánh giá chuyến đi", c_style, 80, 455, 270, 40)
    for c in ["c1_1", "c1_2", "c1_3", "c1_4"]:
        p2.add_edge(f"e_m1_{c}", "", tree_edge, "mod1", c)

    # Children of Mod 2
    p2.add_vertex("c2_1", "2.1 Tiếp nhận & xử lý hàng chờ tư vấn", c_style, 440, 290, 290, 40)
    p2.add_vertex("c2_2", "2.2 Quản lý hồ sơ khách hàng & tra cứu", c_style, 440, 345, 290, 40)
    p2.add_vertex("c2_3", "2.3 Giữ chỗ & Khóa ghế (Pessimistic Lock)", c_style, 440, 400, 290, 40)
    p2.add_vertex("c2_4", "2.4 Hủy booking & Hoàn trả số chỗ trống", c_style, 440, 455, 290, 40)
    p2.add_vertex("c2_5", "2.5 Giám sát lịch khởi hành & chỗ trống", c_style, 440, 510, 290, 40)
    for c in ["c2_1", "c2_2", "c2_3", "c2_4", "c2_5"]:
        p2.add_edge(f"e_m2_{c}", "", tree_edge, "mod2", c)

    # Children of Mod 3
    p2.add_vertex("c3_1", "3.1 Quản lý Tour (CRUD) & Điểm đến", c_style, 810, 290, 300, 40)
    p2.add_vertex("c3_2", "3.2 AI Gemini tự động sinh mô tả tour", c_style, 810, 345, 300, 40)
    p2.add_vertex("c3_3", "3.3 Quản lý Lịch khởi hành & Điều phối HDV", c_style, 810, 400, 300, 40)
    p2.add_vertex("c3_4", "3.4 Bắt đầu (RUNNING) & Kết thúc chuyến", c_style, 810, 455, 300, 40)
    p2.add_vertex("c3_5", "3.5 Quản lý hồ sơ Hướng dẫn viên", c_style, 810, 510, 300, 40)
    p2.add_vertex("c3_6", "3.6 Quản lý Tài khoản & Phân quyền RBAC", c_style, 810, 565, 300, 40)
    p2.add_vertex("c3_7", "3.7 AI phân tích & tóm tắt phản hồi du khách", c_style, 810, 620, 300, 40)
    for c in ["c3_1", "c3_2", "c3_3", "c3_4", "c3_5", "c3_6", "c3_7"]:
        p2.add_edge(f"e_m3_{c}", "", tree_edge, "mod3", c)

    # Children of Mod 4
    p2.add_vertex("c4_1", "4.1 Lập phiếu thu tiền & Đối soát giao dịch", c_style, 1190, 290, 290, 40)
    p2.add_vertex("c4_2", "4.2 Quản lý Đặt cọc (>= 30% -> DEPOSITED)", c_style, 1190, 345, 290, 40)
    p2.add_vertex("c4_3", "4.3 Thu đủ 100% vé (-> CONFIRMED)", c_style, 1190, 400, 290, 40)
    p2.add_vertex("c4_4", "4.4 Xử lý hoàn tiền khi hủy (REFUND)", c_style, 1190, 455, 290, 40)
    p2.add_vertex("c4_5", "4.5 Báo cáo Top Tour doanh thu cao nhất", c_style, 1190, 510, 290, 40)
    p2.add_vertex("c4_6", "4.6 Báo cáo Tỷ lệ lấp đầy ghế ngồi", c_style, 1190, 565, 290, 40)
    for c in ["c4_1", "c4_2", "c4_3", "c4_4", "c4_5", "c4_6"]:
        p2.add_edge(f"e_m4_{c}", "", tree_edge, "mod4", c)


    # =========================================================================
    # 03. SƠ ĐỒ LỚP CHI TIẾT (CLASS DIAGRAM - CHUẨN UML OOP)
    # =========================================================================
    p3 = df.add_page("p03_class", "03. Sơ đồ Lớp (Class Diagram)")
    p3.add_vertex("p3_title", "<b>SƠ ĐỒ LỚP CHI TIẾT HỆ THỐNG VIETJOURNEY AI (UML CLASS DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 15, 1000, 35)

    cls_style = "rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=6;fillColor=#f8fafc;strokeColor=#0284c7;strokeWidth=2;fontSize=11;"
    
    # Tour
    p3.add_vertex("c_tour",
                  "<b>Tour</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ code: str [UK]<br/>"
                  "+ title: str<br/>"
                  "+ destination: str<br/>"
                  "+ category: str<br/>"
                  "+ duration_days: int<br/>"
                  "+ duration_nights: int<br/>"
                  "+ base_price: Decimal (VNĐ)<br/>"
                  "+ description: str<br/>"
                  "+ is_active: bool<br/>"
                  "<hr/>"
                  "+ create_tour()<br/>"
                  "+ update_tour()<br/>"
                  "+ generate_ai_desc()",
                  cls_style, 50, 70, 210, 240)

    # Departure
    p3.add_vertex("c_departure",
                  "<b>Departure</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ tour_id: int [FK]<br/>"
                  "+ departure_date: date<br/>"
                  "+ return_date: date<br/>"
                  "+ total_slots: int<br/>"
                  "+ available_slots: int<br/>"
                  "+ price_override: Decimal<br/>"
                  "+ guide_id: int [FK]<br/>"
                  "+ status: DepartureStatus<br/>"
                  "<hr/>"
                  "+ lock_slots(qty: int)<br/>"
                  "+ release_slots(qty: int)<br/>"
                  "+ start_trip()<br/>"
                  "+ complete_trip()",
                  cls_style, 340, 70, 220, 250)

    # TourGuide
    p3.add_vertex("c_guide",
                  "<b>TourGuide</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ full_name: str<br/>"
                  "+ phone: str<br/>"
                  "+ email: str<br/>"
                  "+ languages: str<br/>"
                  "+ experience_years: int<br/>"
                  "+ status: GuideStatus<br/>"
                  "+ rating: float<br/>"
                  "<hr/>"
                  "+ check_conflict(d1, d2)<br/>"
                  "+ assign_departure()",
                  cls_style, 640, 70, 200, 210)

    # Customer
    p3.add_vertex("c_customer",
                  "<b>Customer</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ full_name: str<br/>"
                  "+ phone: str [UK]<br/>"
                  "+ email: str<br/>"
                  "+ id_card: str<br/>"
                  "+ address: str<br/>"
                  "<hr/>"
                  "+ get_or_create()<br/>"
                  "+ get_booking_history()",
                  cls_style, 50, 390, 210, 190)

    # Booking
    p3.add_vertex("c_booking",
                  "<b>Booking</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ booking_code: str [UK]<br/>"
                  "+ departure_id: int [FK]<br/>"
                  "+ customer_id: int [FK]<br/>"
                  "+ num_people: int<br/>"
                  "+ total_amount: Decimal<br/>"
                  "+ deposit_amount: Decimal<br/>"
                  "+ paid_amount: Decimal<br/>"
                  "+ status: BookingStatus<br/>"
                  "+ refund_amount: Decimal<br/>"
                  "<hr/>"
                  "+ confirm_booking()<br/>"
                  "+ calculate_status()<br/>"
                  "+ cancel_and_refund()",
                  cls_style, 340, 390, 220, 260)

    # Payment
    p3.add_vertex("c_payment",
                  "<b>Payment</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ booking_id: int [FK]<br/>"
                  "+ payment_type: PaymentType<br/>"
                  "+ amount: Decimal (VNĐ)<br/>"
                  "+ payment_method: Method<br/>"
                  "+ status: PaymentStatus<br/>"
                  "+ transaction_code: str [UK]<br/>"
                  "+ created_by: str<br/>"
                  "<hr/>"
                  "+ record_payment()<br/>"
                  "+ generate_receipt()",
                  cls_style, 640, 390, 210, 220)

    # User
    p3.add_vertex("c_user",
                  "<b>User</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ username: str [UK]<br/>"
                  "+ hashed_password: str (PBKDF2)<br/>"
                  "+ full_name: str<br/>"
                  "+ email: str<br/>"
                  "+ role: UserRole<br/>"
                  "+ is_active: bool<br/>"
                  "<hr/>"
                  "+ verify_password()<br/>"
                  "+ has_permission(role)",
                  cls_style, 920, 70, 210, 210)

    # Feedback
    p3.add_vertex("c_feedback",
                  "<b>Feedback</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ tour_id: int [FK]<br/>"
                  "+ booking_id: int [FK]<br/>"
                  "+ customer_name: str<br/>"
                  "+ rating: int (1-5)<br/>"
                  "+ comments: str<br/>"
                  "+ guide_rating: int (1-5)<br/>"
                  "+ sentiment: SentimentType<br/>"
                  "<hr/>"
                  "+ analyze_sentiment()",
                  cls_style, 920, 390, 210, 210)

    # AISessionLog & Key
    p3.add_vertex("c_ailog",
                  "<b>AISessionLog</b><hr/>"
                  "+ id: int [PK]<br/>"
                  "+ feature_type: str<br/>"
                  "+ input_prompt: str<br/>"
                  "+ response_content: str<br/>"
                  "+ model_name: str<br/>"
                  "+ created_at: datetime<br/>"
                  "<hr/>"
                  "+ log_interaction()",
                  cls_style, 1200, 70, 210, 190)

    p3.add_vertex("c_idemp_key",
                  "<b>BookingRequestKey</b><hr/>"
                  "+ key: str [PK]<br/>"
                  "+ fingerprint: str<br/>"
                  "+ booking_id: int [FK]<br/>"
                  "<hr/>"
                  "+ check_duplicate()<br/>"
                  "+ store_key()",
                  cls_style, 1200, 390, 210, 170)

    # Routers and Services Box
    srv_style = "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=8;fillColor=#f1f5f9;strokeColor=#475569;strokeWidth=1.5;fontSize=11;"
    p3.add_vertex("c_routers",
                  "<b>Controllers / API Routers</b><hr/>"
                  "+ AuthRouter (/auth)<br/>"
                  "+ TourRouter (/tours)<br/>"
                  "+ DepartureRouter (/departures)<br/>"
                  "+ BookingRouter (/bookings)<br/>"
                  "+ PaymentRouter (/payments)<br/>"
                  "+ GuideRouter (/guides)<br/>"
                  "+ FeedbackRouter (/feedbacks)<br/>"
                  "+ AIRouter (/ai)<br/>"
                  "+ StatsRouter (/stats)",
                  srv_style, 50, 710, 260, 210)

    p3.add_vertex("c_services",
                  "<b>Service & Logic Layer</b><hr/>"
                  "+ <b>AIService (GeminiClient)</b>:<br/>"
                  "   - consult_tours(query)<br/>"
                  "   - generate_tour_description()<br/>"
                  "   - summarize_feedbacks(tour_id)<br/>"
                  "+ <b>BookingService</b>:<br/>"
                  "   - process_guest_request()<br/>"
                  "   - confirm_booking_with_lock()<br/>"
                  "+ <b>PaymentService</b>:<br/>"
                  "   - process_payment_and_update()<br/>"
                  "   - calculate_refund()",
                  srv_style, 380, 710, 330, 210)

    # Edges between classes
    uml_comp = "endArrow=diamond;html=1;endFill=1;strokeColor=#0284c7;strokeWidth=1.5;"
    uml_assoc = "endArrow=none;html=1;strokeColor=#475569;strokeWidth=1.5;"
    uml_dep = "endArrow=open;dashed=1;html=1;strokeColor=#64748b;strokeWidth=1.5;endFill=0;"

    # Tour 1 -> N Departure
    p3.add_edge("ec_tour_dep", "1..*", uml_comp, "c_tour", "c_departure")
    # Departure N -> 1 Guide
    p3.add_edge("ec_dep_guide", "0..1", uml_assoc, "c_departure", "c_guide")
    # Departure 1 -> N Booking
    p3.add_edge("ec_dep_book", "1..*", uml_assoc, "c_departure", "c_booking")
    # Customer 1 -> N Booking
    p3.add_edge("ec_cust_book", "1..*", uml_assoc, "c_customer", "c_booking")
    # Booking 1 -> N Payment
    p3.add_edge("ec_book_pay", "1..*", uml_comp, "c_booking", "c_payment")
    # Tour 1 -> N Feedback
    p3.add_edge("ec_tour_fb", "0..*", uml_assoc, "c_tour", "c_feedback")
    # Booking 1 -> 1 Key
    p3.add_edge("ec_book_key", "1..1", uml_assoc, "c_booking", "c_idemp_key")
    # Services -> AI Log
    p3.add_edge("ec_srv_ailog", "&laquo;writes&raquo;", uml_dep, "c_services", "c_ailog")
    p3.add_edge("ec_rtr_srv", "&laquo;delegates&raquo;", uml_dep, "c_routers", "c_services")


    # =========================================================================
    # 04. SƠ ĐỒ THỰC THỂ LIÊN KẾT (ERD - 10 BẢNG CHUẨN 3NF)
    # =========================================================================
    p4 = df.add_page("p04_erd", "04. Sơ đồ CSDL ERD (10 Bảng)")
    p4.add_vertex("p4_title", "<b>SƠ ĐỒ THỰC THỂ LIÊN KẾT (ERD 10 BẢNG CHUẨN HÓA 3NF)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 15, 1000, 35)

    erd_style = "rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=6;fillColor=#ffffff;strokeColor=#334155;strokeWidth=1.5;fontSize=11;"
    
    # Tables
    p4.add_vertex("t_users",
                  "<b>USERS</b> (Quản trị & Phân quyền)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>UK</b> username: VARCHAR(50)<br/>"
                  "hashed_password: VARCHAR(255)<br/>"
                  "full_name: VARCHAR(100)<br/>"
                  "email: VARCHAR(100)<br/>"
                  "phone: VARCHAR(20)<br/>"
                  "role: VARCHAR(20) [ADMIN/CONSULTANT/ACCOUNTANT]<br/>"
                  "is_active: BOOLEAN<br/>"
                  "created_at: DATETIME",
                  erd_style, 50, 70, 260, 180)

    p4.add_vertex("t_tours",
                  "<b>TOURS</b> (Danh mục tour)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>UK</b> code: VARCHAR(20)<br/>"
                  "title: VARCHAR(255)<br/>"
                  "destination: VARCHAR(100)<br/>"
                  "category: VARCHAR(50)<br/>"
                  "duration_days: INTEGER<br/>"
                  "duration_nights: INTEGER<br/>"
                  "base_price: DECIMAL(18,0)<br/>"
                  "description: TEXT<br/>"
                  "itinerary_summary: TEXT<br/>"
                  "highlights: TEXT<br/>"
                  "image_url: VARCHAR(255)<br/>"
                  "is_active: BOOLEAN<br/>"
                  "created_at: DATETIME",
                  erd_style, 380, 70, 260, 240)

    p4.add_vertex("t_guides",
                  "<b>TOUR_GUIDES</b> (Hướng dẫn viên)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "full_name: VARCHAR(100)<br/>"
                  "phone: VARCHAR(20)<br/>"
                  "email: VARCHAR(100)<br/>"
                  "languages: VARCHAR(100)<br/>"
                  "experience_years: INTEGER<br/>"
                  "status: VARCHAR(20) [AVAILABLE/ON_TOUR/OFF]<br/>"
                  "rating: FLOAT<br/>"
                  "notes: TEXT",
                  erd_style, 1080, 70, 260, 180)

    p4.add_vertex("t_departures",
                  "<b>DEPARTURES</b> (Lịch khởi hành & Ghế)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>FK</b> tour_id: INTEGER<br/>"
                  "departure_date: DATE<br/>"
                  "return_date: DATE<br/>"
                  "total_slots: INTEGER<br/>"
                  "available_slots: INTEGER<br/>"
                  "price_override: DECIMAL(18,0)<br/>"
                  "<b>FK</b> guide_id: INTEGER<br/>"
                  "status: VARCHAR(20) [OPEN/FULL/RUNNING...]<br/>"
                  "notes: TEXT<br/>"
                  "created_at: DATETIME",
                  erd_style, 730, 70, 270, 210)

    p4.add_vertex("t_customers",
                  "<b>CUSTOMERS</b> (Hồ sơ khách hàng)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "full_name: VARCHAR(100)<br/>"
                  "<b>UK</b> phone: VARCHAR(20)<br/>"
                  "email: VARCHAR(100)<br/>"
                  "id_card: VARCHAR(20)<br/>"
                  "address: VARCHAR(255)<br/>"
                  "notes: TEXT<br/>"
                  "created_at: DATETIME",
                  erd_style, 50, 420, 260, 170)

    p4.add_vertex("t_bookings",
                  "<b>BOOKINGS</b> (Đơn đặt tour)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>UK</b> booking_code: VARCHAR(30)<br/>"
                  "<b>FK</b> departure_id: INTEGER<br/>"
                  "<b>FK</b> customer_id: INTEGER<br/>"
                  "num_people: INTEGER<br/>"
                  "total_amount: DECIMAL(18,0)<br/>"
                  "deposit_amount: DECIMAL(18,0)<br/>"
                  "paid_amount: DECIMAL(18,0)<br/>"
                  "status: VARCHAR(20) [WAITING/PENDING/CONFIRMED...]<br/>"
                  "refund_amount: DECIMAL(18,0)<br/>"
                  "cancellation_reason: TEXT<br/>"
                  "special_requests: TEXT<br/>"
                  "created_at: DATETIME<br/>"
                  "updated_at: DATETIME",
                  erd_style, 380, 420, 280, 250)

    p4.add_vertex("t_payments",
                  "<b>PAYMENTS</b> (Lịch sử thanh toán)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>FK</b> booking_id: INTEGER<br/>"
                  "payment_type: VARCHAR(30) [DEPOSIT/FULL/REFUND]<br/>"
                  "amount: DECIMAL(18,0)<br/>"
                  "payment_method: VARCHAR(30) [TRANSFER/CASH]<br/>"
                  "status: VARCHAR(20) [SUCCESS/PENDING/FAILED]<br/>"
                  "<b>UK</b> transaction_code: VARCHAR(50)<br/>"
                  "note: TEXT<br/>"
                  "created_by: VARCHAR(100)<br/>"
                  "created_at: DATETIME",
                  erd_style, 730, 420, 280, 200)

    p4.add_vertex("t_feedbacks",
                  "<b>FEEDBACKS</b> (Đánh giá sau tour)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "<b>FK</b> tour_id: INTEGER<br/>"
                  "<b>FK</b> booking_id: INTEGER<br/>"
                  "customer_name: VARCHAR(100)<br/>"
                  "rating: INTEGER (1-5)<br/>"
                  "comments: TEXT<br/>"
                  "guide_rating: INTEGER (1-5)<br/>"
                  "sentiment: VARCHAR(20) [POS/NEU/NEG]<br/>"
                  "created_at: DATETIME",
                  erd_style, 1080, 420, 260, 190)

    p4.add_vertex("t_ailogs",
                  "<b>AI_SESSION_LOGS</b> (Nhật ký AI)<hr/>"
                  "<b>PK</b> id: INTEGER<br/>"
                  "feature_type: VARCHAR(50)<br/>"
                  "input_prompt: TEXT<br/>"
                  "response_content: TEXT<br/>"
                  "model_name: VARCHAR(50)<br/>"
                  "created_at: DATETIME",
                  erd_style, 50, 720, 260, 140)

    p4.add_vertex("t_keys",
                  "<b>BOOKING_REQUEST_KEYS</b> (Chống gửi lặp)<hr/>"
                  "<b>PK</b> key: VARCHAR(64)<br/>"
                  "fingerprint: VARCHAR(128)<br/>"
                  "<b>FK</b> booking_id: INTEGER",
                  erd_style, 380, 740, 280, 100)

    # ERD Connectors (Crow's foot)
    erd_edge = "endArrow=ERmany;startArrow=ERone;html=1;strokeColor=#1e293b;strokeWidth=1.5;"
    p4.add_edge("er_tours_dep", "1 : N", erd_edge, "t_tours", "t_departures")
    p4.add_edge("er_guide_dep", "1 : N", erd_edge, "t_guides", "t_departures")
    p4.add_edge("er_dep_book", "1 : N", erd_edge, "t_departures", "t_bookings")
    p4.add_edge("er_cust_book", "1 : N", erd_edge, "t_customers", "t_bookings")
    p4.add_edge("er_book_pay", "1 : N", erd_edge, "t_bookings", "t_payments")
    p4.add_edge("er_tour_fb", "1 : N", erd_edge, "t_tours", "t_feedbacks")
    p4.add_edge("er_book_key", "1 : 1", "endArrow=ERone;startArrow=ERone;html=1;strokeColor=#1e293b;strokeWidth=1.5;", "t_bookings", "t_keys")


    # =========================================================================
    # 05. SƠ ĐỒ LUỒNG MÀN HÌNH (SCREEN FLOW DIAGRAM)
    # =========================================================================
    p5 = df.add_page("p05_screenflow", "05. Sơ đồ Luồng màn hình (Screen Flow)")
    p5.add_vertex("p5_title", "<b>SƠ ĐỒ PHÂN LUỒNG MÀN HÌNH NGHIỆP VỤ (SCREEN FLOW DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 15, 1000, 35)

    scr_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fafc;strokeColor=#334155;strokeWidth=2;fontSize=12;fontStyle=1;align=center;"
    flow_edge = "endArrow=block;html=1;strokeColor=#0284c7;strokeWidth=2;endFill=1;fontSize=11;fontColor=#0284c7;"

    # Guest screens
    p5.add_vertex("scr_home", "<b>Trang chủ Tour</b><br/>(tours.html / index.html)<br/><i>Khách vãng lai xem danh mục</i>",
                  scr_style + "fillColor=#e0f2fe;strokeColor=#0284c7;", 50, 100, 240, 70)
    
    p5.add_vertex("scr_ai_chat", "<b>Drawer Trợ lý AI Gemini</b><br/><i>Tư vấn tour theo ngân sách & số ngày</i>",
                  scr_style + "fillColor=#f3e8ff;strokeColor=#9333ea;", 50, 240, 240, 60)
    
    p5.add_vertex("scr_modal_req", "<b>Modal Gửi Yêu Cầu Tour</b><br/><i>Tạo đơn WAITING_CONFIRM<br/>(Chưa trừ số chỗ)</i>",
                  scr_style + "fillColor=#fef3c7;strokeColor=#d97706;", 50, 370, 240, 65)

    p5.add_edge("ef_home_ai", "Bấm 'Hỏi AI'", flow_edge, "scr_home", "scr_ai_chat")
    p5.add_edge("ef_home_req", "Bấm 'Đặt tour'", flow_edge, "scr_home", "scr_modal_req")

    # Login screen
    p5.add_vertex("scr_login", "<b>Màn hình Đăng Nhập</b><br/>(login.html)<br/><i>Xác thực username/password</i>",
                  scr_style + "fillColor=#fee2e2;strokeColor=#dc2626;", 380, 100, 230, 70)
    p5.add_edge("ef_home_login", "Bấm 'Đăng nhập'", flow_edge, "scr_home", "scr_login")

    # RBAC Dispatcher
    p5.add_vertex("scr_rbac", "<b>Hệ thống RBAC Dispatcher</b><br/><i>Giải mã JWT & Điều hướng vai trò</i>",
                  "rhombus;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;fontSize=11;fontStyle=1;fontColor=#ffffff;align=center;",
                  690, 95, 200, 80)
    p5.add_edge("ef_login_rbac", "Đăng nhập thành công", flow_edge, "scr_login", "scr_rbac")

    # Consultant Branch
    p5.add_vertex("scr_consult", "<b>Hàng Chờ Tư Vấn</b><br/>(consultations.html)<br/><i>Duyệt giữ chỗ (PENDING) / Từ chối</i>",
                  scr_style + "fillColor=#dcfce7;strokeColor=#16a34a;", 970, 60, 260, 65)
    p5.add_vertex("scr_booking", "<b>Quản lý Đặt Chỗ</b><br/>(bookings.html)<br/><i>Theo dõi đơn, Hủy đơn hoàn chỗ</i>",
                  scr_style + "fillColor=#dcfce7;strokeColor=#16a34a;", 1300, 60, 260, 65)
    p5.add_edge("ef_rbac_c", "Vai trò CONSULTANT", flow_edge, "scr_rbac", "scr_consult")
    p5.add_edge("ef_c_b", "Xác nhận giữ chỗ", flow_edge, "scr_consult", "scr_booking")

    # Accountant Branch
    p5.add_vertex("scr_payment", "<b>Kế toán & Thu tiền</b><br/>(payments.html)<br/><i>Thu tiền cọc, Thu đủ, Hoàn tiền</i>",
                  scr_style + "fillColor=#fef3c7;strokeColor=#d97706;", 970, 220, 260, 65)
    p5.add_vertex("scr_stats", "<b>Thống kê & Doanh thu</b><br/>(stats.html)<br/><i>Biểu đồ Top tour, Tỷ lệ lấp đầy</i>",
                  scr_style + "fillColor=#fef3c7;strokeColor=#d97706;", 1300, 220, 260, 65)
    p5.add_edge("ef_rbac_acc", "Vai trò ACCOUNTANT", flow_edge, "scr_rbac", "scr_payment")
    p5.add_edge("ef_p_s", "Xem báo cáo", flow_edge, "scr_payment", "scr_stats")

    # Admin Branch
    p5.add_vertex("scr_tours_adm", "<b>Quản lý Tour & AI</b><br/>(tours_admin.html)<br/><i>CRUD Tour, AI sinh mô tả</i>",
                  scr_style + "fillColor=#fee2e2;strokeColor=#dc2626;", 970, 380, 260, 65)
    p5.add_vertex("scr_dep_adm", "<b>Lịch Khởi Hành & HDV</b><br/>(departures.html)<br/><i>Mở đợt mới, Bắt đầu / Hoàn tất</i>",
                  scr_style + "fillColor=#fee2e2;strokeColor=#dc2626;", 1300, 380, 260, 65)
    p5.add_vertex("scr_aihub", "<b>AI Hub & Phản hồi</b><br/>(ai_hub.html)<br/><i>AI phân tích cảm xúc & Tóm tắt</i>",
                  scr_style + "fillColor=#f3e8ff;strokeColor=#9333ea;", 970, 510, 260, 65)
    p5.add_vertex("scr_users_adm", "<b>Quản lý Tài Khoản</b><br/>(users.html)<br/><i>Phân quyền tài khoản nhân sự</i>",
                  scr_style + "fillColor=#fee2e2;strokeColor=#dc2626;", 1300, 510, 260, 65)
    p5.add_edge("ef_rbac_adm", "Vai trò ADMIN (Toàn quyền)", flow_edge, "scr_rbac", "scr_tours_adm")
    p5.add_edge("ef_adm_dep", "Điều hành", flow_edge, "scr_tours_adm", "scr_dep_adm")
    p5.add_edge("ef_adm_ai", "Phân tích review", flow_edge, "scr_tours_adm", "scr_aihub")
    p5.add_edge("ef_adm_usr", "Cấu hình nhân sự", flow_edge, "scr_tours_adm", "scr_users_adm")


    # =========================================================================
    # 06. UC001 - ĐĂNG NHẬP & PHÂN QUYỀN (ACTIVITY DIAGRAM)
    # =========================================================================
    p6 = df.add_page("p06_uc001_act", "06. UC001 - Đăng nhập (Activity)")
    p6.add_vertex("p6_title", "<b>UC001: ĐĂNG NHẬP VÀ PHÂN QUYỀN RBAC (ACTIVITY DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 20, 1000, 35)

    act_step = "rounded=1;arcSize=20;whiteSpace=wrap;html=1;fillColor=#eff6ff;strokeColor=#3b82f6;strokeWidth=1.5;fontSize=12;fontStyle=1;align=center;"
    act_diamond = "rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=1.5;fontSize=11;fontStyle=1;align=center;"
    act_edge = "endArrow=block;html=1;strokeColor=#334155;strokeWidth=1.5;endFill=1;fontSize=11;"

    p6.add_vertex("a1_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 720, 80, 30, 30)
    p6.add_vertex("a1_s1", "Người dùng nhập Username & Password", act_step, 615, 140, 240, 50)
    p6.add_vertex("a1_s2", "Kiểm tra dữ liệu rỗng (Client-side validation)", act_step, 615, 220, 240, 50)
    p6.add_vertex("a1_d1", "Hợp lệ?", act_diamond, 685, 300, 100, 60)
    p6.add_vertex("a1_s3", "Gửi POST /auth/login tới Backend", act_step, 615, 400, 240, 50)
    p6.add_vertex("a1_s4", "Truy vấn CSDL bảng Users & Xác minh mật khẩu PBKDF2", act_step, 600, 480, 270, 50)
    p6.add_vertex("a1_d2", "Khớp mật khẩu & Đang active?", act_diamond, 655, 560, 160, 70)
    p6.add_vertex("a1_err1", "Báo lỗi: 'Tên đăng nhập hoặc mật khẩu không chính xác'", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 260, 570, 270, 50)
    p6.add_vertex("a1_s5", "Hệ thống sinh JWT Access Token (chứa user_id, role)", act_step, 600, 670, 270, 50)
    p6.add_vertex("a1_s6", "Lưu Token vào localStorage & Kiểm tra vai trò (Role)", act_step, 600, 750, 270, 50)
    p6.add_vertex("a1_d3", "Phân quyền theo Role", act_diamond, 655, 830, 160, 70)

    # 3 branches
    p6.add_vertex("a1_r_adm", "ADMIN: Chuyển hướng Dashboard Quản trị & Toàn bộ menu", act_step + "fillColor=#fee2e2;strokeColor=#dc2626;", 220, 930, 260, 55)
    p6.add_vertex("a1_r_con", "CONSULTANT: Chuyển hướng Hàng chờ tư vấn & Đặt chỗ", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 605, 930, 260, 55)
    p6.add_vertex("a1_r_acc", "ACCOUNTANT: Chuyển hướng Kế toán & Báo cáo doanh thu", act_step + "fillColor=#fef3c7;strokeColor=#d97706;", 990, 930, 260, 55)

    p6.add_vertex("a1_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 720, 1030, 30, 30)

    # Edges
    p6.add_edge("ea1_0", "", act_edge, "a1_init", "a1_s1")
    p6.add_edge("ea1_1", "", act_edge, "a1_s1", "a1_s2")
    p6.add_edge("ea1_2", "", act_edge, "a1_s2", "a1_d1")
    p6.add_edge("ea1_3", "Đúng", act_edge, "a1_d1", "a1_s3")
    p6.add_edge("ea1_4", "", act_edge, "a1_s3", "a1_s4")
    p6.add_edge("ea1_5", "", act_edge, "a1_s4", "a1_d2")
    p6.add_edge("ea1_err", "Sai", act_edge, "a1_d2", "a1_err1")
    p6.add_edge("ea1_retry", "Nhập lại", act_edge, "a1_err1", "a1_s1")
    p6.add_edge("ea1_ok", "Đúng", act_edge, "a1_d2", "a1_s5")
    p6.add_edge("ea1_6", "", act_edge, "a1_s5", "a1_s6")
    p6.add_edge("ea1_7", "", act_edge, "a1_s6", "a1_d3")
    p6.add_edge("ea1_b1", "ADMIN", act_edge, "a1_d3", "a1_r_adm")
    p6.add_edge("ea1_b2", "CONSULTANT", act_edge, "a1_d3", "a1_r_con")
    p6.add_edge("ea1_b3", "ACCOUNTANT", act_edge, "a1_d3", "a1_r_acc")
    p6.add_edge("ea1_e1", "", act_edge, "a1_r_adm", "a1_end")
    p6.add_edge("ea1_e2", "", act_edge, "a1_r_con", "a1_end")
    p6.add_edge("ea1_e3", "", act_edge, "a1_r_acc", "a1_end")


    # =========================================================================
    # 07. UC001 - ĐĂNG NHẬP (SEQUENCE DIAGRAM)
    # =========================================================================
    p7 = df.add_page("p07_uc001_seq", "07. UC001 - Đăng nhập (Sequence)")
    p7.add_vertex("p7_title", "<b>UC001: ĐĂNG NHẬP VÀ XÁC THỰC PHÂN QUYỀN (SEQUENCE DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 20, 1000, 35)

    seq_life = "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;newEdgeStyle={&quot;curved&quot;:0,&quot;rounded&quot;:0};participant=umlBoundary;strokeWidth=1.5;fontSize=12;fontStyle=1;"
    p7.add_vertex("l1_user", "User<br/>(Actor)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 80, 80, 100, 700)
    p7.add_vertex("l1_ui", "LoginForm<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 340, 80, 120, 700)
    p7.add_vertex("l1_rtr", "AuthRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 640, 80, 120, 700)
    p7.add_vertex("l1_srv", "AuthService<br/>(PBKDF2/JWT)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 940, 80, 120, 700)
    p7.add_vertex("l1_db", "UsersTable<br/>(Database)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 1240, 80, 120, 700)

    call_e = "endArrow=block;html=1;strokeColor=#0f172a;strokeWidth=1.5;endFill=1;fontSize=11;"
    ret_e = "endArrow=open;dashed=1;html=1;strokeColor=#64748b;strokeWidth=1.5;endFill=0;fontSize=11;"

    # Calls
    p7.add_vertex("l1_msg1", "1. Nhập username, password -> Bấm 'Đăng nhập'", "text;html=1;align=center;fontSize=11;", 150, 180, 200, 20)
    p7.add_edge("es1_1", "", call_e, "l1_user", "l1_ui", [(130, 200), (400, 200)])

    p7.add_vertex("l1_msg2", "2. POST /auth/login {username, password}", "text;html=1;align=center;fontSize=11;", 440, 230, 220, 20)
    p7.add_edge("es1_2", "", call_e, "l1_ui", "l1_rtr", [(400, 250), (700, 250)])

    p7.add_vertex("l1_msg3", "3. get_user_by_username(username)", "text;html=1;align=center;fontSize=11;", 740, 280, 210, 20)
    p7.add_edge("es1_3", "", call_e, "l1_rtr", "l1_db", [(700, 300), (1300, 300)])

    p7.add_vertex("l1_msg4", "4. Trả về bản ghi User (kèm hashed_password)", "text;html=1;align=center;fontSize=11;", 740, 330, 240, 20)
    p7.add_edge("es1_4", "", ret_e, "l1_db", "l1_rtr", [(1300, 350), (700, 350)])

    p7.add_vertex("l1_msg5", "5. verify_password(plain, hashed)", "text;html=1;align=center;fontSize=11;", 740, 380, 210, 20)
    p7.add_edge("es1_5", "", call_e, "l1_rtr", "l1_srv", [(700, 400), (1000, 400)])

    p7.add_vertex("l1_msg6", "6. Mật khẩu khớp -> create_access_token()", "text;html=1;align=center;fontSize=11;", 740, 430, 240, 20)
    p7.add_edge("es1_6", "", ret_e, "l1_srv", "l1_rtr", [(1000, 450), (700, 450)])

    p7.add_vertex("l1_msg7", "7. 200 OK {access_token, role, full_name}", "text;html=1;align=center;fontSize=11;", 440, 500, 230, 20)
    p7.add_edge("es1_7", "", ret_e, "l1_rtr", "l1_ui", [(700, 520), (400, 520)])

    p7.add_vertex("l1_msg8", "8. Lưu Token vào localStorage -> Điều hướng theo Role", "text;html=1;align=center;fontSize=11;", 130, 560, 270, 20)
    p7.add_edge("es1_8", "", ret_e, "l1_ui", "l1_user", [(400, 580), (130, 580)])


    # =========================================================================
    # 08. UC002 - QUẢN LÝ TOUR & AI SINH MÔ TẢ (ACTIVITY DIAGRAM)
    # =========================================================================
    p8 = df.add_page("p08_uc002_act", "08. UC002 - Quản lý Tour & AI (Activity)")
    p8.add_vertex("p8_title", "<b>UC002: QUẢN LÝ DANH MỤC TOUR & AI SINH MÔ TẢ (ACTIVITY DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 20, 1000, 35)

    p8.add_vertex("a2_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 735, 70, 30, 30)
    p8.add_vertex("a2_s1", "Admin truy cập Quản lý Tour -> Bấm '+ Thêm tour mới'", act_step, 600, 130, 300, 50)
    p8.add_vertex("a2_s2", "Nhập thông tin cơ bản: Tên tour, Điểm đến, Thời lượng, Giá", act_step, 600, 210, 300, 50)
    p8.add_vertex("a2_d1", "Sử dụng AI sinh mô tả?", act_diamond, 670, 290, 160, 70)
    
    # AI Branch
    p8.add_vertex("a2_ai_call", "Bấm 'AI Viết mô tả tour' -> Gửi prompt tới Gemini Engine", act_step + "fillColor=#f3e8ff;strokeColor=#9333ea;", 280, 380, 320, 50)
    p8.add_vertex("a2_ai_resp", "AI trả về đoạn văn giới thiệu chi tiết & Tóm tắt lịch trình", act_step + "fillColor=#f3e8ff;strokeColor=#9333ea;", 280, 460, 320, 50)
    p8.add_vertex("a2_ai_edit", "Tự động điền vào khung mô tả; Admin rà soát và chỉnh sửa", act_step, 280, 540, 320, 50)

    # Manual Branch
    p8.add_vertex("a2_man", "Admin tự gõ nội dung mô tả thủ công vào khung", act_step, 900, 460, 280, 50)

    # Join
    p8.add_vertex("a2_join", "", "rounded=0;fillColor=#1e293b;strokeColor=none;", 550, 630, 400, 8)
    p8.add_vertex("a2_save", "Admin nhấn nút 'Lưu Tour'", act_step, 650, 670, 200, 45)
    p8.add_vertex("a2_val", "Backend xác thực dữ liệu (code duy nhất, giá > 0)", act_step, 620, 745, 260, 50)
    p8.add_vertex("a2_db", "Lưu bản ghi vào bảng Tours trong CSDL", act_step, 620, 825, 260, 50)
    p8.add_vertex("a2_done", "Hiển thị thông báo thành công & Cập nhật danh sách", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 600, 905, 300, 50)
    p8.add_vertex("a2_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 735, 990, 30, 30)

    p8.add_edge("ea2_0", "", act_edge, "a2_init", "a2_s1")
    p8.add_edge("ea2_1", "", act_edge, "a2_s1", "a2_s2")
    p8.add_edge("ea2_2", "", act_edge, "a2_s2", "a2_d1")
    p8.add_edge("ea2_ai", "Có", act_edge, "a2_d1", "a2_ai_call")
    p8.add_edge("ea2_ai2", "", act_edge, "a2_ai_call", "a2_ai_resp")
    p8.add_edge("ea2_ai3", "", act_edge, "a2_ai_resp", "a2_ai_edit")
    p8.add_edge("ea2_ai4", "", act_edge, "a2_ai_edit", "a2_join")
    p8.add_edge("ea2_man1", "Không", act_edge, "a2_d1", "a2_man")
    p8.add_edge("ea2_man2", "", act_edge, "a2_man", "a2_join")
    p8.add_edge("ea2_3", "", act_edge, "a2_join", "a2_save")
    p8.add_edge("ea2_4", "", act_edge, "a2_save", "a2_val")
    p8.add_edge("ea2_5", "", act_edge, "a2_val", "a2_db")
    p8.add_edge("ea2_6", "", act_edge, "a2_db", "a2_done")
    p8.add_edge("ea2_7", "", act_edge, "a2_done", "a2_end")


    # =========================================================================
    # 09. UC002 - QUẢN LÝ TOUR & AI (SEQUENCE DIAGRAM)
    # =========================================================================
    p9 = df.add_page("p09_uc002_seq", "09. UC002 - Quản lý Tour & AI (Sequence)")
    p9.add_vertex("p9_title", "<b>UC002: QUẢN LÝ TOUR VÀ AI SINH MÔ TẢ (SEQUENCE DIAGRAM)</b>",
                  "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                  300, 20, 1000, 35)

    p9.add_vertex("l2_adm", "Admin<br/>(Actor)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 60, 80, 100, 720)
    p9.add_vertex("l2_ui", "TourAdminView<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 320, 80, 120, 720)
    p9.add_vertex("l2_rtr", "TourRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 600, 80, 120, 720)
    p9.add_vertex("l2_ai", "AIService<br/>(Gemini Engine)", seq_life + "fillColor=#f3e8ff;strokeColor=#9333ea;", 890, 80, 130, 720)
    p9.add_vertex("l2_ext", "Google Gemini API<br/>(Cloud)", seq_life + "fillColor=#f3e8ff;strokeColor=#7e22ce;", 1190, 80, 130, 720)
    p9.add_vertex("l2_db", "ToursDB<br/>(Database)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1440, 80, 100, 720)

    # Sequence calls
    p9.add_vertex("l2_m1", "1. Bấm 'AI Viết mô tả tour' (title, destination, days)", "text;html=1;align=center;fontSize=11;", 110, 170, 250, 20)
    p9.add_edge("es2_1", "", call_e, "l2_adm", "l2_ui", [(110, 190), (380, 190)])

    p9.add_vertex("l2_m2", "2. POST /ai/generate-tour-description", "text;html=1;align=center;fontSize=11;", 400, 215, 230, 20)
    p9.add_edge("es2_2", "", call_e, "l2_ui", "l2_rtr", [(380, 235), (660, 235)])

    p9.add_vertex("l2_m3", "3. build_prompt() -> generate_content()", "text;html=1;align=center;fontSize=11;", 680, 260, 240, 20)
    p9.add_edge("es2_3", "", call_e, "l2_rtr", "l2_ai", [(660, 280), (955, 280)])

    p9.add_vertex("l2_m4", "4. Request Gemini Flash/Pro Model", "text;html=1;align=center;fontSize=11;", 980, 305, 220, 20)
    p9.add_edge("es2_4", "", call_e, "l2_ai", "l2_ext", [(955, 325), (1255, 325)])

    p9.add_vertex("l2_m5", "5. Trả về đoạn văn mô tả & lịch trình JSON", "text;html=1;align=center;fontSize=11;", 980, 350, 240, 20)
    p9.add_edge("es2_5", "", ret_e, "l2_ext", "l2_ai", [(1255, 370), (955, 370)])

    p9.add_vertex("l2_m6", "6. Trả kết quả sinh mô tả về Frontend", "text;html=1;align=center;fontSize=11;", 400, 410, 230, 20)
    p9.add_edge("es2_6", "", ret_e, "l2_ai", "l2_ui", [(955, 430), (380, 430)])

    p9.add_vertex("l2_m7", "7. Hiển thị nội dung lên Form; Admin chỉnh sửa & Bấm 'Lưu'", "text;html=1;align=center;fontSize=11;", 80, 465, 310, 20)
    p9.add_edge("es2_7", "", call_e, "l2_adm", "l2_ui", [(110, 485), (380, 485)])

    p9.add_vertex("l2_m8", "8. POST /tours (Payload đầy đủ)", "text;html=1;align=center;fontSize=11;", 400, 510, 220, 20)
    p9.add_edge("es2_8", "", call_e, "l2_ui", "l2_rtr", [(380, 530), (660, 530)])

    p9.add_vertex("l2_m9", "9. INSERT INTO tours VALUES (...) -> COMMIT", "text;html=1;align=center;fontSize=11;", 800, 555, 270, 20)
    p9.add_edge("es2_9", "", call_e, "l2_rtr", "l2_db", [(660, 575), (1490, 575)])

    p9.add_vertex("l2_m10", "10. 201 Created -> Hiển thị tour mới trên bảng", "text;html=1;align=center;fontSize=11;", 110, 620, 270, 20)
    p9.add_edge("es2_10", "", ret_e, "l2_rtr", "l2_ui", [(660, 640), (380, 640)])
    p9.add_edge("es2_11", "", ret_e, "l2_ui", "l2_adm", [(380, 660), (110, 660)])


    # =========================================================================
    # 10. UC003 - QUẢN LÝ LỊCH KHỞI HÀNH (ACTIVITY DIAGRAM)
    # =========================================================================
    p10 = df.add_page("p10_uc003_act", "10. UC003 - Lịch khởi hành (Activity)")
    p10.add_vertex("p10_title", "<b>UC003: QUẢN LÝ LỊCH KHỞI HÀNH & ĐIỀU PHỐI HDV (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p10.add_vertex("a3_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 70, 30, 30)
    p10.add_vertex("a3_s1", "Admin vào Lịch khởi hành -> Bấm '+ Mở đợt khởi hành mới'", act_step, 575, 130, 330, 50)
    p10.add_vertex("a3_s2", "Chọn Tour, Ngày đi, Ngày về, Tổng số chỗ, Chọn Hướng dẫn viên", act_step, 560, 210, 360, 50)
    p10.add_vertex("a3_d1", "Ngày đi < Ngày về & Tổng chỗ > 0?", act_diamond, 640, 290, 200, 70)
    p10.add_vertex("a3_err1", "Báo lỗi thời gian hoặc số chỗ không hợp lệ", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 260, 300, 260, 50)
    p10.add_vertex("a3_s3", "Kiểm tra lịch bận của HDV trong khoảng thời gian đã chọn", act_step, 580, 400, 320, 50)
    p10.add_vertex("a3_d2", "HDV có bị trùng lịch dẫn tour khác?", act_diamond, 640, 480, 200, 70)
    p10.add_vertex("a3_err2", "Cảnh báo trùng lịch -> Yêu cầu chọn HDV khác", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 1000, 490, 260, 50)
    p10.add_vertex("a3_s4", "Thiết lập: available_slots = total_slots, status = 'OPEN'", act_step, 580, 590, 320, 50)
    p10.add_vertex("a3_s5", "Lưu bản ghi vào bảng Departures trong CSDL", act_step, 600, 670, 280, 50)
    
    # Trip Lifecycle
    p10.add_vertex("a3_lc", "Vòng đời chuyến đi: Khi đến ngày khởi hành -> Bấm 'Bắt đầu' (status=RUNNING, HDV=ON_TOUR)<br/>Khi kết thúc -> Bấm 'Hoàn tất' (status=COMPLETED, HDV=AVAILABLE)",
                   act_step + "fillColor=#fef3c7;strokeColor=#d97706;", 475, 755, 530, 60)
    p10.add_vertex("a3_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 860, 30, 30)

    p10.add_edge("ea3_0", "", act_edge, "a3_init", "a3_s1")
    p10.add_edge("ea3_1", "", act_edge, "a3_s1", "a3_s2")
    p10.add_edge("ea3_2", "", act_edge, "a3_s2", "a3_d1")
    p10.add_edge("ea3_e1", "Sai", act_edge, "a3_d1", "a3_err1")
    p10.add_edge("ea3_re1", "", act_edge, "a3_err1", "a3_s2")
    p10.add_edge("ea3_3", "Đúng", act_edge, "a3_d1", "a3_s3")
    p10.add_edge("ea3_4", "", act_edge, "a3_s3", "a3_d2")
    p10.add_edge("ea3_e2", "Bị trùng", act_edge, "a3_d2", "a3_err2")
    p10.add_edge("ea3_re2", "", act_edge, "a3_err2", "a3_s2")
    p10.add_edge("ea3_5", "Không trùng", act_edge, "a3_d2", "a3_s4")
    p10.add_edge("ea3_6", "", act_edge, "a3_s4", "a3_s5")
    p10.add_edge("ea3_7", "", act_edge, "a3_s5", "a3_lc")
    p10.add_edge("ea3_8", "", act_edge, "a3_lc", "a3_end")


    # =========================================================================
    # 11. UC003 - QUẢN LÝ LỊCH KHỞI HÀNH (SEQUENCE DIAGRAM)
    # =========================================================================
    p11 = df.add_page("p11_uc003_seq", "11. UC003 - Lịch khởi hành (Sequence)")
    p11.add_vertex("p11_title", "<b>UC003: QUẢN LÝ LỊCH KHỞI HÀNH VÀ ĐIỀU PHỐI HDV (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p11.add_vertex("l3_adm", "Admin<br/>(Actor)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 80, 80, 100, 680)
    p11.add_vertex("l3_ui", "DepartureView<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 360, 80, 120, 680)
    p11.add_vertex("l3_rtr", "DepartureRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 680, 80, 130, 680)
    p11.add_vertex("l3_grtr", "GuideRouter / CRUD<br/>(Service)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 1000, 80, 130, 680)
    p11.add_vertex("l3_db", "Database<br/>(departures, guides)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1320, 80, 130, 680)

    p11.add_vertex("l3_m1", "1. Điền form mở đợt mới (tour_id, dates, total_slots, guide_id)", "text;html=1;align=center;fontSize=11;", 130, 170, 270, 20)
    p11.add_edge("es3_1", "", call_e, "l3_adm", "l3_ui", [(130, 190), (420, 190)])

    p11.add_vertex("l3_m2", "2. GET /departures/check-conflict?guide_id=...&from=...&to=...", "text;html=1;align=center;fontSize=11;", 440, 215, 300, 20)
    p11.add_edge("es3_2", "", call_e, "l3_ui", "l3_rtr", [(420, 235), (745, 235)])

    p11.add_vertex("l3_m3", "3. check_guide_schedule_conflict()", "text;html=1;align=center;fontSize=11;", 760, 260, 230, 20)
    p11.add_edge("es3_3", "", call_e, "l3_rtr", "l3_grtr", [(745, 280), (1065, 280)])

    p11.add_vertex("l3_m4", "4. Trả về: {conflict: false, message: 'HDV sẵn sàng'}", "text;html=1;align=center;fontSize=11;", 760, 305, 260, 20)
    p11.add_edge("es3_4", "", ret_e, "l3_grtr", "l3_rtr", [(1065, 325), (745, 325)])

    p11.add_vertex("l3_m5", "5. POST /departures (Tạo lịch mới)", "text;html=1;align=center;fontSize=11;", 440, 360, 240, 20)
    p11.add_edge("es3_5", "", call_e, "l3_ui", "l3_rtr", [(420, 380), (745, 380)])

    p11.add_vertex("l3_m6", "6. INSERT INTO departures (available_slots=total_slots, status='OPEN')", "text;html=1;align=center;fontSize=11;", 780, 410, 370, 20)
    p11.add_edge("es3_6", "", call_e, "l3_rtr", "l3_db", [(745, 430), (1385, 430)])

    p11.add_vertex("l3_m7", "7. 201 Created -> Cập nhật bảng hiển thị", "text;html=1;align=center;fontSize=11;", 440, 465, 230, 20)
    p11.add_edge("es3_7", "", ret_e, "l3_rtr", "l3_ui", [(745, 485), (420, 485)])
    p11.add_edge("es3_8", "", ret_e, "l3_ui", "l3_adm", [(420, 505), (130, 505)])

    p11.add_vertex("l3_m8", "8. Khi đến ngày đi -> Admin bấm 'Bắt đầu' -> POST /{id}/start", "text;html=1;align=center;fontSize=11;", 130, 550, 320, 20)
    p11.add_edge("es3_9", "", call_e, "l3_adm", "l3_ui", [(130, 570), (420, 570)])
    p11.add_edge("es3_10", "", call_e, "l3_ui", "l3_rtr", [(420, 570), (745, 570)])
    p11.add_edge("es3_11", "UPDATE status='RUNNING'", call_e, "l3_rtr", "l3_db", [(745, 570), (1385, 570)])


    # =========================================================================
    # 12. UC004 - KHÁCH HÀNG & ĐẶT CHỖ (ACTIVITY DIAGRAM)
    # =========================================================================
    p12 = df.add_page("p12_uc004_act", "12. UC004 - Khách hàng & Đặt chỗ (Activity)")
    p12.add_vertex("p12_title", "<b>UC004: KHÁCH HÀNG & QUẢN LÝ ĐẶT CHỖ (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p12.add_vertex("a4_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 60, 30, 30)
    
    # 2 Entry points
    p12.add_vertex("a4_guest", "Nhánh 1: Khách vãng lai gửi form yêu cầu tour<br/>(status = 'WAITING_CONFIRM', <b>chưa trừ chỗ</b>)", act_step + "fillColor=#e0f2fe;strokeColor=#0284c7;", 250, 120, 320, 60)
    p12.add_vertex("a4_consult", "Nhánh 2: Nhân viên tiếp nhận khách & Hàng chờ tư vấn<br/>(Tra cứu hoặc tạo mới hồ sơ Customer)", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 880, 120, 320, 60)

    p12.add_vertex("a4_d_approve", "Tư vấn viên liên hệ: Khách xác nhận đi hay Hủy?", act_diamond, 620, 220, 240, 70)
    p12.add_vertex("a4_cancel", "Bấm 'Từ chối' -> status = 'CANCELLED' (Nhập lý do)", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 250, 230, 300, 50)
    
    p12.add_vertex("a4_confirm", "Bấm 'Xác Nhận Giữ Chỗ' (Kèm Idempotency-Key chống gửi lặp)", act_step, 575, 330, 330, 50)
    p12.add_vertex("a4_lock", "Backend mở Transaction & Khóa bản ghi (SELECT ... FOR UPDATE)", act_step, 570, 415, 340, 50)
    p12.add_vertex("a4_d_slots", "Số chỗ khả dụng (available_slots) >= Số khách đặt?", act_diamond, 605, 500, 270, 70)
    
    p12.add_vertex("a4_err_slot", "Không đủ chỗ -> Rollback Transaction -> Báo lỗi 'Hết chỗ'", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 1000, 510, 320, 50)

    p12.add_vertex("a4_deduct", "Trừ số chỗ: available_slots -= num_people<br/>Nếu available_slots == 0 -> Đổi status đợt sang 'FULL'", act_step, 580, 610, 320, 55)
    p12.add_vertex("a4_update_bk", "Cập nhật Booking: status = 'PENDING', sinh mã BK-...<br/>Lưu Idempotency Key vào booking_request_keys", act_step, 580, 700, 320, 55)
    p12.add_vertex("a4_commit", "Commit Transaction -> Đồng bộ số liệu sang phân hệ Kế toán", act_step, 590, 790, 300, 50)
    p12.add_vertex("a4_done", "Xuất thông báo 'Giữ chỗ thành công!' (Trạng thái: Chờ thanh toán)", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 580, 875, 320, 50)
    p12.add_vertex("a4_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 960, 30, 30)

    p12.add_edge("ea4_0a", "", act_edge, "a4_init", "a4_guest")
    p12.add_edge("ea4_0b", "", act_edge, "a4_init", "a4_consult")
    p12.add_edge("ea4_1a", "", act_edge, "a4_guest", "a4_d_approve")
    p12.add_edge("ea4_1b", "", act_edge, "a4_consult", "a4_d_approve")
    p12.add_edge("ea4_c", "Khách hủy/từ chối", act_edge, "a4_d_approve", "a4_cancel")
    p12.add_edge("ea4_ok", "Khách xác nhận", act_edge, "a4_d_approve", "a4_confirm")
    p12.add_edge("ea4_2", "", act_edge, "a4_confirm", "a4_lock")
    p12.add_edge("ea4_3", "", act_edge, "a4_lock", "a4_d_slots")
    p12.add_edge("ea4_err", "Không đủ", act_edge, "a4_d_slots", "a4_err_slot")
    p12.add_edge("ea4_pass", "Đủ chỗ", act_edge, "a4_d_slots", "a4_deduct")
    p12.add_edge("ea4_4", "", act_edge, "a4_deduct", "a4_update_bk")
    p12.add_edge("ea4_5", "", act_edge, "a4_update_bk", "a4_commit")
    p12.add_edge("ea4_6", "", act_edge, "a4_commit", "a4_done")
    p12.add_edge("ea4_7", "", act_edge, "a4_done", "a4_end")


    # =========================================================================
    # 13. UC004 - KHÁCH HÀNG & ĐẶT CHỖ (SEQUENCE DIAGRAM)
    # =========================================================================
    p13 = df.add_page("p13_uc004_seq", "13. UC004 - Khách hàng & Đặt chỗ (Sequence)")
    p13.add_vertex("p13_title", "<b>UC004: XÁC NHẬN GIỮ CHỖ & KHÓA GHẾ PESSIMISTIC LOCK (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p13.add_vertex("l4_actor", "Consultant<br/>(Actor)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 60, 80, 100, 720)
    p13.add_vertex("l4_ui", "BookingUI<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 320, 80, 120, 720)
    p13.add_vertex("l4_rtr", "BookingRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 600, 80, 120, 720)
    p13.add_vertex("l4_mid", "IdempotencyService<br/>(Anti-duplicate)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 880, 80, 130, 720)
    p13.add_vertex("l4_crud", "BookingCRUD<br/>(Transaction)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 1170, 80, 120, 720)
    p13.add_vertex("l4_db", "Database<br/>(dep, bookings, keys)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1430, 80, 120, 720)

    p13.add_vertex("l4_m1", "1. Bấm 'Xác Nhận Giữ Chỗ' (req_id, departure_id, seats)", "text;html=1;align=center;fontSize=11;", 100, 170, 270, 20)
    p13.add_edge("es4_1", "", call_e, "l4_actor", "l4_ui", [(110, 190), (380, 190)])

    p13.add_vertex("l4_m2", "2. POST /bookings/{id}/confirm (Header: Idempotency-Key)", "text;html=1;align=center;fontSize=11;", 390, 215, 290, 20)
    p13.add_edge("es4_2", "", call_e, "l4_ui", "l4_rtr", [(380, 235), (660, 235)])

    p13.add_vertex("l4_m3", "3. check_idempotency_key(key)", "text;html=1;align=center;fontSize=11;", 680, 260, 210, 20)
    p13.add_edge("es4_3", "", call_e, "l4_rtr", "l4_mid", [(660, 280), (945, 280)])

    p13.add_vertex("l4_m4", "4. Key hợp lệ (chưa xử lý)", "text;html=1;align=center;fontSize=11;", 680, 305, 210, 20)
    p13.add_edge("es4_4", "", ret_e, "l4_mid", "l4_rtr", [(945, 325), (660, 325)])

    p13.add_vertex("l4_m5", "5. confirm_and_deduct_slots(booking_id, db)", "text;html=1;align=center;fontSize=11;", 680, 350, 260, 20)
    p13.add_edge("es4_5", "", call_e, "l4_rtr", "l4_crud", [(660, 370), (1230, 370)])

    p13.add_vertex("l4_m6", "6. BEGIN TRANSACTION -> SELECT available_slots FROM departures FOR UPDATE", "text;html=1;align=center;fontSize=11;", 1100, 395, 420, 20)
    p13.add_edge("es4_6", "", call_e, "l4_crud", "l4_db", [(1230, 415), (1490, 415)])

    p13.add_vertex("l4_m7", "7. Kiểm tra available_slots >= num_people -> UPDATE available_slots -= num_people", "text;html=1;align=center;fontSize=11;", 1070, 445, 450, 20)
    p13.add_edge("es4_7", "", call_e, "l4_crud", "l4_db", [(1230, 465), (1490, 465)])

    p13.add_vertex("l4_m8", "8. UPDATE bookings SET status='PENDING' & INSERT booking_request_keys -> COMMIT", "text;html=1;align=center;fontSize=11;", 1070, 495, 450, 20)
    p13.add_edge("es4_8", "", call_e, "l4_crud", "l4_db", [(1230, 515), (1490, 515)])

    p13.add_vertex("l4_m9", "9. Trả về BookingOut {booking_code: 'BK-...', status: 'PENDING'}", "text;html=1;align=center;fontSize=11;", 680, 560, 340, 20)
    p13.add_edge("es4_9", "", ret_e, "l4_crud", "l4_rtr", [(1230, 580), (660, 580)])

    p13.add_vertex("l4_m10", "10. 200 OK -> Hiển thị thông báo 'Xác nhận giữ chỗ thành công!'", "text;html=1;align=center;fontSize=11;", 110, 620, 330, 20)
    p13.add_edge("es4_10", "", ret_e, "l4_rtr", "l4_ui", [(660, 640), (380, 640)])
    p13.add_edge("es4_11", "", ret_e, "l4_ui", "l4_actor", [(380, 660), (110, 660)])


    # =========================================================================
    # 14. UC005 - QUẢN LÝ THANH TOÁN (ACTIVITY DIAGRAM)
    # =========================================================================
    p14 = df.add_page("p14_uc005_act", "14. UC005 - Quản lý Thanh toán (Activity)")
    p14.add_vertex("p14_title", "<b>UC005: QUẢN LÝ THANH TOÁN, ĐẶT CỌC VÀ HOÀN TIỀN (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p14.add_vertex("a5_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 60, 30, 30)
    p14.add_vertex("a5_s1", "Kế toán/Admin truy cập menu 'Kế toán & Thu tiền' -> Chọn đơn Booking", act_step, 545, 120, 390, 50)
    p14.add_vertex("a5_s2", "Mở modal 'Thu tiền' -> Nhập số tiền thu, Phương thức, Phân loại thu", act_step, 545, 200, 390, 50)
    p14.add_vertex("a5_d1", "Số tiền > 0 và <= Dư nợ còn lại?", act_diamond, 625, 280, 230, 70)
    p14.add_vertex("a5_err", "Báo lỗi: Số tiền không hợp lệ hoặc vượt quá dư nợ", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 220, 290, 290, 50)

    p14.add_vertex("a5_s3", "Tạo bản ghi Payments: transaction_code (UK), amount, created_by", act_step, 545, 380, 390, 50)
    p14.add_vertex("a5_s4", "Cộng dồn: paid_amount += amount của đơn booking tương ứng", act_step, 555, 460, 370, 50)
    p14.add_vertex("a5_d2", "Tỷ lệ đã thanh toán so với tổng tiền?", act_diamond, 615, 540, 250, 70)

    # Branches
    p14.add_vertex("a5_st_conf", "Đủ 100%: Cập nhật status = 'CONFIRMED' (Xác nhận đi)", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 250, 650, 330, 50)
    p14.add_vertex("a5_st_dep", "Đạt >= 30% (< 100%): Cập nhật status = 'DEPOSITED' (Đã cọc)", act_step + "fillColor=#e0f2fe;strokeColor=#0284c7;", 640, 650, 340, 50)
    p14.add_vertex("a5_st_pend", "< 30%: Giữ status = 'PENDING' (Chờ thu đủ cọc)", act_step + "fillColor=#fef3c7;strokeColor=#d97706;", 1030, 650, 300, 50)

    # Cancel & Refund Branch
    p14.add_vertex("a5_rf", "Trường hợp Hủy tour: Nếu hủy trước khởi hành -> Tính % hoàn tiền hợp lệ theo số ngày báo trước<br/>Lập phiếu chi hoàn tiền (payment_type='REFUND') & Hoàn trả số chỗ khả dụng cho departure",
                   act_step + "fillColor=#fee2e2;strokeColor=#dc2626;", 440, 740, 600, 65)
    
    p14.add_vertex("a5_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 845, 30, 30)

    p14.add_edge("ea5_0", "", act_edge, "a5_init", "a5_s1")
    p14.add_edge("ea5_1", "", act_edge, "a5_s1", "a5_s2")
    p14.add_edge("ea5_2", "", act_edge, "a5_s2", "a5_d1")
    p14.add_edge("ea5_err", "Sai", act_edge, "a5_d1", "a5_err")
    p14.add_edge("ea5_re", "", act_edge, "a5_err", "a5_s2")
    p14.add_edge("ea5_3", "Đúng", act_edge, "a5_d1", "a5_s3")
    p14.add_edge("ea5_4", "", act_edge, "a5_s3", "a5_s4")
    p14.add_edge("ea5_5", "", act_edge, "a5_s4", "a5_d2")
    p14.add_edge("ea5_b1", "100%", act_edge, "a5_d2", "a5_st_conf")
    p14.add_edge("ea5_b2", ">= 30%", act_edge, "a5_d2", "a5_st_dep")
    p14.add_edge("ea5_b3", "< 30%", act_edge, "a5_d2", "a5_st_pend")
    p14.add_edge("ea5_e1", "", act_edge, "a5_st_conf", "a5_rf")
    p14.add_edge("ea5_e2", "", act_edge, "a5_st_dep", "a5_rf")
    p14.add_edge("ea5_e3", "", act_edge, "a5_st_pend", "a5_rf")
    p14.add_edge("ea5_e4", "", act_edge, "a5_rf", "a5_end")


    # =========================================================================
    # 15. UC005 - QUẢN LÝ THANH TOÁN (SEQUENCE DIAGRAM)
    # =========================================================================
    p15 = df.add_page("p15_uc005_seq", "15. UC005 - Quản lý Thanh toán (Sequence)")
    p15.add_vertex("p15_title", "<b>UC005: GHI NHẬN THANH TOÁN & ĐỒNG BỘ DÒNG TIỀN (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p15.add_vertex("l5_acc", "Accountant<br/>(Actor)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 80, 80, 100, 680)
    p15.add_vertex("l5_ui", "PaymentUI<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 360, 80, 120, 680)
    p15.add_vertex("l5_rtr", "PaymentRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 680, 80, 130, 680)
    p15.add_vertex("l5_srv", "PaymentService<br/>(Accounting)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 1000, 80, 130, 680)
    p15.add_vertex("l5_db", "Database<br/>(payments, bookings)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 1320, 80, 130, 680)

    p15.add_vertex("l5_m1", "1. Mở modal 'Thu tiền' -> Nhập số tiền, chọn phương thức, loại thu", "text;html=1;align=center;fontSize=11;", 130, 170, 300, 20)
    p15.add_edge("es5_1", "", call_e, "l5_acc", "l5_ui", [(130, 190), (420, 190)])

    p15.add_vertex("l5_m2", "2. POST /payments (Payload giao dịch thu tiền)", "text;html=1;align=center;fontSize=11;", 440, 215, 270, 20)
    p15.add_edge("es5_2", "", call_e, "l5_ui", "l5_rtr", [(420, 235), (745, 235)])

    p15.add_vertex("l5_m3", "3. record_payment(booking_id, amount, method, created_by)", "text;html=1;align=center;fontSize=11;", 760, 260, 310, 20)
    p15.add_edge("es5_3", "", call_e, "l5_rtr", "l5_srv", [(745, 280), (1065, 280)])

    p15.add_vertex("l5_m4", "4. INSERT INTO payments (transaction_code, amount, status='SUCCESS')", "text;html=1;align=center;fontSize=11;", 1080, 305, 360, 20)
    p15.add_edge("es5_4", "", call_e, "l5_srv", "l5_db", [(1065, 325), (1385, 325)])

    p15.add_vertex("l5_m5", "5. UPDATE bookings SET paid_amount += amount, status='CONFIRMED' / 'DEPOSITED'", "text;html=1;align=center;fontSize=11;", 1070, 360, 390, 20)
    p15.add_edge("es5_5", "", call_e, "l5_srv", "l5_db", [(1065, 380), (1385, 380)])

    p15.add_vertex("l5_m6", "6. COMMIT TRANSACTION -> Trả về PaymentReceipt", "text;html=1;align=center;fontSize=11;", 760, 420, 290, 20)
    p15.add_edge("es5_6", "", ret_e, "l5_srv", "l5_rtr", [(1065, 440), (745, 440)])

    p15.add_vertex("l5_m7", "7. 201 Created -> Cập nhật bảng thanh toán & Đổi màu nhãn trạng thái", "text;html=1;align=center;fontSize=11;", 130, 490, 350, 20)
    p15.add_edge("es5_7", "", ret_e, "l5_rtr", "l5_ui", [(745, 510), (420, 510)])
    p15.add_edge("es5_8", "", ret_e, "l5_ui", "l5_acc", [(420, 530), (130, 530)])


    # =========================================================================
    # 16. UC006 - PHẢN HỒI & AI TÓM TẮT (ACTIVITY DIAGRAM)
    # =========================================================================
    p16 = df.add_page("p16_uc006_act", "16. UC006 - Phản hồi & AI (Activity)")
    p16.add_vertex("p16_title", "<b>UC006: QUẢN LÝ PHẢN HỒI & AI TÓM TẮT SENTIMENT (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p16.add_vertex("a6_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 70, 30, 30)
    p16.add_vertex("a6_s1", "Khách hàng sau chuyến đi gửi khảo sát (Sao tour 1-5, Sao HDV 1-5, Nhận xét)", act_step, 530, 130, 420, 50)
    p16.add_vertex("a6_s2", "Lưu phản hồi vào bảng Feedbacks trong CSDL", act_step, 590, 210, 300, 50)
    p16.add_vertex("a6_s3", "Admin/Consultant vào menu 'Phản Hồi' -> Bấm 'AI Tóm tắt phản hồi theo Tour'", act_step, 535, 290, 410, 50)
    p16.add_vertex("a6_d1", "Tour đã có ít nhất 1 nhận xét?", act_diamond, 640, 370, 200, 70)
    p16.add_vertex("a6_err", "Báo lỗi: 'Chưa có dữ liệu phản hồi để AI phân tích'", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 240, 380, 310, 50)

    p16.add_vertex("a6_s4", "Backend gom toàn bộ text review của tour -> Gửi sang Gemini AI Engine", act_step + "fillColor=#f3e8ff;strokeColor=#9333ea;", 540, 480, 400, 50)
    p16.add_vertex("a6_s5", "Gemini phân tích Sentiment (Tích cực/Tiêu cực/Trung lập)<br/>Trích xuất: Điểm khen ngợi, Điểm cần khắc phục, Đánh giá chất lượng HDV, Đề xuất cải tiến",
                   act_step + "fillColor=#f3e8ff;strokeColor=#9333ea;", 480, 560, 520, 65)
    p16.add_vertex("a6_s6", "Lưu vết truy vấn vào bảng ai_session_logs (feature_type='FEEDBACK_SUMMARY')", act_step, 520, 660, 440, 50)
    p16.add_vertex("a6_s7", "Hiển thị Dashboard phân tích AI trực quan cho Ban Giám Đốc", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 565, 740, 350, 50)
    p16.add_vertex("a6_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 830, 30, 30)

    p16.add_edge("ea6_0", "", act_edge, "a6_init", "a6_s1")
    p16.add_edge("ea6_1", "", act_edge, "a6_s1", "a6_s2")
    p16.add_edge("ea6_2", "", act_edge, "a6_s2", "a6_s3")
    p16.add_edge("ea6_3", "", act_edge, "a6_s3", "a6_d1")
    p16.add_edge("ea6_e", "Chưa có", act_edge, "a6_d1", "a6_err")
    p16.add_edge("ea6_ok", "Đã có", act_edge, "a6_d1", "a6_s4")
    p16.add_edge("ea6_4", "", act_edge, "a6_s4", "a6_s5")
    p16.add_edge("ea6_5", "", act_edge, "a6_s5", "a6_s6")
    p16.add_edge("ea6_6", "", act_edge, "a6_s6", "a6_s7")
    p16.add_edge("ea6_7", "", act_edge, "a6_s7", "a6_end")


    # =========================================================================
    # 17. UC006 - PHẢN HỒI & AI TÓM TẮT (SEQUENCE DIAGRAM)
    # =========================================================================
    p17 = df.add_page("p17_uc006_seq", "17. UC006 - Phản hồi & AI (Sequence)")
    p17.add_vertex("p17_title", "<b>UC006: AI PHÂN TÍCH CẢM XÚC VÀ TÓM TẮT PHẢN HỒI (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p17.add_vertex("l6_adm", "Admin / User<br/>(Actor)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 60, 80, 100, 680)
    p17.add_vertex("l6_ui", "FeedbackUI / AIHub<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 340, 80, 130, 680)
    p17.add_vertex("l6_rtr", "AIRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 640, 80, 120, 680)
    p17.add_vertex("l6_srv", "AIService<br/>(Gemini Engine)", seq_life + "fillColor=#f3e8ff;strokeColor=#9333ea;", 940, 80, 130, 680)
    p17.add_vertex("l6_gem", "Google Gemini API<br/>(Cloud)", seq_life + "fillColor=#f3e8ff;strokeColor=#7e22ce;", 1240, 80, 130, 680)
    p17.add_vertex("l6_db", "Database<br/>(feedbacks, ai_logs)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1490, 80, 120, 680)

    p17.add_vertex("l6_m1", "1. Chọn tour -> Bấm 'Bắt đầu phân tích & tóm tắt AI'", "text;html=1;align=center;fontSize=11;", 110, 170, 260, 20)
    p17.add_edge("es6_1", "", call_e, "l6_adm", "l6_ui", [(110, 190), (405, 190)])

    p17.add_vertex("l6_m2", "2. POST /ai/summarize-feedbacks?tour_id=...", "text;html=1;align=center;fontSize=11;", 420, 215, 250, 20)
    p17.add_edge("es6_2", "", call_e, "l6_ui", "l6_rtr", [(405, 235), (700, 235)])

    p17.add_vertex("l6_m3", "3. Truy vấn danh sách đánh giá: SELECT FROM feedbacks WHERE tour_id=...", "text;html=1;align=center;fontSize=11;", 720, 260, 390, 20)
    p17.add_edge("es6_3", "", call_e, "l6_rtr", "l6_db", [(700, 280), (1550, 280)])

    p17.add_vertex("l6_m4", "4. Trả về mảng Feedbacks (comments, rating, guide_rating)", "text;html=1;align=center;fontSize=11;", 720, 305, 340, 20)
    p17.add_edge("es6_4", "", ret_e, "l6_db", "l6_rtr", [(1550, 325), (700, 325)])

    p17.add_vertex("l6_m5", "5. summarize_feedbacks(feedbacks_data)", "text;html=1;align=center;fontSize=11;", 720, 350, 250, 20)
    p17.add_edge("es6_5", "", call_e, "l6_rtr", "l6_srv", [(700, 370), (1005, 370)])

    p17.add_vertex("l6_m6", "6. Gửi request phân tích cảm xúc & tóm tắt", "text;html=1;align=center;fontSize=11;", 1020, 395, 250, 20)
    p17.add_edge("es6_6", "", call_e, "l6_srv", "l6_gem", [(1005, 415), (1305, 415)])

    p17.add_vertex("l6_m7", "7. Trả về JSON: {sentiment, strengths, weaknesses, guide_eval, suggestions}", "text;html=1;align=center;fontSize=11;", 920, 440, 420, 20)
    p17.add_edge("es6_7", "", ret_e, "l6_gem", "l6_srv", [(1305, 460), (1005, 460)])

    p17.add_vertex("l6_m8", "8. INSERT INTO ai_session_logs (...) -> Log phiên phân tích", "text;html=1;align=center;fontSize=11;", 1020, 485, 340, 20)
    p17.add_edge("es6_8", "", call_e, "l6_srv", "l6_db", [(1005, 505), (1550, 505)])

    p17.add_vertex("l6_m9", "9. Trả kết quả tóm tắt có cấu trúc", "text;html=1;align=center;fontSize=11;", 420, 545, 230, 20)
    p17.add_edge("es6_9", "", ret_e, "l6_rtr", "l6_ui", [(700, 565), (405, 565)])
    p17.add_edge("es6_10", "Hiển thị 4 khối phân tích", ret_e, "l6_ui", "l6_adm", [(405, 595), (110, 595)])


    # =========================================================================
    # 18. UC007 - QUẢN LÝ HƯỚNG DẪN VIÊN (ACTIVITY DIAGRAM)
    # =========================================================================
    p18 = df.add_page("p18_uc007_act", "18. UC007 - Hướng dẫn viên (Activity)")
    p18.add_vertex("p18_title", "<b>UC007: QUẢN LÝ HƯỚNG DẪN VIÊN & ĐIỀU PHỐI TOUR (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p18.add_vertex("a7_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 70, 30, 30)
    p18.add_vertex("a7_s1", "Admin truy cập menu 'Quản lý Hướng Dẫn Viên'", act_step, 570, 130, 310, 50)
    p18.add_vertex("a7_s2", "Chọn 'Thêm HDV mới' hoặc 'Cập nhật' thông tin", act_step, 570, 210, 310, 50)
    p18.add_vertex("a7_s3", "Nhập: Họ tên, SĐT, Email, Ngôn ngữ, Số năm kinh nghiệm, Ghi chú", act_step, 540, 290, 370, 50)
    p18.add_vertex("a7_val", "Kiểm tra hợp lệ: Họ tên, SĐT không được để trống", act_step, 570, 370, 310, 50)
    p18.add_vertex("a7_save", "Lưu thông tin vào bảng tour_guides trong CSDL", act_step, 570, 450, 310, 50)
    
    # State tracking
    p18.add_vertex("a7_state", "Theo dõi trạng thái công tác: AVAILABLE (Rảnh) / ON_TOUR (Đang dẫn tour) / OFF (Nghỉ)<br/>Khi một đợt khởi hành chuyển RUNNING -> HDV tự động chuyển ON_TOUR<br/>Khi đợt khởi hành chuyển COMPLETED -> HDV tự động chuyển về AVAILABLE",
                   act_step + "fillColor=#fef3c7;strokeColor=#d97706;", 460, 530, 530, 65)

    # Delete check
    p18.add_vertex("a7_d_del", "Thao tác Xóa: HDV đang được phân công vào đợt khởi hành sắp tới?", act_diamond, 585, 630, 280, 70)
    p18.add_vertex("a7_err_del", "Chặn xóa & Báo lỗi: 'Không thể xóa HDV đang có lịch dẫn tour'", act_step + "fillColor=#fee2e2;strokeColor=#ef4444;", 180, 640, 330, 50)
    p18.add_vertex("a7_ok_del", "Cho phép xóa hoặc chuyển trạng thái sang OFF", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 600, 740, 250, 50)
    p18.add_vertex("a7_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 830, 30, 30)

    p18.add_edge("ea7_0", "", act_edge, "a7_init", "a7_s1")
    p18.add_edge("ea7_1", "", act_edge, "a7_s1", "a7_s2")
    p18.add_edge("ea7_2", "", act_edge, "a7_s2", "a7_s3")
    p18.add_edge("ea7_3", "", act_edge, "a7_s3", "a7_val")
    p18.add_edge("ea7_4", "", act_edge, "a7_val", "a7_save")
    p18.add_edge("ea7_5", "", act_edge, "a7_save", "a7_state")
    p18.add_edge("ea7_6", "", act_edge, "a7_state", "a7_d_del")
    p18.add_edge("ea7_e", "Có lịch", act_edge, "a7_d_del", "a7_err_del")
    p18.add_edge("ea7_ok", "Không có lịch", act_edge, "a7_d_del", "a7_ok_del")
    p18.add_edge("ea7_7", "", act_edge, "a7_ok_del", "a7_end")


    # =========================================================================
    # 19. UC007 - QUẢN LÝ HƯỚNG DẪN VIÊN (SEQUENCE DIAGRAM)
    # =========================================================================
    p19 = df.add_page("p19_uc007_seq", "19. UC007 - Hướng dẫn viên (Sequence)")
    p19.add_vertex("p19_title", "<b>UC007: QUẢN LÝ HỒ SƠ VÀ TRẠNG THÁI HƯỚNG DẪN VIÊN (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p19.add_vertex("l7_adm", "Admin<br/>(Actor)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 80, 80, 100, 680)
    p19.add_vertex("l7_ui", "GuideView<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 360, 80, 120, 680)
    p19.add_vertex("l7_rtr", "GuideRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 680, 80, 130, 680)
    p19.add_vertex("l7_crud", "GuideCRUD<br/>(Repository)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 1000, 80, 130, 680)
    p19.add_vertex("l7_db", "Database<br/>(tour_guides, departures)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1320, 80, 130, 680)

    p19.add_vertex("l7_m1", "1. Mở modal 'Thêm HDV' -> Nhập họ tên, SĐT, ngôn ngữ, thâm niên", "text;html=1;align=center;fontSize=11;", 130, 170, 310, 20)
    p19.add_edge("es7_1", "", call_e, "l7_adm", "l7_ui", [(130, 190), (420, 190)])

    p19.add_vertex("l7_m2", "2. POST /guides (Payload GuideCreate)", "text;html=1;align=center;fontSize=11;", 440, 215, 240, 20)
    p19.add_edge("es7_2", "", call_e, "l7_ui", "l7_rtr", [(420, 235), (745, 235)])

    p19.add_vertex("l7_m3", "3. create_guide(db, guide_data)", "text;html=1;align=center;fontSize=11;", 760, 260, 220, 20)
    p19.add_edge("es7_3", "", call_e, "l7_rtr", "l7_crud", [(745, 280), (1065, 280)])

    p19.add_vertex("l7_m4", "4. INSERT INTO tour_guides (status='AVAILABLE', rating=5.0) -> COMMIT", "text;html=1;align=center;fontSize=11;", 1070, 305, 380, 20)
    p19.add_edge("es7_4", "", call_e, "l7_crud", "l7_db", [(1065, 325), (1385, 325)])

    p19.add_vertex("l7_m5", "5. 201 Created -> Trả về GuideOut", "text;html=1;align=center;fontSize=11;", 760, 360, 220, 20)
    p19.add_edge("es7_5", "", ret_e, "l7_crud", "l7_rtr", [(1065, 380), (745, 380)])

    p19.add_vertex("l7_m6", "6. Hiển thị HDV mới trên danh sách & Kích hoạt trạng thái 'Sẵn sàng'", "text;html=1;align=center;fontSize=11;", 130, 420, 340, 20)
    p19.add_edge("es7_6", "", ret_e, "l7_rtr", "l7_ui", [(745, 440), (420, 440)])
    p19.add_edge("es7_7", "", ret_e, "l7_ui", "l7_adm", [(420, 460), (130, 460)])

    p19.add_vertex("l7_m7", "7. DELETE /guides/{id} -> Kiểm tra departures liên kết -> Xóa thành công", "text;html=1;align=center;fontSize=11;", 440, 520, 360, 20)
    p19.add_edge("es7_8", "", call_e, "l7_adm", "l7_ui", [(130, 540), (420, 540)])
    p19.add_edge("es7_9", "", call_e, "l7_ui", "l7_rtr", [(420, 540), (745, 540)])
    p19.add_edge("es7_10", "", call_e, "l7_rtr", "l7_db", [(745, 540), (1385, 540)])


    # =========================================================================
    # 20. UC008 - THỐNG KÊ & BÁO CÁO (ACTIVITY DIAGRAM)
    # =========================================================================
    p20 = df.add_page("p20_uc008_act", "20. UC008 - Thống kê & Báo cáo (Activity)")
    p20.add_vertex("p20_title", "<b>UC008: THỐNG KÊ DOANH THU VÀ PHÂN TÍCH TỶ LỆ LẤP ĐẦY (ACTIVITY DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p20.add_vertex("a8_init", "", "ellipse;fillColor=#0f172a;strokeColor=none;html=1;", 725, 70, 30, 30)
    p20.add_vertex("a8_s1", "Admin/Kế toán truy cập màn hình 'Thống Kê Doanh Thu'", act_step, 545, 130, 360, 50)
    p20.add_vertex("a8_s2", "Hệ thống truy vấn tổng hợp từ các bảng Payments, Bookings, Departures, Tours", act_step, 510, 210, 430, 50)

    # Fork 3 metrics
    p20.add_vertex("a8_fork", "", "rounded=0;fillColor=#1e293b;strokeColor=none;", 450, 290, 550, 8)
    
    p20.add_vertex("a8_m1", "1. Tính Doanh thu theo từng Tour:<br/>SUM(payments.amount) - SUM(refunds)<br/>Sắp xếp giảm dần -> Lấy Top tour", act_step, 200, 340, 300, 60)
    p20.add_vertex("a8_m2", "2. Tính Tỷ lệ lấp đầy ghế ngồi toàn hệ thống:<br/>(Tổng ghế đã bán / Tổng ghế mở bán) * 100%<br/>Phân chia phần trăm 'Đã đặt' vs 'Còn trống'", act_step, 550, 340, 350, 60)
    p20.add_vertex("a8_m3", "3. Tính Tổng thực thu toàn công ty &<br/>Doanh thu dự kiến từ các đơn PENDING", act_step, 950, 340, 300, 60)

    # Join
    p20.add_vertex("a8_join", "", "rounded=0;fillColor=#1e293b;strokeColor=none;", 450, 440, 550, 8)

    p20.add_vertex("a8_render1", "Vẽ Biểu đồ cột: 'Top Tour Đóng Góp Doanh Thu Cao Nhất' (Tooltip hiển thị tiền tệ)", act_step + "fillColor=#e0f2fe;strokeColor=#0284c7;", 510, 480, 430, 50)
    p20.add_vertex("a8_render2", "Vẽ Biểu đồ tròn: 'Tỷ Lệ Lấp Đầy Chỗ Ngồi' (Chart.js Doughnut)", act_step + "fillColor=#dcfce7;strokeColor=#16a34a;", 530, 560, 390, 50)
    p20.add_vertex("a8_render3", "Hiển thị các khối KPI Card: Doanh thu thực tế, Số giao dịch hoàn tất", act_step + "fillColor=#fef3c7;strokeColor=#d97706;", 510, 640, 430, 50)
    p20.add_vertex("a8_end", "", "ellipse;html=1;shape=endState;fillColor=#0f172a;strokeColor=#ef4444;strokeWidth=2;", 725, 730, 30, 30)

    p20.add_edge("ea8_0", "", act_edge, "a8_init", "a8_s1")
    p20.add_edge("ea8_1", "", act_edge, "a8_s1", "a8_s2")
    p20.add_edge("ea8_2", "", act_edge, "a8_s2", "a8_fork")
    p20.add_edge("ea8_f1", "", act_edge, "a8_fork", "a8_m1")
    p20.add_edge("ea8_f2", "", act_edge, "a8_fork", "a8_m2")
    p20.add_edge("ea8_f3", "", act_edge, "a8_fork", "a8_m3")
    p20.add_edge("ea8_j1", "", act_edge, "a8_m1", "a8_join")
    p20.add_edge("ea8_j2", "", act_edge, "a8_m2", "a8_join")
    p20.add_edge("ea8_j3", "", act_edge, "a8_m3", "a8_join")
    p20.add_edge("ea8_3", "", act_edge, "a8_join", "a8_render1")
    p20.add_edge("ea8_4", "", act_edge, "a8_render1", "a8_render2")
    p20.add_edge("ea8_5", "", act_edge, "a8_render2", "a8_render3")
    p20.add_edge("ea8_6", "", act_edge, "a8_render3", "a8_end")


    # =========================================================================
    # 21. UC008 - THỐNG KÊ & BÁO CÁO (SEQUENCE DIAGRAM)
    # =========================================================================
    p21 = df.add_page("p21_uc008_seq", "21. UC008 - Thống kê & Báo cáo (Sequence)")
    p21.add_vertex("p21_title", "<b>UC008: TRUY VẤN DỮ LIỆU VÀ VẼ BIỂU ĐỒ BÁO CÁO DOANH THU (SEQUENCE DIAGRAM)</b>",
                   "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#0f172a;",
                   300, 20, 1000, 35)

    p21.add_vertex("l8_acc", "Accountant / Admin<br/>(Actor)", seq_life + "fillColor=#fef3c7;strokeColor=#d97706;", 80, 80, 120, 680)
    p21.add_vertex("l8_ui", "StatsView<br/>(Frontend)", seq_life + "fillColor=#f8fafc;strokeColor=#475569;", 380, 80, 120, 680)
    p21.add_vertex("l8_rtr", "StatsRouter<br/>(FastAPI)", seq_life + "fillColor=#dcfce7;strokeColor=#16a34a;", 700, 80, 130, 680)
    p21.add_vertex("l8_db", "Database<br/>(payments, dep, tours)", seq_life + "fillColor=#fee2e2;strokeColor=#dc2626;", 1020, 80, 140, 680)
    p21.add_vertex("l8_chart", "ChartService<br/>(Chart.js Engine)", seq_life + "fillColor=#e0f2fe;strokeColor=#0284c7;", 1340, 80, 130, 680)

    p21.add_vertex("l8_m1", "1. Bấm menu 'Thống Kê Doanh Thu'", "text;html=1;align=center;fontSize=11;", 150, 170, 220, 20)
    p21.add_edge("es8_1", "", call_e, "l8_acc", "l8_ui", [(140, 190), (440, 190)])

    p21.add_vertex("l8_m2", "2. Gửi đồng thời: GET /stats/summary & GET /stats/revenue-by-tour", "text;html=1;align=center;fontSize=11;", 450, 215, 340, 20)
    p21.add_edge("es8_2", "", call_e, "l8_ui", "l8_rtr", [(440, 235), (765, 235)])

    p21.add_vertex("l8_m3", "3. Truy vấn tổng hợp doanh thu: SELECT tour, SUM(amount) FROM payments...", "text;html=1;align=center;fontSize=11;", 780, 260, 390, 20)
    p21.add_edge("es8_3", "", call_e, "l8_rtr", "l8_db", [(765, 280), (1090, 280)])

    p21.add_vertex("l8_m4", "4. Truy vấn số ghế: SELECT SUM(total_slots), SUM(available_slots) FROM departures", "text;html=1;align=center;fontSize=11;", 770, 305, 410, 20)
    p21.add_edge("es8_4", "", call_e, "l8_rtr", "l8_db", [(765, 325), (1090, 325)])

    p21.add_vertex("l8_m5", "5. Trả về kết quả JSON {total_revenue, top_tours, occupancy_rate}", "text;html=1;align=center;fontSize=11;", 450, 360, 340, 20)
    p21.add_edge("es8_5", "", ret_e, "l8_rtr", "l8_ui", [(765, 380), (440, 380)])

    p21.add_vertex("l8_m6", "6. renderTopToursChart(top_tours) & renderOccupancy(occupancy_rate)", "text;html=1;align=center;fontSize=11;", 450, 420, 370, 20)
    p21.add_edge("es8_6", "", call_e, "l8_ui", "l8_chart", [(440, 440), (1405, 440)])

    p21.add_vertex("l8_m7", "7. Vẽ biểu đồ cột và biểu đồ tròn hoàn tất", "text;html=1;align=center;fontSize=11;", 450, 475, 260, 20)
    p21.add_edge("es8_7", "", ret_e, "l8_chart", "l8_ui", [(1405, 495), (440, 495)])

    p21.add_vertex("l8_m8", "8. Hiển thị Dashboard hoàn chỉnh, hỗ trợ hover tooltip xem số liệu", "text;html=1;align=center;fontSize=11;", 140, 545, 340, 20)
    p21.add_edge("es8_8", "", ret_e, "l8_ui", "l8_acc", [(440, 565), (140, 565)])

    # Output file
    output_path = os.path.abspath("docs/diagrams/vietjourney_all_diagrams.drawio")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    xml_content = df.to_xml()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    print(f"Thành công! Đã tạo file Draw.io: {output_path}")
    print(f"Tổng số trang sơ đồ: {len(df.pages)}")
    return output_path

if __name__ == "__main__":
    build_drawio_file()
