# Danh Mục Công Cụ & Kịch Bản Tự Động Hóa (Scripts Directory)

Thư mục `scripts/` chứa các kịch bản Python, Node.js (Playwright) và PowerShell phục vụ quá trình khởi tạo cơ sở dữ liệu, kiểm thử tự động, build tài liệu và đóng gói hệ thống.

---

## 1. Cơ Sở Dữ Liệu & Di Trú (Database & Migrations)

| Tập lệnh | Mô tả công việc | Cách sử dụng |
| :--- | :--- | :--- |
| **`setup_database.py`** | Khởi tạo bảng dữ liệu và seed tài khoản mặc định (demo hoặc production). | `.venv\Scripts\python.exe scripts/setup_database.py --demo` |
| **`migrate_money.py`** | Kiểm toán và chuyển đổi dữ liệu tiền tệ sang chuẩn số nguyên VNĐ / `Decimal(18,0)`. | `.venv\Scripts\python.exe scripts/migrate_money.py --apply` |
| **`init_mysql_db.py`** | Kiểm tra kết nối và tạo schema cho cơ sở dữ liệu MySQL khi triển khai production. | `.venv\Scripts\python.exe scripts/init_mysql_db.py` |
| **`migrate_sqlite_to_mysql.py`** | Chuyển đổi toàn bộ dữ liệu từ SQLite sang MySQL. | `.venv\Scripts\python.exe scripts/migrate_sqlite_to_mysql.py` |

---

## 2. Kiểm Thử Trình Duyệt & Giao Diện (UI Testing & QA)

| Tập lệnh | Mô tả công việc | Cách sử dụng |
| :--- | :--- | :--- |
| **`run_ui_test_server.py`** | Chạy máy chủ kiểm thử độc lập trên cổng `8011` với database mẫu. | `.venv\Scripts\python.exe scripts/run_ui_test_server.py` |
| **`ui_smoke.cjs`** | Bộ test Playwright kiểm tra các modal, form nhập liệu, đăng nhập và đặt tour. | `node scripts/ui_smoke.cjs` |
| **`ui_regressions.cjs`** | Kiểm tra hồi quy giao diện, responsive mobile và xử lý lỗi người dùng. | `node scripts/ui_regressions.cjs` |

---

## 3. Biên Tập Tài Liệu & Sơ Đồ Kiến Trúc (Build & Reporting)

| Tập lệnh | Mô tả công việc |
| :--- | :--- |
| **`build_combined_report.py`** | Biên dịch và xuất báo cáo tổng hợp đề tài hoàn chỉnh định dạng Word (`.docx`). |
| **`build_user_guide_docx.py`** | Tự động chèn ảnh chụp màn hình thực tế vào tài liệu Hướng dẫn sử dụng `TAI_LIEU_HUONG_DAN_SU_DUNG_V1.0.docx`. |
| **`diagram_renderers.py`** / **`drawio_builder.py`** | Sinh sơ đồ luồng dữ liệu, sơ đồ tuần tự và sơ đồ ERD cho báo cáo. |
| **`package_frontend.py`** | Tối ưu hóa và đóng gói các thư viện frontend (Tailwind, Chart.js, Lucide) cho môi trường offline. |
