# BÁO CÁO KT2: PHÁT TRIỂN NGHIỆP VỤ & XỬ LÝ RÀNG BUỘC CHỖ NGỒI
## DỰ ÁN: HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)

---

## 1. Danh sách RESTful API Endpoints (FastAPI)

Hệ thống cung cấp đầy đủ các API chuẩn mực có tài liệu Swagger tự động tại `/docs`:

| Phương thức | Đường dẫn API | Chức năng | Phân quyền (RBAC) |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Đăng nhập và nhận JWT token | Công khai |
| `POST` | `/api/v1/auth/switch-role/{role}` | Chuyển đổi quyền nhanh phục vụ kiểm thử | Công khai |
| `GET` | `/api/v1/tours` | Lấy danh sách tour (lọc theo danh mục/điểm đến) | Tất cả |
| `POST` | `/api/v1/tours` | Thêm tour du lịch mới | Admin / Tư vấn |
| `PUT` | `/api/v1/tours/{id}` | Chỉnh sửa thông tin tour | Admin / Tư vấn |
| `DELETE` | `/api/v1/tours/{id}` | Xóa tour | Admin |
| `GET` | `/api/v1/departures` | Lấy danh sách các đợt khởi hành & số chỗ | Tất cả |
| `POST` | `/api/v1/departures` | Mở đợt khởi hành mới | Admin / Tư vấn |
| `POST` | `/api/v1/departures/{id}/assign-guide/{guide_id}` | Phân công Hướng dẫn viên cho tour | Admin / Tư vấn |
| `GET` | `/api/v1/bookings` | Danh sách phiếu đặt chỗ | Tất cả |
| `POST` | `/api/v1/bookings` | Đặt tour mới (Kiểm tra & trừ số chỗ) | Tất cả |
| `POST` | `/api/v1/bookings/{id}/cancel` | Hủy tour và tính tiền hoàn cọc | Admin / Tư vấn / Kế toán |
| `GET` | `/api/v1/payments` | Lịch sử thu/chi, đặt cọc và hoàn tiền | Kế toán / Admin |
| `POST` | `/api/v1/payments` | Thu tiền đặt cọc hoặc thanh toán đợt cuối | Kế toán / Admin |
| `GET` | `/api/v1/guides` | Danh sách Hướng dẫn viên và đánh giá sao | Tất cả |
| `GET` | `/api/v1/feedbacks` | Danh sách nhận xét đánh giá từ du khách | Tất cả |
| `GET` | `/api/v1/stats/dashboard` | Báo cáo KPI, doanh thu, tỷ lệ lấp đầy | Tất cả |

---

## 2. Giải thuật Xử lý Ràng buộc Số chỗ & Chống Overbooking

Trong file `backend/app/crud.py`, thuật toán đặt tour đảm bảo tính toàn vẹn dữ liệu:

```python
def create_booking(db: Session, booking_in: schemas.BookingCreate, user_name: str):
    departure = get_departure_by_id(db, booking_in.departure_id)
    if not departure:
        raise HTTPException(status_code=404, detail="Lịch khởi hành không tồn tại.")
        
    if departure.status in ["CANCELLED", "COMPLETED"]:
        raise HTTPException(status_code=400, detail="Đợt đi đã kết thúc hoặc bị hủy.")
        
    # RÀNG BUỘC CHỐNG OVERBOOKING
    if departure.available_slots < booking_in.num_people:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không đủ chỗ trống! Chuyến đi chỉ còn lại {departure.available_slots} chỗ, yêu cầu của bạn là {booking_in.num_people} chỗ."
        )
    
    # TRỪ CHỖ TỨC THỜI
    departure.available_slots -= booking_in.num_people
    if departure.available_slots == 0:
        departure.status = "FULL" # Khóa đợt đi khi kín ghế
    
    # ... lưu booking và thanh toán ...
    db.commit()
```

---

## 3. Quy tắc Hủy Tour và Hoàn Tiền Tự Động

Khi khách hàng hủy booking, hàm `cancel_booking` tính toán hoàn tiền dựa trên số ngày trước ngày khởi hành:

$$\text{Tỷ lệ hoàn tiền} = \begin{cases} 
100\% & \text{nếu } \Delta_{\text{ngày}} \ge 15 \\ 
70\% & \text{nếu } 7 \le \Delta_{\text{ngày}} < 15 \\ 
50\% & \text{nếu } 3 \le \Delta_{\text{ngày}} < 7 \\ 
0\% & \text{nếu } \Delta_{\text{ngày}} < 3 
\end{cases}$$

Đồng thời, hàm thực hiện:
1. `departure.available_slots += booking.num_people` (hoàn trả lại số ghế).
2. Nếu trạng thái trước đó là `FULL`, tự động chuyển về `OPEN` để tiếp tục mở bán cho khách khác.
3. Tạo bản ghi giao dịch kế toán `REFUND` với số tiền hoàn chính xác.

---

## 4. Kết quả Kiểm thử Tự động (Automated Test Execution)

Toàn bộ các ca kiểm thử nghiệp vụ đã được thực thi bằng framework `pytest`:

| Tên Test Case | Mục tiêu kiểm thử | Kết quả |
|---|---|---|
| `test_booking_reduces_available_slots` | Khách đặt 2 chỗ, `available_slots` giảm chính xác từ 5 xuống 3 | **PASSED** ✅ |
| `test_prevent_overbooking` | Khách yêu cầu 6 chỗ trong khi chỉ còn 5 chỗ, hệ thống chặn lỗi 400 | **PASSED** ✅ |
| `test_booking_fills_departure_to_full` | Đặt hết toàn bộ chỗ trống, trạng thái tự động thành `FULL` | **PASSED** ✅ |
| `test_cancellation_restores_slots_and_refunds` | Hủy tour trước 20 ngày, phục hồi chỗ ngồi và hoàn 100% tiền | **PASSED** ✅ |
| `test_deposit_and_final_payment_flow` | Luồng cọc 30% (`DEPOSITED`) và thanh toán đủ (`CONFIRMED`) | **PASSED** ✅ |

**Tỷ lệ vượt qua**: **100% (5/5 tests passed)**.
