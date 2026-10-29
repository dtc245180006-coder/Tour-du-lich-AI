from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/bookings", tags=["Quản lý Đặt chỗ & Khách hàng"])


@crud._transactional
def _create_once(db, payload, key, kind, user_name=None):
    fingerprint = hashlib.sha256((kind + payload.model_dump_json()).encode()).hexdigest()
    if key:
        if len(key) > 64 or not key.isascii() or not all(c.isalnum() or c in '-_' for c in key):
            raise HTTPException(status_code=422, detail="Mã yêu cầu không hợp lệ.")
        record = db.get(models.BookingRequestKey, key)
        if record:
            if record.fingerprint != fingerprint:
                raise HTTPException(status_code=409, detail="Mã yêu cầu đã dùng cho nội dung khác.")
            return db.get(models.Booking, record.booking_id)
    booking = (crud.create_guest_booking(db, payload) if kind == 'guest' else
               crud.create_booking(db, payload, user_name=user_name))
    if key:
        db.add(models.BookingRequestKey(key=key, fingerprint=fingerprint, booking_id=booking.id))
        try:
            db.flush()
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Yêu cầu đang được xử lý. Hãy thử lại với cùng mã.")
    return booking

@router.get("", response_model=List[schemas.BookingOut])
def list_bookings(
    status_filter: Optional[str] = Query(None, description="PENDING, DEPOSITED, CONFIRMED, COMPLETED, CANCELLED"),
    departure_id: Optional[int] = Query(None, description="Lọc theo đợt khởi hành"),
    keyword: Optional[str] = Query(None, description="Tìm theo mã đặt chỗ, tên khách, số điện thoại, email, tên tour"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT", "ACCOUNTANT"]))
):
    bookings = crud.get_bookings(db=db, status_filter=status_filter, departure_id=departure_id, keyword=keyword)
    results = []
    for b in bookings:
        b_out = schemas.BookingOut.model_validate(b)
        if b.customer:
            b_out.customer_name = b.customer.full_name
            b_out.customer_phone = b.customer.phone
        if b.departure:
            b_out.departure_date = b.departure.departure_date
            if b.departure.tour:
                b_out.tour_title = b.departure.tour.title
        results.append(b_out)
    return results

# ===================================================================
# TRA CỨU ĐƠN HÀNG DÀNH CHO KHÁCH HÀNG (KHÔNG CẦN ĐĂNG NHẬP)
# ===================================================================

def _format_booking_tracking(booking: models.Booking):
    departure = booking.departure
    tour = departure.tour if departure else None
    remaining_amount = max(0.0, float(booking.total_amount) - float(booking.paid_amount))
    
    # Số tiền cần chuyển khoản nếu còn nợ
    qr_amount = remaining_amount if booking.status != "WAITING_CONFIRM" else float(booking.deposit_amount)
    vietqr_url = (
        f"https://img.vietqr.io/image/MB-0333388888-compact2.png"
        f"?amount={int(qr_amount)}"
        f"&addInfo=VJ+{booking.booking_code}"
        f"&accountName=CONG+TY+DU+LICH+VIETJOURNEY"
    )

    return {
        "booking_code": booking.booking_code,
        "access_token": booking.access_token,
        "status": booking.status,
        "created_at": booking.created_at.strftime("%d/%m/%Y %H:%M") if booking.created_at else "",
        "num_people": booking.num_people,
        "special_requests": booking.special_requests or "Không có",
        "total_amount": float(booking.total_amount),
        "deposit_amount": float(booking.deposit_amount),
        "paid_amount": float(booking.paid_amount),
        "remaining_amount": remaining_amount,
        "refund_amount": float(booking.refund_amount or 0.0),
        "cancellation_reason": booking.cancellation_reason,
        "customer": {
            "full_name": booking.customer.full_name if booking.customer else "Khách hàng",
            "phone": booking.customer.phone if booking.customer else "",
            "email": booking.customer.email if booking.customer else ""
        },
        "tour": {
            "title": tour.title if tour else "Tour du lịch",
            "destination": tour.destination if tour else "",
            "code": tour.code if tour else "",
            "category": tour.category if tour else "",
            "duration_days": tour.duration_days if tour else 1,
            "duration_nights": tour.duration_nights if tour else 0,
            "departure_date": departure.departure_date.strftime("%d/%m/%Y") if departure and departure.departure_date else "",
            "return_date": departure.return_date.strftime("%d/%m/%Y") if departure and departure.return_date else ""
        },
        "vietqr": {
            "bank_name": "MB Bank (Ngân hàng Quân Đội)",
            "account_no": "0333388888",
            "account_name": "CONG TY DU LICH VIETJOURNEY",
            "amount": qr_amount,
            "content": f"VJ {booking.booking_code}",
            "qr_url": vietqr_url
        },
        "payments": [
            {
                "id": p.id,
                "amount": float(p.amount),
                "payment_type": p.payment_type,
                "payment_method": p.payment_method,
                "transaction_code": p.transaction_code,
                "status": p.status,
                "created_at": p.created_at.strftime("%d/%m/%Y %H:%M") if p.created_at else "",
                "note": p.note
            }
            for p in (booking.payments or []) if p.status == "COMPLETED"
        ]
    }

@router.get("/magic-track")
def magic_track_booking(
    code: str = Query(..., description="Mã đặt chỗ"),
    token: str = Query(..., description="Mã bảo mật truy cập trực tiếp từ email"),
    db: Session = Depends(get_db)
):
    """
    Tra cứu một chạm trực tiếp từ email (Magic Link):
    - Không cần đăng nhập, không cần nhập lại mật khẩu
    - Xác thực bảo mật qua access_token riêng biệt được gửi trong hộp thư của khách
    """
    code_clean = code.strip().upper()
    token_clean = token.strip()
    
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.booking_code == code_clean)
        .filter(models.Booking.access_token == token_clean)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Liên kết tra cứu không hợp lệ hoặc đơn hàng không tồn tại. Vui lòng kiểm tra lại thư điện tử của Quý khách."
        )
    return _format_booking_tracking(booking)

