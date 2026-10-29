import os
import sys
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

drawio_file = os.path.abspath("docs/diagrams/vietjourney_all_diagrams.drawio")
with open(drawio_file, "r", encoding="utf-8") as f:
    xml_content = f.read()

# Escape for JS template string
xml_json = json.dumps(xml_content)

diagrams_list = [
    {"id": "01", "name": "01_So_do_Use_Case_Tong_quat", "title": "01. Sơ đồ Use Case tổng quát", "cat": "Kiến trúc tổng quan", "type": "Use Case Diagram"},
    {"id": "02", "name": "02_Phan_cap_chuc_nang", "title": "02. Sơ đồ phân cấp chức năng", "cat": "Kiến trúc tổng quan", "type": "Decomposition Diagram"},
    {"id": "03", "name": "03_So_do_Lop_Class_Diagram", "title": "03. Sơ đồ Lớp (UML Class Diagram)", "cat": "Kiến trúc tổng quan", "type": "Class Diagram"},
    {"id": "04", "name": "04_So_do_CSDL_ERD_10_Bang", "title": "04. Sơ đồ CSDL ERD (10 Bảng chuẩn 3NF)", "cat": "Kiến trúc tổng quan", "type": "Entity Relationship"},
    {"id": "05", "name": "05_So_do_Luong_man_hinh_Screen_Flow", "title": "05. Sơ đồ Luồng màn hình (Screen Flow)", "cat": "Kiến trúc tổng quan", "type": "Screen Flow"},
    
    {"id": "06", "name": "06_UC001_Dang_nhap_Activity", "title": "06. UC001: Đăng nhập & Xác thực RBAC", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "07", "name": "07_UC001_Dang_nhap_Sequence", "title": "07. UC001: Đăng nhập & Cấp JWT Token", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "08", "name": "08_UC002_Quan_ly_Tour_AI_Activity", "title": "08. UC002: Quản lý Tour & AI sinh mô tả", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "09", "name": "09_UC002_Quan_ly_Tour_AI_Sequence", "title": "09. UC002: Quản lý Tour & AI sinh mô tả", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "10", "name": "10_UC003_Lich_khoi_hanh_Activity", "title": "10. UC003: Quản lý Lịch khởi hành & HDV", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "11", "name": "11_UC003_Lich_khoi_hanh_Sequence", "title": "11. UC003: Quản lý Lịch khởi hành & HDV", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "12", "name": "12_UC004_Dat_cho_Idempotency_Activity", "title": "12. UC004: Khách hàng & Đặt chỗ (Khóa ghế)", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "13", "name": "13_UC004_Dat_cho_Idempotency_Sequence", "title": "13. UC004: Khách hàng & Đặt chỗ (Idempotency)", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "14", "name": "14_UC005_Thanh_toan_Dat_coc_Activity", "title": "14. UC005: Quản lý Thanh toán & Đặt cọc", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "15", "name": "15_UC005_Thanh_toan_Dat_coc_Sequence", "title": "15. UC005: Ghi nhận Thanh toán & Dòng tiền", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "16", "name": "16_UC006_Phan_hoi_AI_Summary_Activity", "title": "16. UC006: Quản lý Phản hồi & AI Sentiment", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "17", "name": "17_UC006_Phan_hoi_AI_Summary_Sequence", "title": "17. UC006: AI Phân tích & Tóm tắt phản hồi", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "18", "name": "18_UC007_Huong_dan_vien_Activity", "title": "18. UC007: Quản lý Hướng dẫn viên", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "19", "name": "19_UC007_Huong_dan_vien_Sequence", "title": "19. UC007: Quản lý Hướng dẫn viên", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
    
    {"id": "20", "name": "20_UC008_Thong_ke_Bao_cao_Activity", "title": "20. UC008: Thống kê Doanh thu & Lấp đầy", "cat": "Biểu đồ Hoạt Động (Activity)", "type": "Activity Diagram"},
    {"id": "21", "name": "21_UC008_Thong_ke_Bao_cao_Sequence", "title": "21. UC008: Truy vấn số liệu & Vẽ biểu đồ", "cat": "Biểu đồ Tuần Tự (Sequence)", "type": "Sequence Diagram"},
]

diag_cards_html = ""
for d in diagrams_list:
    diag_cards_html += f"""
    <div class="card" data-cat="{d['cat']}">
      <div class="card-header">
        <span class="card-badge">{d['type']}</span>
        <span class="card-id">#{d['id']}</span>
      </div>
      <div class="card-body">
        <a href="/diagrams/{d['name']}.png" target="_blank" title="Bấm để xem ảnh phóng to">
          <img src="/diagrams/{d['name']}.png" alt="{d['title']}" loading="lazy" />
        </a>
      </div>
      <div class="card-footer">
        <div class="card-title">{d['title']}</div>
        <div class="card-actions">
          <a href="/diagrams/{d['name']}.png" download="{d['name']}.png" class="btn-sm btn-download">
            <i class="fa-solid fa-download"></i> Tải ảnh PNG
          </a>
          <button onclick="copyImagePath('/diagrams/{d['name']}.png')" class="btn-sm btn-copy">
            <i class="fa-regular fa-copy"></i> Copy Link
          </button>
        </div>
      </div>
    </div>
    """

html_page = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VietJourney AI - Hệ Thống Sơ Đồ Thiết Kế UML (Draw.io Multi-page Studio)</title>
  <link rel="stylesheet" href="/static/vendor/css/all.min.css">
  <style>
    * {{ box-sizing: border-box; }}
    body, html {{
      margin: 0; padding: 0; height: 100%; overflow: hidden;
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
      background: #0f172a; color: #f8fafc;
    }}
    #app-container {{
      display: flex; flex-direction: column; height: 100vh;
    }}
    /* Top Bar */
    #top-bar {{
      height: 60px; background: #1e293b; border-bottom: 1.5px solid #334155;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 20px; z-index: 100;
    }}
    .brand {{
      display: flex; align-items: center; gap: 12px;
    }}
    .brand-icon {{
      width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(135deg, #0284c7, #38bdf8);
      display: flex; align-items: center; justify-content: center; font-size: 18px; color: white;
    }}
    .brand-text h1 {{
      margin: 0; font-size: 16px; font-weight: 800; color: #f8fafc; letter-spacing: 0.5px;
    }}
    .brand-text span {{
      font-size: 11.5px; color: #94a3b8; font-weight: 500;
    }}
    .nav-tabs {{
      display: flex; background: #0f172a; padding: 4px; border-radius: 8px; border: 1px solid #334155;
    }}
    .nav-tab {{
      background: transparent; border: none; color: #94a3b8; padding: 8px 18px;
      border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
      display: flex; align-items: center; gap: 8px;
    }}
    .nav-tab.active {{
      background: #0284c7; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .top-actions {{
      display: flex; align-items: center; gap: 10px;
    }}
    .btn {{
      display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
      border-radius: 6px; font-size: 13px; font-weight: 600; text-decoration: none;
      border: none; cursor: pointer; transition: all 0.2s;
    }}
    .btn-primary {{
      background: #0284c7; color: white;
    }}
    .btn-primary:hover {{ background: #0369a1; }}
    .btn-success {{
      background: #10b981; color: white;
    }}
    .btn-success:hover {{ background: #059669; }}
    .btn-outline {{
      background: transparent; border: 1px solid #475569; color: #cbd5e1;
    }}
    .btn-outline:hover {{ background: #334155; color: white; }}

    /* Content Area */
    #content-area {{
      flex: 1; position: relative; overflow: hidden;
    }}
    .view-panel {{
      position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: none;
    }}
    .view-panel.active {{
      display: block;
    }}

    /* Drawio iframe */
    #drawio-frame {{
      width: 100%; height: 100%; border: none;
    }}

    /* Gallery Panel */
    #gallery-panel {{
      overflow-y: auto; padding: 24px 30px 60px 30px; background: #0b1120;
    }}
    .gallery-header {{
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
      padding-bottom: 12px; border-bottom: 1px solid #1e293b;
    }}
    .filter-group {{
      display: flex; gap: 8px;
    }}
    .filter-btn {{
      background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 6px 14px;
      border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }}
    .filter-btn.active, .filter-btn:hover {{
      background: #0284c7; color: white; border-color: #0284c7;
    }}
    .gallery-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px;
    }}
    .card {{
      background: #1e293b; border: 1px solid #334155; border-radius: 12px; overflow: hidden;
      display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s;
    }}
    .card:hover {{
      transform: translateY(-3px); box-shadow: 0 10px 20px -5px rgba(0,0,0,0.4); border-color: #0284c7;
    }}
    .card-header {{
      padding: 10px 14px; background: #0f172a; display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid #334155;
    }}
    .card-badge {{
      background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;
    }}
    .card-id {{
      font-size: 12px; font-weight: bold; color: #64748b;
    }}
    .card-body {{
      padding: 12px; background: #ffffff; display: flex; align-items: center; justify-content: center; height: 220px;
      overflow: hidden;
    }}
    .card-body img {{
      max-width: 100%; max-height: 100%; object-fit: contain; cursor: zoom-in; transition: transform 0.3s;
    }}
    .card-body img:hover {{
      transform: scale(1.04);
    }}
    .card-footer {{
      padding: 12px 14px; background: #1e293b; display: flex; flex-direction: column; gap: 8px;
    }}
    .card-title {{
      font-size: 13px; font-weight: 700; color: #f8fafc; line-height: 1.4;
    }}
    .card-actions {{
      display: flex; gap: 8px;
    }}
    .btn-sm {{
      padding: 5px 10px; border-radius: 5px; font-size: 11.5px; font-weight: 600; cursor: pointer; text-decoration: none;
      display: inline-flex; align-items: center; gap: 4px; border: none;
    }}
    .btn-download {{
      background: #0284c7; color: white;
    }}
    .btn-download:hover {{ background: #0369a1; }}
    .btn-copy {{
      background: #334155; color: #cbd5e1;
    }}
    .btn-copy:hover {{ background: #475569; color: white; }}

    /* Toast */
    #toast {{
      position: fixed; bottom: 24px; right: 24px; background: #10b981; color: white;
      padding: 10px 18px; border-radius: 8px; font-size: 13px; font-weight: 600;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3); opacity: 0; pointer-events: none; transition: opacity 0.3s; z-index: 1000;
    }}
  </style>
</head>
<body>
  <div id="app-container">
    <!-- Top Navigation Bar -->
    <header id="top-bar">
      <div class="brand">
        <div class="brand-icon"><i class="fa-solid fa-diagram-project"></i></div>
        <div class="brand-text">
          <h1>VietJourney AI &bull; Draw.io UML Studio</h1>
          <span>21 Sơ đồ thiết kế chuẩn UML &bull; Mỗi sơ đồ 1 trang &bull; Đúng 100% CSDL & Codebase</span>
        </div>
      </div>

      <nav class="nav-tabs">
        <button class="nav-tab active" onclick="switchView('drawio')">
          <i class="fa-solid fa-pen-ruler"></i> Trình Soạn Thảo Draw.io
        </button>
        <button class="nav-tab" onclick="switchView('gallery')">
          <i class="fa-regular fa-images"></i> Bộ Sưu Tập 21 Ảnh PNG
        </button>
      </nav>

      <div class="top-actions">
        <a href="/diagrams/vietjourney_all_diagrams.drawio" download="vietjourney_all_diagrams.drawio" class="btn btn-primary" title="Tải file Draw.io Multi-page chứa cả 21 trang">
          <i class="fa-solid fa-file-arrow-down"></i> Tải File .drawio
        </a>
        <a href="/tours.html" class="btn btn-outline" title="Quay lại ứng dụng chính">
          <i class="fa-solid fa-house"></i> VietJourney App
        </a>
      </div>
    </header>

    <!-- Main Content Area -->
    <main id="content-area">
      <!-- 1. Draw.io Embedded Editor Panel -->
      <section id="drawio-panel" class="view-panel active">
        <iframe id="drawio-frame" src="https://embed.diagrams.net/?embed=1&ui=atlas&spin=1&proto=json&page=0"></iframe>
      </section>

      <!-- 2. Gallery 21 PNG Panel -->
      <section id="gallery-panel" class="view-panel">
        <div class="gallery-header">
          <div>
            <h2 style="margin:0 0 4px 0;font-size:18px;color:#38bdf8;">Bộ Sưu Tập 21 Ảnh Sơ Đồ Xuất Sẵn</h2>
            <p style="margin:0;font-size:12px;color:#94a3b8;">Đã được tạo sẵn bằng Google Chrome Headless &bull; Độ sắc nét chuẩn đồ án &bull; Dán trực tiếp vào file Word</p>
          </div>
          <div class="filter-group">
            <button class="filter-btn active" onclick="filterGallery('all', this)">Tất cả (21)</button>
            <button class="filter-btn" onclick="filterGallery('Kiến trúc tổng quan', this)">Kiến trúc (5)</button>
            <button class="filter-btn" onclick="filterGallery('Biểu đồ Hoạt Động (Activity)', this)">Activity (8)</button>
            <button class="filter-btn" onclick="filterGallery('Biểu đồ Tuần Tự (Sequence)', this)">Sequence (8)</button>
          </div>
        </div>

        <div class="gallery-grid">
          {diag_cards_html}
        </div>
      </section>
    </main>
  </div>

  <div id="toast">Đã copy đường dẫn ảnh!</div>

  <script>
    // Embedded Multi-page Draw.io XML
    const xmlData = {xml_json};
    const iframe = document.getElementById('drawio-frame');

    // Draw.io postMessage protocol
    window.addEventListener('message', function(evt) {{
      if (!evt.data) return;
      try {{
        const msg = (typeof evt.data === 'string') ? JSON.parse(evt.data) : evt.data;
        if (msg.event === 'init') {{
          console.log('Draw.io init event received -> Loading multi-page XML...');
          iframe.contentWindow.postMessage(JSON.stringify({{
            action: 'load',
            autosave: 1,
            xml: xmlData
          }}), '*');
        }} else if (msg.event === 'load') {{
          console.log('Draw.io loaded successfully with 21 pages!');
        }}
      }} catch (err) {{}}
    }});

    // Tab Switching
    function switchView(viewName) {{
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
      if (viewName === 'drawio') {{
        document.querySelectorAll('.nav-tab')[0].classList.add('active');
        document.getElementById('drawio-panel').classList.add('active');
      }} else {{
        document.querySelectorAll('.nav-tab')[1].classList.add('active');
        document.getElementById('gallery-panel').classList.add('active');
      }}
    }}

    // Filter Gallery
    function filterGallery(category, btn) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cards = document.querySelectorAll('.card');
      cards.forEach(c => {{
        if (category === 'all' || c.getAttribute('data-cat') === category) {{
          c.style.display = 'flex';
        }} else {{
          c.style.display = 'none';
        }}
      }});
    }}

    // Copy Image Path Helper
    function copyImagePath(url) {{
      const fullUrl = window.location.origin + url;
      navigator.clipboard.writeText(fullUrl).then(() => {{
        const toast = document.getElementById('toast');
        toast.style.opacity = '1';
        setTimeout(() => {{ toast.style.opacity = '0'; }}, 2500);
      }});
    }}
  </script>
</body>
</html>
"""

output_path = os.path.abspath("frontend/drawio_editor.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_page)

print(f"Thành công! Đã tạo trang web Draw.io Studio: {output_path}")
print(f"Kích thước file: {os.path.getsize(output_path):,} bytes")
