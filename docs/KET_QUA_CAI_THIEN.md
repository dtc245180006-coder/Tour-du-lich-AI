# Kết quả cải thiện — 28/10/2026

## Phạm vi đã triển khai

| Nhóm | Kết quả |
|---|---|
| Môi trường | .venv, dependency lock, start.bat; cấu hình mẫu; seed/admin setup riêng; không tự seed hay tạo database MySQL khi import. |
| Xác thực | Bỏ API đổi vai trò công khai; RBAC booking/công cụ AI; /auth/me và xử lý 401; PBKDF2 salt riêng, nâng cấp hash cũ; secret development ổn định và production bắt buộc. |
| Bảo vệ dữ liệu | Chặn path traversal/whitelist trang; không trả booking gần đây công khai; khách không tự ghi đè thông tin khách cũ; chặn xóa tour/chuyến có lịch sử và vô hiệu hóa Admin cuối cùng. |
| Tính toàn vẹn | Transaction chung; SQLite BEGIN IMMEDIATE, MySQL khóa booking; UPDATE trừ chỗ có điều kiện; rollback; chống booking lặp bằng header/bảng key và thu tiền lặp qua mã giao dịch. |
| Nghiệp vụ | Sửa hủy/từ chối đơn; kiểm tra chuyến quá hạn/đóng; trạng thái chạy/kết thúc; giới hạn sức chứa theo chỗ đã giữ; số tiền/dư nợ/tỷ lệ hoàn; Decimal/VNĐ và công cụ audit/migrate có backup. |
| Báo cáo/AI | Không tính yêu cầu chưa duyệt vào doanh thu dự kiến; thực thu trừ hoàn; CSAT từ dữ liệu. Không tự dịch lịch; giá/ngày/chỗ theo chuyến gần nhất; cloud chỉ chọn ID và dữ liệu hiển thị từ DB; sửa đơn vị timeout SDK; giữ draft AI qua chuyển trang. |
| An toàn giao diện | DOMPurify cục bộ cho innerHTML; bỏ inline handler trong template động; data action không eval; toast textContent; chống gửi lặp; mã retry booking/payment. |
| UX | Modal mở lại/Escape/focus trap/return focus; giới hạn chiều cao; label/input và tên nút icon; validation trước submit; lỗi dễ đọc; loading/retry; mã đơn lưu/sao chép; router đa trang; sidebar mobile/desktop. |
| Hiển thị | CSS/icon/chart/sanitizer cục bộ; ảnh dự phòng; chữ chính lớn hơn, focus rõ, reduced motion; chính sách thu gọn, CTA ngắn; biểu đồ không tự tạo số mẫu. |

## Kiểm chứng

- 37/37 test backend đạt: bảo mật, validation, booking/payment, rollback, idempotency và đồng thời trên SQLite. JavaScript qua node --check.
- 6 yêu cầu vào chuyến 3 chỗ: chỉ 3 booking thành công. Hủy đồng thời không hoàn tiền hai lần.
- Chromium: modal mở lại/Escape, sanitizer, yêu cầu khách và chống gửi lặp, đăng nhập, 10 trang nội bộ, draft AI, viewport 360/390/768 và desktop. Ảnh trong artifacts/.
- Audit SQLite hiện tại không phát hiện tiền âm/lẻ; không rebuild hoặc sửa dữ liệu nghiệp vụ.

## Giới hạn kiểm chứng

- Chưa có MySQL/AI cloud thực tế để xác minh trong phiên này. MySQL cũ cần audit/migrate theo hướng dẫn trước khi triển khai; không tự chạy migration MySQL.
- Browser smoke không thay thế kiểm thử toàn bộ dữ liệu, thiết bị và accessibility chuyên sâu.
- Còn cảnh báo deprecation TestClient/httpx và Browserslist trong build; không làm thất bại kiểm tra.
- Chưa triển khai công khai. HTTPS, backup định kỳ, domain/tài khoản/secret production cần thiết lập tại server.

## Lưu ý cấu hình từ đợt trước

Lần chạy test đầu của đợt sửa trước đã đi qua test AI cũ có thể ghi GEMINI_API_KEY trống vào .env. Sau đó đã cô lập cấu hình; nhập lại key nếu trước đó đã cấu hình và bị mất. Các test mới dùng database/.env riêng.

Hướng dẫn: [vận hành và kiểm thử](HUONG_DAN_VAN_HANH.md). Báo cáo ban đầu được giữ để đối chiếu, không phản ánh trạng thái hiện tại.