@router.post("/track-guest")
def track_guest_booking(
    payload: schemas.BookingTrackRequest,
    db: Session = Depends(get_db)
):
    """
    Tra cứu đơn hàng công khai qua Mã đặt chỗ + Số điện thoại hoặc Email:
    - Không cần đăng nhập
    - Bảo mật xác thực 2 yếu tố: Mã đơn + SĐT/Email trùng khớp
    """
    code_clean = payload.booking_code.strip().upper()
    contact_clean = payload.contact.strip()
    contact_lower = contact_clean.lower()
    
    booking = (
        db.query(models.Booking)
        .join(models.Customer, models.Booking.customer_id == models.Customer.id)
        .filter(models.Booking.booking_code == code_clean)
        .first()
    )
    
    if not booking or not booking.customer:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng. Vui lòng kiểm tra lại Mã đặt chỗ."
        )
        
    c_phone = (booking.customer.phone or "").strip()
    c_email = (booking.customer.email or "").strip().lower()
    
    # Kiểm tra xem contact có khớp với Số điện thoại hoặc Email đã đăng ký không
    if contact_clean != c_phone and contact_lower != c_email:
        raise HTTPException(
            status_code=403,
            detail="Số điện thoại hoặc Email không khớp với thông tin người đặt của đơn hàng này."
        )
        
    return _format_booking_tracking(booking)


@router.post("/resend-tracking-email")
def resend_tracking_email(
    payload: schemas.ResendTrackRequest,
    db: Session = Depends(get_db)
):
    """
    Trường hợp khách QUÊN MÃ ĐẶT CHỖ:
    - Nhập địa chỉ Gmail/Email của khách
    - Hệ thống tìm toàn bộ các đơn hàng của email này
    - Tự động gửi thư tổng hợp danh sách đơn kèm Magic Link một chạm về Gmail của khách
    """
    email_clean = payload.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Vui lòng nhập địa chỉ email hợp lệ.")

    # Tìm các booking gắn với email này
    customers = db.query(models.Customer).filter(models.Customer.email.ilike(email_clean)).all()
    if not customers:
        # Trả về thông báo thành công chung để bảo vệ quyền riêng tư
        return {
            "success": True,
            "message": "Nếu địa chỉ email này có đơn đặt tour trong hệ thống, VietJourney đã gửi danh sách mã đặt chỗ và liên kết tra cứu về hộp thư của bạn."
        }

    customer_ids = [c.id for c in customers]
    customer_name = customers[0].full_name

    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.customer_id.in_(customer_ids))
        .order_by(models.Booking.created_at.desc())
        .limit(10)
        .all()
    )

    if not bookings:
        return {
            "success": True,
            "message": "Nếu địa chỉ email này có đơn đặt tour trong hệ thống, VietJourney đã gửi danh sách mã đặt chỗ và liên kết tra cứu về hộp thư của bạn."
        }

    bookings_data = []
    for b in bookings:
        tour_title = b.departure.tour.title if b.departure and b.departure.tour else "Tour du lịch"
        dep_date = b.departure.departure_date.strftime("%d/%m/%Y") if b.departure and b.departure.departure_date else "---"
        bookings_data.append({
            "booking_code": b.booking_code,
            "access_token": b.access_token,
            "tour_title": tour_title,
            "departure_date": dep_date,
            "num_people": b.num_people,
            "total_amount": float(b.total_amount),
            "paid_amount": float(b.paid_amount),
            "status": b.status
        })

    from backend.app import email_service
    email_service.send_recovery_email(email_clean, customer_name, bookings_data)

    return {
        "success": True,
        "message": f"VietJourney đã gửi email chứa danh sách {len(bookings_data)} đơn đặt tour kèm liên kết tra cứu tới {email_clean}. Quý khách vui lòng kiểm tra hộp thư đến (hoặc mục Thư rác/Spam)."
    }


