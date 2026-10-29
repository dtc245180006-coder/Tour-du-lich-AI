"""
Script tạo tệp Word .docx hoàn chỉnh cho "TÀI LIỆU HƯỚNG DẪN SỬ DỤNG - V1.0"
Áp dụng chuẩn định dạng Word: Times New Roman, Heading phân cấp, Bảng biểu chuyên nghiệp, Hình ảnh minh họa có chú thích.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_user_guide_docx(output_path):
    doc = docx.Document()

    # Page Margins (Left 2.5cm, Right 2.0cm, Top 2.0cm, Bottom 2.0cm)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    # Styles
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(12)
    normal_font.color.rgb = RGBColor(15, 23, 42)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(4)

    # Helper functions
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(3, 105, 161)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(14)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(71, 85, 105)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(2, 132, 199)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(15, 118, 110)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
        r = p.add_run(text)
        r.italic = italic
        return p

    def add_callout(text, prefix="Lưu ý quan trọng: "):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.25)
        r_pre = p.add_run(prefix)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(185, 28, 28)
        r = p.add_run(text)
        r.italic = True
        return p

    def add_img(img_path, caption_text, width=Inches(5.8)):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            doc.add_picture(img_path, width=width)
            # Center picture
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r = p_cap.add_run(caption_text)
            r.italic = True
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(100, 116, 139)

    # ==================== COVER & HEADER ====================
    add_title("Hệ thống quản lý tour du lịch có tích hợp AI")
    add_subtitle("TÀI LIỆU HƯỚNG DẪN SỬ DỤNG – V1.0")

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.space_after = Pt(18)
    r_info = p_info.add_run("Nhóm thực hiện: Nhóm 17 (Bùi Văn Trường, Hà Thành Duy)\nĐịa chỉ truy cập: http://127.0.0.1:8000 | Phiên bản mã nguồn: V1.0 (Tháng 10/2026)")
    r_info.italic = True
    r_info.font.size = Pt(10.5)
    r_info.font.color.rgb = RGBColor(100, 116, 139)

    # ==================== MỤC LỤC ====================
    p_toc_head = doc.add_paragraph()
    p_toc_head.paragraph_format.space_after = Pt(4)
    r_th = p_toc_head.add_run("NỘI DUNG TÀI LIỆU")
    r_th.bold = True
    r_th.font.size = Pt(12)

    toc_items = [
        ("1. GIỚI THIỆU ỨNG DỤNG", "Trang 2"),
        ("2. CẤU HÌNH PHẦN CỨNG - PHẦN MỀM", "Trang 2"),
        ("   2.1 Phần cứng", "Trang 2"),
        ("   2.2 Phần mềm", "Trang 3"),
        ("3. CÁC CHỨC NĂNG CHÍNH", "Trang 4"),
        ("   3.1 Chức năng của Khách vãng lai", "Trang 4"),
        ("   3.2 Chức năng của Quản trị viên (Admin)", "Trang 5"),
        ("   3.3 Chức năng của Nhân viên tư vấn (Consultant)", "Trang 8"),
        ("   3.4 Chức năng của Kế toán (Accountant)", "Trang 10"),
        ("4. XỬ LÝ SỰ CỐ VÀ LƯU Ý SỬ DỤNG", "Trang 12")
    ]
    for item, page in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(2)
        r1 = p_t.add_run(item)
        if item.startswith("   "):
            r1.font.size = Pt(11)
        else:
            r1.bold = True
        r_dots = p_t.add_run(" " + "." * (75 - len(item) * 2) + " ")
        r_dots.font.color.rgb = RGBColor(203, 213, 225)
        r2 = p_t.add_run(page)
        r2.italic = True
        r2.font.size = Pt(10.5)

    doc.add_page_break()

    # ==================== 1. GIỚI THIỆU ỨNG DỤNG ====================
    add_h1("1. GIỚI THIỆU ỨNG DỤNG")
    add_p("VietJourney AI là hệ thống quản lý tour du lịch có tích hợp trí tuệ nhân tạo (Google Gemini AI), hỗ trợ giới thiệu tour, tiếp nhận yêu cầu tư vấn, quản lý lịch khởi hành, đặt chỗ, thanh toán, hướng dẫn viên và phản hồi khách hàng. Tài liệu hướng dẫn thao tác trên phiên bản mã nguồn hiện tại, dành cho khách vãng lai và các bộ phận nhân sự vận hành hệ thống.")
    add_p("Quy trình tổng quát của hệ thống: Khách chọn tour và gửi yêu cầu → Tư vấn viên liên hệ, duyệt và giữ chỗ (trừ số ghế khả dụng) → Kế toán đối soát và ghi nhận tiền cọc/toàn bộ → Quản trị viên điều hành đợt khởi hành → Theo dõi đánh giá phản hồi và báo cáo doanh thu. Khách gửi yêu cầu ban đầu chỉ ở trạng thái chờ duyệt (WAITING_CONFIRM), chưa được xem là đã giữ chỗ hoặc đã thanh toán.")
    add_p("Phân quyền người dùng: Khách vãng lai không cần tài khoản để xem tour, tra cứu hướng dẫn viên, sử dụng trợ lý AI tư vấn và gửi biểu mẫu yêu cầu. Ba vai trò đăng nhập quản trị nội bộ gồm Quản trị viên (ADMIN), Nhân viên tư vấn (CONSULTANT) và Kế toán (ACCOUNTANT). Hướng dẫn viên được quản lý dưới dạng hồ sơ nhân sự phục vụ phân công chuyến đi.")
    add_p("Địa chỉ chạy mặc định trên máy chủ nội bộ: http://127.0.0.1:8000. Mọi hình ảnh minh họa trong tài liệu được trích xuất trực tiếp từ giao diện vận hành thực tế.")

    add_img("docs/media/user_guide_01.png", "Hình 1. Trang chủ VietJourney AI trong môi trường thực tế")

    # ==================== 2. CẤU HÌNH PHẦN CỨNG - PHẦN MỀM ====================
    add_h1("2. CẤU HÌNH PHẦN CỨNG - PHẦN MỀM")

    add_h2("2.1 Phần cứng")
    add_p("Cấu hình đề xuất cho việc học tập, kiểm thử và trình diễn ứng dụng:")

    # Table Hardware
    t_hw = doc.add_table(rows=1, cols=3)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = t_hw.rows[0].cells
    hdr_cells[0].text = "Thành phần"
    hdr_cells[1].text = "Cấu hình tối thiểu"
    hdr_cells[2].text = "Cấu hình khuyến nghị"
    for c in hdr_cells:
        set_cell_background(c, "E0F2FE")
        set_cell_margins(c)
        c.paragraphs[0].runs[0].bold = True

    hw_rows = [
        ("Bộ vi xử lý (CPU)", "Intel Core i3 / AMD Ryzen 3 (2 nhân)", "Intel Core i5 / AMD Ryzen 5 trở lên"),
        ("Bộ nhớ RAM", "4 GB", "8 GB trở lên"),
        ("Dung lượng ổ cứng", "Trống tối thiểu 2 GB", "Ổ cứng SSD trống 5 GB trở lên"),
        ("Màn hình hiển thị", "Độ phân giải 1366 × 768", "Độ phân giải 1920 × 1080 (Full HD)"),
        ("Kết nối Internet", "Băng thông 5 Mbps (gọi Gemini AI)", "Băng thông ổn định từ 20 Mbps")
    ]
    for comp, min_c, rec_c in hw_rows:
        row = t_hw.add_row().cells
        row[0].text = comp
        row[1].text = min_c
        row[2].text = rec_c
        for cell in row:
            set_cell_margins(cell)
            set_cell_background(cell, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_h2("2.2 Phần mềm")
    add_p("Môi trường sử dụng: Hệ điều hành Windows 10/11, Linux (Ubuntu/Debian) hoặc macOS; Python phiên bản 3.10 trở lên; Trình duyệt web hỗ trợ chuẩn hiện đại như Google Chrome hoặc Microsoft Edge. Hệ thống backend phát triển bằng FastAPI và SQLAlchemy; cơ sở dữ liệu mặc định dùng SQLite (hoặc MySQL Server 8.0+ khi triển khai quy mô lớn). Giao diện frontend thuần HTML/Tailwind/JS đã được đóng gói tĩnh, không yêu cầu cài đặt môi trường Node.js trên máy người dùng.")

    add_h3("Các bước cài đặt và khởi chạy lần đầu:")
    add_p("Bước 1. Mở thư mục dự án tourdulichAI, mở cửa sổ PowerShell tại thư mục đó. Tạo môi trường Python: py -m venv .venv")
    add_p("Bước 2. Cài đặt các thư viện cần thiết: .venv\\Scripts\\python.exe -m pip install -r requirements-lock.txt")
    add_p("Bước 3. Kiểm tra file cấu hình .env (sao chép từ .env.example nếu cần); không đưa mật khẩu cá nhân hay khóa API vào tài liệu chia sẻ.")
    add_p("Bước 4. Khởi tạo cơ sở dữ liệu mẫu bằng lệnh: .venv\\Scripts\\python.exe scripts\\setup_database.py --demo")
    add_p("Bước 5. Khởi động ứng dụng bằng file start.bat (hoặc gõ lệnh uvicorn backend.app.main:app --reload). Khi cửa sổ thông báo Application startup complete, mở trình duyệt truy cập: http://127.0.0.1:8000")
    add_p("Bước 6. Để dừng máy chủ, quay lại cửa sổ dòng lệnh và bấm tổ hợp phím Ctrl + C.")

    add_h3("Bảng tài khoản thử nghiệm (Demo Accounts):")
    t_acc = doc.add_table(rows=1, cols=4)
    t_acc.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_acc = t_acc.rows[0].cells
    h_acc[0].text = "Vai trò (Role)"
    h_acc[1].text = "Tên đăng nhập"
    h_acc[2].text = "Mật khẩu"
    h_acc[3].text = "Phân hệ nghiệp vụ truy cập"
    for c in h_acc:
        set_cell_background(c, "E0F2FE")
        set_cell_margins(c)
        c.paragraphs[0].runs[0].bold = True

    acc_rows = [
        ("Quản trị viên (ADMIN)", "admin", "admin123", "Toàn quyền: Tour, Lịch đi, HDV, Tài khoản, AI Hub, Báo cáo"),
        ("Nhân viên tư vấn (CONSULTANT)", "tuvan", "tuvan123", "Hàng chờ tư vấn, Quản lý đặt chỗ, Tra cứu khách hàng"),
        ("Kế toán (ACCOUNTANT)", "ketoan", "ketoan123", "Kế toán & Thu tiền, Phiếu thanh toán, Báo cáo doanh thu")
    ]
    for r, u, p, note in acc_rows:
        row = t_acc.add_row().cells
        row[0].text = r
        row[1].text = u
        row[2].text = p
        row[3].text = note
        for cell in row:
            set_cell_margins(cell)
            set_cell_background(cell, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_img("docs/media/user_guide_02.png", "Hình 2. Màn hình đăng nhập hệ thống và thông tin phân quyền")

    # ==================== 3. CÁC CHỨC NĂNG CHÍNH ====================
    add_h1("3. CÁC CHỨC NĂNG CHÍNH")
    add_p("Các chức năng của hệ thống VietJourney AI được phân định rành mạch theo 4 nhóm tác nhân (Actors) đã được quy định trong tài liệu Đặc tả yêu cầu phần mềm (SRS V1.0): Khách vãng lai, Quản trị viên (Admin), Nhân viên tư vấn (Consultant) và Kế toán (Accountant).")

    # 3.1 Khách vãng lai
    add_h2("3.1 Chức năng của Khách vãng lai (Guest)")
    add_p("Khách vãng lai là người dùng truy cập công khai vào hệ thống để tra cứu tour, hỏi đáp trợ lý ảo và đăng ký nhu cầu du lịch mà không cần tài khoản.")

    add_h3("Tra cứu danh mục tour & Lịch khởi hành:")
    add_p("Bước 1. Mở trang chủ (tours.html). Duyệt danh sách các tour du lịch hiện có, tìm kiếm theo tên, lọc theo danh mục (Biển đảo, Tây Bắc, Di sản, Miền Tây).")
    add_p("Bước 2. Bấm 'Xem chi tiết' để xem hành trình từng ngày, điểm nhấn nổi bật, thời lượng và bảng giá niêm yết.")
    add_p("Bước 3. Đối chiếu danh sách các đợt khởi hành còn mở bán, ngày đi, ngày về và số lượng chỗ còn trống.")

    add_h3("Tư vấn tour thông minh qua Trợ lý AI Gemini:")
    add_p("Bước 1. Bấm vào biểu tượng 'Trợ lý AI Gemini' ở góc dưới bên phải màn hình để mở Drawer hội thoại.")
    add_p("Bước 2. Nhập nhu cầu du lịch bằng ngôn ngữ tự nhiên (Ví dụ: 'Tôi muốn đi Đà Lạt 3 ngày 2 đêm, ngân sách khoảng 3 triệu đồng cho 2 người').")
    add_p("Bước 3. AI Gemini sử dụng kỹ thuật RAG, đối chiếu trực tiếp dữ liệu tour còn chỗ trong cơ sở dữ liệu để đưa ra phản hồi chính xác kèm lịch trình gợi ý.")

    add_h3("Gửi biểu mẫu yêu cầu đặt tour:")
    add_p("Bước 1. Tại đợt khởi hành mong muốn, khách bấm nút 'Đặt tour'.")
    add_p("Bước 2. Điền họ tên, số điện thoại, địa chỉ email, số lượng người tham gia và ghi chú đặc biệt (ăn chay, có người cao tuổi...).")
    add_p("Bước 3. Bấm 'Gửi yêu cầu' và lưu lại mã định danh (REQ-...) để nhân viên hỗ trợ đối soát.")
    add_callout("Đơn gửi từ khách hàng mang trạng thái WAITING_CONFIRM (Chờ tư vấn xác nhận). Hệ thống TUYỆT ĐỐI CHƯA TRỪ CHỖ KHẢ DỤNG và chưa thu bất kỳ khoản tiền nào cho tới khi nhân viên tư vấn liên hệ và bấm duyệt.", "Lưu ý khách hàng: ")

    add_img("docs/media/user_guide_03.png", "Hình 3. Biểu mẫu gửi yêu cầu tư vấn tour của khách vãng lai")

    # 3.2 Quản trị viên
    add_h2("3.2 Chức năng của Quản trị viên (Admin)")
    add_p("Quản trị viên nắm quyền kiểm soát toàn diện danh mục sản phẩm, lịch trình, nhân sự điều hành và trí tuệ nhân tạo.")

    add_h3("Quản lý danh mục Tour & Tích hợp AI viết mô tả:")
    add_p("Bước 1. Truy cập menu 'Quản Lý Tour' (/tours_admin.html) để xem danh sách toàn bộ sản phẩm.")
    add_p("Bước 2. Bấm '+ Thêm tour mới' và nhập các thông tin: Mã tour duy nhất (code), Tên tour, Danh mục, Điểm đến, Thời lượng (ngày/đêm), Giá gốc.")
    add_p("Bước 3. Tích hợp AI: Bấm nút 'AI Viết mô tả tour' -> Gemini AI tự động sinh đoạn văn giới thiệu chi tiết, hấp dẫn và tự động điền vào khung nội dung lịch trình.")
    add_p("Bước 4. Admin duyệt lại nội dung, chỉnh sửa theo thực tế rồi bấm 'Lưu Tour'.")
    add_p("Bước 5. Xóa tour: Hệ thống tự động chặn thao tác xóa nếu tour đã phát sinh lịch khởi hành hoặc đơn booking nhằm bảo vệ tính toàn vẹn dữ liệu.")

    add_img("docs/media/user_guide_04.png", "Hình 4. Màn hình quản lý danh mục tour và kích hoạt AI sinh mô tả")

    add_h3("Quản lý Lịch khởi hành & Vòng đời chuyến đi:")
    add_p("Bước 1. Vào menu 'Lịch Khởi Hành & Chỗ' (/departures.html) -> Bấm '+ Mở đợt khởi hành mới'.")
    add_p("Bước 2. Chọn Tour gốc, Ngày xuất phát, Ngày kết thúc, Tổng số chỗ mở bán (total_slots), và phân công Hướng dẫn viên.")
    add_p("Bước 3. Hệ thống tự động xác thực: Ngày kết thúc phải sau ngày xuất phát; Hướng dẫn viên không bị trùng lịch dẫn tour khác. Sau khi lưu, trạng thái là OPEN và available_slots = total_slots.")
    add_p("Bước 4. Điều hành vòng đời: Khi đoàn lên đường, Admin bấm 'Bắt đầu' -> Trạng thái chuyến chuyển sang RUNNING, đồng thời HDV tự động chuyển sang ON_TOUR. Khi về an toàn, Admin bấm 'Hoàn tất' -> Trạng thái chuyến chuyển sang COMPLETED, HDV trở về AVAILABLE.")

    add_img("docs/media/user_guide_05.png", "Hình 5. Quản lý lịch khởi hành, số chỗ ngồi và phân công hướng dẫn viên")

    add_h3("Quản lý hồ sơ Hướng dẫn viên (Tour Guides):")
    add_p("Bước 1. Mở menu 'Hướng Dẫn Viên' (/guides.html) để theo dõi danh sách đội ngũ điều hành dẫn tour.")
    add_p("Bước 2. Thêm mới hoặc chỉnh sửa hồ sơ: Họ tên, Số điện thoại, Email, Ngôn ngữ giao tiếp, Số năm kinh nghiệm và trạng thái làm việc.")
    add_p("Bước 3. Theo dõi trạng thái: AVAILABLE (Sẵn sàng), ON_TOUR (Đang dẫn tour), OFF (Nghỉ phép). Hệ thống cảnh báo khi xóa HDV đang có lịch phân công sắp diễn ra.")

    add_img("docs/media/user_guide_06.png", "Hình 6. Danh sách hồ sơ hướng dẫn viên và trạng thái điều hành")

    add_h3("Quản lý Tài khoản & Phân quyền bảo mật (RBAC):")
    add_p("Bước 1. Vào menu 'Quản Lý Tài Khoản' (/users.html) -> Bấm '+ Thêm tài khoản'.")
    add_p("Bước 2. Nhập tên đăng nhập duy nhất, họ tên, mật khẩu khởi tạo và chọn một trong 3 vai trò: ADMIN, CONSULTANT hoặc ACCOUNTANT.")
    add_p("Bước 3. Khóa hoặc mở lại tài khoản nhân viên. Hệ thống tự động bảo vệ tài khoản Quản trị viên hoạt động cuối cùng.")

    add_img("docs/media/user_guide_07.png", "Hình 7. Quản lý tài khoản nhân viên và phân quyền vai trò RBAC")

    add_h3("AI Hub - Phân tích cảm xúc & Tóm tắt phản hồi du khách:")
    add_p("Bước 1. Vào menu 'AI Hub & Phản Hồi' (/ai_hub.html).")
    add_p("Bước 2. Chọn một Tour cụ thể -> Nhấn nút 'Bắt Đầu Phân Tích & Tóm Tắt AI'.")
    add_p("Bước 3. AI Gemini phân tích toàn bộ văn bản review của du khách, trích xuất 4 khối báo cáo trực quan: Chỉ số cảm xúc (Sentiment tích cực/tiêu cực/trung lập), Điểm khen ngợi, Điểm cần khắc phục, Đánh giá HDV và Đề xuất cải tiến.")

    add_img("docs/media/user_guide_08.png", "Hình 8. AI Hub phân tích cảm xúc và tóm tắt phản hồi khách hàng")

    # 3.3 Nhân viên tư vấn
    add_h2("3.3 Chức năng của Nhân viên tư vấn (Consultant)")
    add_p("Nhân viên tư vấn chịu trách nhiệm tiếp nhận khách hàng, giải quyết hàng chờ tư vấn, xác nhận giữ chỗ và chăm sóc khách.")
    add_callout("Nhân viên tư vấn KHÔNG ĐƯỢC PHÉP THU TIỀN trên hệ thống. Sau khi giữ chỗ thành công, tư vấn viên bàn giao mã booking cho Kế toán để thực hiện các thủ tục thu tiền và xuất phiếu thu.", "Quy tắc nghiệp vụ: ")

    add_h3("Tiếp nhận & Xử lý hàng chờ tư vấn:")
    add_p("Bước 1. Mở menu 'Hàng Chờ Tư Vấn' (/consultations.html).")
    add_p("Bước 2. Tìm yêu cầu của khách (mang trạng thái WAITING_CONFIRM), bấm liên hệ khách hàng qua điện thoại để xác nhận thông tin.")
    add_p("Bước 3. Xử lý yêu cầu:")
    add_p("   - Nếu khách đồng ý: Bấm nút 'Xác Nhận Giữ Chỗ' -> Hệ thống kích hoạt khóa bi quan (Pessimistic Locking), kiểm tra số chỗ trống -> Trừ số chỗ khả dụng (available_slots -= num_people) -> Chuyển đơn sang trạng thái chính thức PENDING (Chờ thanh toán).")
    add_p("   - Nếu khách đổi ý: Bấm 'Từ chối' và nhập lý do -> Đơn chuyển sang CANCELLED (không ảnh hưởng số chỗ của chuyến).")

    add_img("docs/media/user_guide_09.png", "Hình 9. Hàng chờ tiếp nhận và duyệt yêu cầu giữ chỗ")

    add_h3("Quản lý Đặt chỗ (Bookings) & Khách hàng:")
    add_p("Bước 1. Vào menu 'Quản Lý Đặt Chỗ' (/bookings.html).")
    add_p("Bước 2. Theo dõi trạng thái đơn hàng: PENDING (Chờ thanh toán cọc), DEPOSITED (Đã cọc >= 30%), CONFIRMED (Đã thanh toán đủ 100%), CANCELLED (Đã hủy).")
    add_p("Bước 3. Đặt chỗ trực tiếp tại quầy: Chọn tour, chọn lịch khởi hành còn mở, nhập thông tin khách hàng và bấm 'Tạo Đặt Chỗ' để giữ ghế ngay.")

    add_img("docs/media/user_guide_10.png", "Hình 10. Danh sách đơn đặt chỗ và tiến trình xử lý công nợ")

    add_h3("Hủy đặt chỗ & Hoàn trả số chỗ trống:")
    add_p("Bước 1. Khi khách yêu cầu hủy chuyến đã giữ chỗ, tư vấn viên tìm đúng mã booking.")
    add_p("Bước 2. Bấm nút 'Hủy đơn' -> Điền lý do khách hủy.")
    add_p("Bước 3. Hệ thống đổi trạng thái sang CANCELLED và TỰ ĐỘNG CỘNG HOÀN TRẢ LẠI SỐ GHẾ vào đợt khởi hành tương ứng (available_slots += num_people).")

    add_img("docs/media/user_guide_11.png", "Hình 11. Tra cứu và theo dõi phản hồi đánh giá của khách hàng")

    # 3.4 Kế toán
    add_h2("3.4 Chức năng của Kế toán (Accountant)")
    add_p("Kế toán chịu trách nhiệm độc quyền đối với các giao dịch tài chính, thu tiền, đối soát công nợ, xử lý hoàn tiền và báo cáo doanh thu.")

    add_h3("Ghi nhận thu tiền & Quản lý phiếu thanh toán:")
    add_p("Bước 1. Mở menu 'Kế Toán & Thu Tiền' (/payments.html) hoặc bấm nút 'Thu tiền' từ danh sách đơn đặt chỗ.")
    add_p("Bước 2. Đối chiếu số tiền phải thu và số tiền còn nợ của đơn booking.")
    add_p("Bước 3. Nhập số tiền thu thực tế (VNĐ), chọn hình thức (Chuyển khoản, Tiền mặt) và phân loại thu (Đặt cọc, Thanh toán đợt cuối, Toàn bộ).")
    add_p("Bước 4. Nhấn 'Xác Nhận Thu Tiền': Hệ thống tự động sinh mã giao dịch (PAY-...), cộng dồn số tiền đã đóng và tự động đổi trạng thái đơn sang DEPOSITED (nếu đạt >= 30%) hoặc CONFIRMED (nếu đóng đủ 100%).")

    add_img("docs/media/user_guide_12.png", "Hình 12. Giao diện ghi nhận thanh toán và lập phiếu thu")

    add_h3("Xử lý hoàn tiền khi hủy tour (Refunds):")
    add_p("Khi khách hủy chuyến trước ngày khởi hành, hệ thống áp dụng bảng tỷ lệ hoàn tiền tự động:")

    # Table Refund Policy
    t_rf = doc.add_table(rows=1, cols=3)
    t_rf.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_rf = t_rf.rows[0].cells
    h_rf[0].text = "Thời điểm thông báo hủy tour"
    h_rf[1].text = "Tỷ lệ hoàn tiền"
    h_rf[2].text = "Quy định áp dụng"
    for c in h_rf:
        set_cell_background(c, "E0F2FE")
        set_cell_margins(c)
        c.paragraphs[0].runs[0].bold = True

    rf_rows = [
        ("Trước ngày khởi hành từ 15 ngày trở lên", "Hoàn 100%", "Hoàn lại toàn bộ số tiền khách đã đóng"),
        ("Từ 7 ngày đến dưới 15 ngày", "Hoàn 70%", "Khấu trừ 30% chi phí đặt cọc dịch vụ"),
        ("Từ 3 ngày đến dưới 7 ngày", "Hoàn 50%", "Khấu trừ 50% chi phí chuẩn bị chuyến đi"),
        ("Dưới 3 ngày hoặc sau khi tour đã khởi hành", "Hoàn 0%", "Không hoàn lại tiền theo hợp đồng lữ hành")
    ]
    for d, pct, rule in rf_rows:
        row = t_rf.add_row().cells
        row[0].text = d
        row[1].text = pct
        row[2].text = rule
        for cell in row:
            set_cell_margins(cell)
            set_cell_background(cell, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_p("Kế toán xác nhận lập phiếu chi hoàn tiền (REFUND) và thực hiện chuyển khoản hoàn trả thực tế cho khách.")

    add_h3("Báo cáo thống kê doanh thu & Tỷ lệ lấp đầy:")
    add_p("Bước 1. Truy cập menu 'Thống Kê Doanh Thu' (/stats.html).")
    add_p("Bước 2. Theo dõi các chỉ số tài chính tổng hợp: Tổng thực thu (Doanh thu đã thu trừ tiền hoàn), Doanh thu dự kiến từ các đơn đã giữ chỗ.")
    add_p("Bước 3. Biểu đồ cột 'Top Tour Đóng Góp Doanh Thu Cao Nhất': Rê chuột vào đỉnh cột để xem chi tiết doanh thu từng tuyến tour.")
    add_p("Bước 4. Biểu đồ tròn 'Tỷ Lệ Lấp Đầy Chỗ Ngồi': Thể hiện tỷ lệ phần trăm giữa số ghế đã đặt và số ghế còn trống trên toàn hệ thống.")

    add_img("docs/media/user_guide_13.png", "Hình 13. Màn hình thống kê doanh thu và phân tích tỷ lệ lấp đầy chỗ ngồi")

    # ==================== 4. XỬ LÝ SỰ CỐ & LƯU Ý ====================
    add_h1("4. XỬ LÝ SỰ CỐ VÀ LƯU Ý SỬ DỤNG")

    # Table Troubleshooting
    t_err = doc.add_table(rows=1, cols=3)
    t_err.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_err = t_err.rows[0].cells
    h_err[0].text = "Hiện tượng sự cố"
    h_err[1].text = "Nguyên nhân"
    h_err[2].text = "Hướng dẫn khắc phục"
    for c in h_err:
        set_cell_background(c, "E0F2FE")
        set_cell_margins(c)
        c.paragraphs[0].runs[0].bold = True

    err_rows = [
        ("Không mở được địa chỉ 127.0.0.1:8000", "Chưa bật máy chủ Uvicorn hoặc cửa sổ start.bat bị đóng", "Mở PowerShell, kích hoạt .venv và chạy lệnh: uvicorn backend.app.main:app --reload"),
        ("Đăng nhập thất bại: Sai tài khoản/mật khẩu", "Gõ sai thông tin hoặc tài khoản đang bị khóa (is_active=False)", "Kiểm tra CapsLock; dùng tài khoản demo (admin/admin123, tuvan/tuvan123, ketoan/ketoan123)"),
        ("Không thấy nút 'Thu tiền'", "Đang đăng nhập bằng tài khoản Tư vấn viên (CONSULTANT)", "Tư vấn viên không có quyền thu tiền. Cần đăng nhập tài khoản Kế toán hoặc Admin"),
        ("Báo lỗi 'Không đủ số chỗ trống'", "Đợt khởi hành đã hết chỗ hoặc có nhân viên khác vừa duyệt trước", "Kiểm tra số chỗ khả dụng (available_slots). Đề xuất khách chuyển sang ngày đi khác"),
        ("AI không phản hồi hoặc báo lỗi", "Máy tính mất kết nối Internet hoặc chưa cấu hình Gemini API Key", "Kiểm tra mạng Internet; Admin vào AI Hub kiểm tra trạng thái Google Gemini API Key")
    ]
    for issue, cause, fix in err_rows:
        row = t_err.add_row().cells
        row[0].text = issue
        row[1].text = cause
        row[2].text = fix
        for cell in row:
            set_cell_margins(cell)
            set_cell_background(cell, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    add_h2("Lưu ý vận hành an toàn:")
    add_p("1. Đăng xuất an toàn: Luôn bấm nút 'Đăng xuất' sau khi kết thúc ca làm việc trên máy tính chung tại văn phòng.")
    add_p("2. Thu tiền minh bạch: Mọi khoản thanh toán phải được lập phiếu trên phần mềm để hệ thống tự động đổi trạng thái đơn sang DEPOSITED hoặc CONFIRMED.")
    add_p("3. Sao lưu cơ sở dữ liệu định kỳ: Định kỳ sao chép tệp tour_management.db trước khi nâng cấp phiên bản để bảo vệ an toàn dữ liệu khách hàng.")

    # Save document
    doc.save(output_path)
    print(f"✓ Đã tạo thành công tệp Word: {output_path}")

if __name__ == "__main__":
    out_file1 = os.path.abspath("docs/07_GenAI_SoftwareDevelopment_user-guide.docx")
    out_file2 = os.path.abspath("docs/TAI_LIEU_HUONG_DAN_SU_DUNG_V1.0.docx")
    create_user_guide_docx(out_file1)
    create_user_guide_docx(out_file2)
    print("HOÀN TẤT TẠO 2 TỆP DOCX!")
