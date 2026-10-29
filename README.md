# VietJourney AI — hướng dẫn chạy và kiểm thử

Ứng dụng FastAPI/SQLAlchemy, giao diện HTML/JavaScript; hỗ trợ SQLite và MySQL.

Chi tiết thay đổi và kiểm chứng: [kết quả cải thiện](docs/KET_QUA_CAI_THIEN.md).

## Bản Đồ Hệ Thống & Tài Liệu Kỹ Thuật

- **Bộ Prompt Tái Tạo Hệ Thống Từ Đầu (AI Rebuild Prompts)**: [prompts/README.md](prompts/README.md)
- **Hệ Thống Kỹ Năng Tác Tử (Multi-Agent Skills)**: [skill/README.md](skill/README.md)
- **Kiến trúc hệ thống & Sơ đồ luồng**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Quy chuẩn Vibe Coding (Cursor Rules)**: [.cursorrules](.cursorrules)
- **Sổ tay Tác tử AI (Agent Instructions)**: [AGENT.md](AGENT.md)
- **Cổng tài liệu & Báo cáo đồ án**: [docs/README.md](docs/README.md)
- **Hướng dẫn Backend**: [backend/README.md](backend/README.md)
- **Hướng dẫn Frontend**: [frontend/README.md](frontend/README.md)
- **Danh mục Scripts tự động hóa**: [scripts/README.md](scripts/README.md)

## Khởi chạy Windows

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Nếu chưa có `.env`, tạo theo `.env.example`. Không ghi đè cấu hình đang sử dụng.

- Database có dữ liệu: khởi chạy `start.bat`, mở http://127.0.0.1:8000 sau khi server báo sẵn sàng. Swagger: http://127.0.0.1:8000/docs.
- Database mới, demo: `.venv\Scripts\python.exe scripts\setup_database.py --demo`.
- Database mới, sử dụng thực tế: `.venv\Scripts\python.exe scripts\setup_database.py --admin ten_quan_tri`, nhập mật khẩu riêng khi được hỏi.

Chỉ seed demo mới tạo `admin/admin123`, `tuvan/tuvan123`, `ketoan/ketoan123`. Không dùng mật khẩu demo trên môi trường thật. Startup chỉ tạo bảng còn thiếu, không tự seed hay đổi lịch khởi hành.

Chạy trực tiếp: `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`.

## Cấu hình triển khai

- `APP_ENV=production` yêu cầu SECRET_KEY ngẫu nhiên ít nhất 32 ký tự. Tạo bằng `.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"`.
- Development lưu khóa riêng ở `.jwt_secret`, giữ phiên qua reload. Không đưa `.env` hoặc `.jwt_secret` lên Git.
- MySQL: cấu hình `DB_TYPE`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, hoặc `DATABASE_URL`. Tạo database trước bằng tài khoản quản trị MySQL, dùng tài khoản ứng dụng có quyền phù hợp. Import app không tự tạo database.
- Thiết lập key/model AI trong môi trường hoặc qua giao diện Admin. Khi không có key, hệ thống dùng chức năng nội bộ.
- Khi công khai server: HTTPS/reverse proxy, secret và mật khẩu riêng, backup định kỳ; không dùng --reload. Frontend cùng origin với API; nếu tách domain cần cập nhật allowlist CORS trong main.py.

## Chuyển dữ liệu tiền cũ

Tiền được xử lý bằng Decimal/số nguyên VNĐ, làm tròn nửa lên. Database mới dùng DECIMAL(18,0).

```powershell
.venv\Scripts\python.exe scripts\migrate_money.py
```

Audit dừng nếu có tiền âm/lẻ để đối chiếu trước. SQLite có kiểu số động, không cần rebuild nếu dữ liệu hiện có là số nguyên VNĐ.

Với MySQL cũ, dừng ứng dụng, sao lưu database rồi chạy:

```powershell
.venv\Scripts\python.exe scripts\migrate_money.py --apply
```

Script tạo bảng backup trước khi chuyển cột tiền. DDL MySQL không rollback nguyên khối; giữ các bảng backup đến khi đối chiếu xong. Startup không tự thay kiểu cột cũ.

## Nghiệp vụ

- Khách gửi yêu cầu chưa giữ chỗ/chưa thu tiền. Admin/tư vấn viên duyệt mới trừ chỗ.
- Consultant không được khai đã thu tiền; kế toán/Admin ghi nhận thanh toán. Thu tiền phải dương và không vượt dư nợ.
- Tạo booking hỗ trợ `Idempotency-Key`; cùng key/cùng dữ liệu trả cùng booking, khác dữ liệu trả 409. Thu tiền chống lặp bằng `transaction_code` cho cùng booking.
- Cọc 30%; hủy trước ít nhất 15/7/3 ngày hoàn 100%/70%/50% tiền đã đóng; dưới 3 ngày không hoàn. Chỉ Admin/kế toán được ghi đè tỷ lệ.
- Không hoàn chỗ cho đơn chưa giữ chỗ; không xóa tour/chuyến đã có booking.
- Khởi hành/kết thúc yêu cầu các booking đã duyệt thanh toán đủ. Chỉ thao tác chuyên dụng được đổi trạng thái vòng đời; hoàn thành chuyến đồng bộ booking COMPLETED và chặn hủy theo chính sách trước chuyến.
- `total_revenue`: doanh thu dự kiến từ booking đã duyệt và chưa hủy. `total_collected`: tổng thu trừ tổng hoàn trong sổ giao dịch. Yêu cầu chưa duyệt không tính doanh thu dự kiến.
- AI chọn ID hợp lệ; giá/ngày/chỗ lấy từ chuyến gần nhất, không cộng ghế nhiều ngày thành một chuyến. Văn bản giá/ngày hiển thị được dựng từ database.

## Kiểm thử

```powershell
.venv\Scripts\python.exe -m pytest backend/tests -q
```

Tests dùng database và `.env` tạm. Có phân quyền, validation, rollback, gửi lặp, đặt/hủy đồng thời trên SQLite.

Kiểm thử trình duyệt:

```powershell
npm.cmd ci --prefix .tools
.tools\node_modules\.bin\playwright.cmd install chromium
.venv\Scripts\python.exe scripts\run_ui_test_server.py
# Terminal khác:
node scripts/ui_smoke.cjs
node scripts/ui_regressions.cjs
```

Server test cổng 8011 có dữ liệu tạm. Smoke kiểm tra modal, sanitizer, yêu cầu khách, đăng nhập, trang nghiệp vụ, draft AI và viewport nhỏ. Ảnh ở artifacts/. Không thay thế kiểm thử chấp nhận toàn bộ tổ hợp dữ liệu/thiết bị.

## Build frontend

CSS, icon, chart và sanitizer đã có trong frontend/vendor; chạy ứng dụng không cần npm/CDN. Ảnh bên ngoài có placeholder cục bộ.

```powershell
npm.cmd ci --prefix .tools
.venv\Scripts\python.exe scripts\package_frontend.py
.tools\node_modules\.bin\tailwindcss.cmd -i frontend/css/tailwind-input.css -o frontend/vendor/tailwind.css --minify
```

License giữ trong vendor. Template động dùng data-action và sanitizer; không chèn inline JavaScript vào HTML sinh từ dữ liệu.

## Giới hạn đã biết

Chưa kiểm thử MySQL và AI cloud với khóa thật trong phiên này; cần xác nhận trên môi trường triển khai. Bộ smoke không phải kiểm toán accessibility chuyên sâu. Còn cảnh báo deprecation từ TestClient/httpx và Browserslist của công cụ build, không gây lỗi kiểm tra hiện tại. Chưa triển khai lên server công khai.