@router.get("/{booking_id}", response_model=schemas.BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT", "ACCOUNTANT"]))):
    b = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt chỗ.")
    b_out = schemas.BookingOut.model_validate(b)
    if b.customer:
        b_out.customer_name = b.customer.full_name
        b_out.customer_phone = b.customer.phone
    if b.departure:
        b_out.departure_date = b.departure.departure_date
        if b.departure.tour:
            b_out.tour_title = b.departure.tour.title
    return b_out

@router.post("", response_model=schemas.BookingOut)
def create_booking(
    booking_in: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"])),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Đặt tour mới:
    - Kiểm tra số chỗ còn lại, trừ chỗ tự động.
    - Chống overbooking tuyệt đối.
    - Khởi tạo thanh toán đặt cọc nếu có.
    """
    if booking_in.initial_payment and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Chỉ Admin hoặc nghiệp vụ kế toán được ghi nhận thanh toán.")
    booking = _create_once(db, booking_in, idempotency_key, f"staff:{current_user.id}", current_user.full_name)
    b_out = schemas.BookingOut.model_validate(booking)
    if booking.customer:
        b_out.customer_name = booking.customer.full_name
        b_out.customer_phone = booking.customer.phone
    if booking.departure:
        b_out.departure_date = booking.departure.departure_date
        if booking.departure.tour:
            b_out.tour_title = booking.departure.tour.title
    return b_out

@router.post("/guest-request", response_model=schemas.BookingOut)
def submit_guest_booking_request(
    guest_in: schemas.GuestBookingCreate,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Dành cho Khách vãng lai (Chưa đăng nhập):
    - Gửi thông tin đăng ký tour vào hàng chờ xác nhận (WAITING_CONFIRM)
    - Chưa trừ số chỗ thực tế của đợt khởi hành
    - Nhân viên tư vấn sẽ liên hệ khách và xác nhận giữ chỗ
    """
    booking = _create_once(db, guest_in, idempotency_key, 'guest')
    b_out = schemas.BookingOut.model_validate(booking)
    if booking.customer:
        b_out.customer_name = guest_in.customer_name
        b_out.customer_phone = guest_in.customer_phone
    if booking.departure:
        b_out.departure_date = booking.departure.departure_date
        if booking.departure.tour:
            b_out.tour_title = booking.departure.tour.title
    return b_out

@router.post("/{booking_id}/confirm", response_model=schemas.BookingOut)
def confirm_booking_by_staff(
    booking_id: int,
    confirm_in: schemas.BookingConfirmRequest = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"]))
):
    """
    Nhân viên tư vấn hoặc Admin duyệt đơn từ hàng chờ:
    - Kiểm tra số chỗ còn trống
    - Chính thức trừ chỗ ngồi và chuyển sang hàng chờ thanh toán/giữ chỗ
    """
    booking = crud.confirm_guest_booking(db, booking_id, confirm_in, user_name=current_user.full_name)
    b_out = schemas.BookingOut.model_validate(booking)
    if booking.customer:
        b_out.customer_name = booking.customer.full_name
        b_out.customer_phone = booking.customer.phone
    if booking.departure:
        b_out.departure_date = booking.departure.departure_date
        if booking.departure.tour:
            b_out.tour_title = booking.departure.tour.title
    return b_out

@router.post("/{booking_id}/reject", response_model=schemas.BookingOut)
def reject_booking_by_staff(
    booking_id: int,
    reason: str = Query(..., description="Lý do từ chối"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"]))
):
    """Từ chối đơn đặt tour trong hàng chờ tư vấn"""
    booking = crud.reject_guest_booking(db, booking_id, reason, user_name=current_user.full_name)
    b_out = schemas.BookingOut.model_validate(booking)
    if booking.customer:
        b_out.customer_name = booking.customer.full_name
        b_out.customer_phone = booking.customer.phone
    if booking.departure:
        b_out.departure_date = booking.departure.departure_date
        if booking.departure.tour:
            b_out.tour_title = booking.departure.tour.title
    return b_out

@router.delete("/{booking_id}")
def delete_booking_by_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Xóa vĩnh viễn đặt chỗ (Chỉ Quản trị viên)."""
    return crud.delete_booking(db, booking_id)

@router.post("/{booking_id}/cancel", response_model=schemas.BookingOut)
def cancel_booking(
    booking_id: int,
    cancel_in: schemas.BookingCancel,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT", "ACCOUNTANT"]))
):
    """
    Hủy đặt chỗ:
    - Hoàn trả số chỗ cho chuyến đi.
    - Tính toán tiền cọc được hoàn theo chính sách số ngày hủy.
    """
    if cancel_in.refund_percentage is not None and current_user.role not in ("ADMIN", "ACCOUNTANT"):
        raise HTTPException(status_code=403, detail="Chỉ Admin hoặc kế toán được thay đổi tỷ lệ hoàn tiền.")
    booking = crud.cancel_booking(db=db, booking_id=booking_id, cancel_in=cancel_in, user_name=current_user.full_name)
    b_out = schemas.BookingOut.model_validate(booking)
    if booking.customer:
        b_out.customer_name = booking.customer.full_name
        b_out.customer_phone = booking.customer.phone
    if booking.departure:
        b_out.departure_date = booking.departure.departure_date
        if booking.departure.tour:
            b_out.tour_title = booking.departure.tour.title
    return b_out