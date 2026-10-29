import logging
logger = logging.getLogger(__name__)
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from functools import wraps
from fastapi import HTTPException, status

from backend.app import models, schemas
from backend.app.auth import hash_password
from backend.app.money import vnd
from decimal import Decimal
from backend.app.business_time import today as business_today


def _transactional(fn):
    @wraps(fn)
    def wrapped(db, *args, **kwargs):
        outer = not db.info.get("booking_transaction")
        if outer:
            db.info["booking_transaction"] = True
        try:
            if outer and db.get_bind().dialect.name == "sqlite":
                connection = db.connection()
                if not connection.connection.driver_connection.in_transaction:
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
            result = fn(db, *args, **kwargs)
            if outer:
                db.commit()
                if hasattr(result, '__table__'):
                    db.refresh(result)
            return result
        except Exception:
            if outer:
                db.rollback()
            raise
        finally:
            if outer:
                db.info.pop("booking_transaction", None)
    return wrapped


def _reserve_slots(db, departure, people):
    if departure.departure_date < business_today() or not departure.tour.is_active:
        raise HTTPException(status_code=400, detail="Chuyến đi đã quá hạn hoặc tour ngừng hoạt động.")
    changed = db.query(models.Departure).filter(
        models.Departure.id == departure.id,
        models.Departure.status == "OPEN",
        models.Departure.available_slots >= people,
    ).update({
        models.Departure.available_slots: models.Departure.available_slots - people,
        models.Departure.status: case((models.Departure.available_slots == people, "FULL"), else_="OPEN"),
    }, synchronize_session=False)
    if changed != 1:
        raise HTTPException(status_code=400, detail="Không đủ chỗ trống hoặc chuyến đi không mở bán.")
    db.refresh(departure)


def _sync_guide_status(db, guide_id):
    if not guide_id:
        return
    db.flush()
    guide = db.get(models.TourGuide, guide_id)
    if not guide:
        return
    running = db.query(models.Departure).filter(
        models.Departure.guide_id == guide_id,
        models.Departure.status.in_(['RUNNING', 'ON_TOUR']),
    ).first()
    if running:
        guide.status = 'ON_TOUR'
    elif guide.status == 'ON_TOUR':
        guide.status = 'AVAILABLE'

# ==================== TOURS ====================
def get_tours(
    db: Session, 
    category: Optional[str] = None, 
    destination: Optional[str] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[models.Tour]:
    query = db.query(models.Tour)
    if is_active is not None:
        query = query.filter(models.Tour.is_active == is_active)
    if category and category != "ALL":
        query = query.filter(models.Tour.category == category)
    if destination:
        query = query.filter(models.Tour.destination.ilike(f"%{destination}%"))
    if min_price is not None:
        query = query.filter(models.Tour.base_price >= min_price)
    if max_price is not None:
        query = query.filter(models.Tour.base_price <= max_price)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.Tour.title.ilike(kw)) | 
            (models.Tour.destination.ilike(kw)) |
            (models.Tour.code.ilike(kw)) |
            (models.Tour.highlights.ilike(kw)) |
            (models.Tour.description.ilike(kw))
        )
    return query.order_by(desc(models.Tour.created_at)).all()

def get_tour_by_id(db: Session, tour_id: int) -> Optional[models.Tour]:
    return db.query(models.Tour).filter(models.Tour.id == tour_id).first()

def get_tour_by_code(db: Session, code: str) -> Optional[models.Tour]:
    return db.query(models.Tour).filter(models.Tour.code == code).first()

def create_tour(db: Session, tour_in: schemas.TourCreate) -> models.Tour:
    existing = get_tour_by_code(db, tour_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Mã tour '{tour_in.code}' đã tồn tại trong hệ thống."
        )
    tour = models.Tour(**tour_in.model_dump())
    db.add(tour)
    db.commit()
    db.refresh(tour)
    return tour

def update_tour(db: Session, tour_id: int, tour_in: schemas.TourUpdate) -> models.Tour:
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Không tìm thấy tour.")
    update_data = tour_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tour, field, value)
    db.commit()
    db.refresh(tour)
    return tour

def delete_tour(db: Session, tour_id: int, force: bool = False) -> dict:
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Không tìm thấy tour.")
    
    total_bookings = sum(len(dep.bookings) for dep in tour.departures)
    if total_bookings > 0 and not force:
        raise HTTPException(
            status_code=400, 
            detail=f"Tour '{tour.title}' hiện có {total_bookings} đơn đặt chỗ trong {len(tour.departures)} đợt khởi hành. Bạn cần liên hệ khách hàng để hủy/hoàn tiền trước, hoặc sử dụng tùy chọn Xóa cưỡng chế (Force Delete)."
        )
    
    if total_bookings > 0 and force:
        for dep in tour.departures:
            for b in dep.bookings:
                db.query(models.BookingRequestKey).filter(models.BookingRequestKey.booking_id == b.id).delete()
                db.query(models.Payment).filter(models.Payment.booking_id == b.id).delete()
                db.delete(b)
            if dep.guide and dep.guide.status == "ON_TOUR":
                dep.guide.status = "AVAILABLE"
            db.delete(dep)
            
    title = tour.title
    db.delete(tour)
    db.commit()
    return {"success": True, "message": f"Đã xóa vĩnh viễn tour '{title}' thành công."}

# ==================== DEPARTURES ====================
def get_departures(
    db: Session, 
    tour_id: Optional[int] = None, 
    status_filter: Optional[str] = None,
    keyword: Optional[str] = None,
    guide_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[models.Departure]:
    query = db.query(models.Departure).join(models.Tour, models.Departure.tour_id == models.Tour.id, isouter=True).join(models.TourGuide, models.Departure.guide_id == models.TourGuide.id, isouter=True)
    if tour_id:
        query = query.filter(models.Departure.tour_id == tour_id)
    if status_filter and status_filter != "ALL":
        query = query.filter(models.Departure.status == status_filter)
    if guide_id:
        query = query.filter(models.Departure.guide_id == guide_id)
    if from_date:
        query = query.filter(models.Departure.departure_date >= from_date)
    if to_date:
        query = query.filter(models.Departure.departure_date <= to_date)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.Tour.title.ilike(kw)) |
            (models.Tour.code.ilike(kw)) |
            (models.Tour.destination.ilike(kw)) |
            (models.TourGuide.full_name.ilike(kw)) |
            (models.Departure.notes.ilike(kw))
        )
    return query.order_by(models.Departure.departure_date.asc()).all()

def get_departure_by_id(db: Session, departure_id: int) -> Optional[models.Departure]:
    return db.query(models.Departure).filter(models.Departure.id == departure_id).first()

def check_guide_schedule_conflict(
    db: Session,
    guide_id: Optional[int],
    departure_date: date,
    return_date: date,
    exclude_departure_id: Optional[int] = None
) -> Optional[dict]:
    if not guide_id:
        return None
    
    if return_date < departure_date:
        raise HTTPException(
            status_code=400,
            detail="Ngày về không thể diễn ra trước ngày khởi hành."
        )

    guide = db.query(models.TourGuide).filter(models.TourGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Không tìm thấy hướng dẫn viên được chỉ định.")

    conflict_query = db.query(models.Departure).filter(
        models.Departure.guide_id == guide_id,
        models.Departure.status.notin_(["CANCELLED", "COMPLETED"]),
        models.Departure.departure_date <= return_date,
        models.Departure.return_date >= departure_date
    )
    if exclude_departure_id:
        conflict_query = conflict_query.filter(models.Departure.id != exclude_departure_id)
        
    conflict = conflict_query.first()
    if conflict:
        tour_title = conflict.tour.title if conflict.tour else f"Đợt #{conflict.id}"
        conflict_msg = (
            f"Trùng lịch: Hướng dẫn viên '{guide.full_name}' đã được phân công dẫn tour '{tour_title}' "
            f"từ ngày {conflict.departure_date.strftime('%d/%m/%Y')} đến {conflict.return_date.strftime('%d/%m/%Y')} "
            f"(Trạng thái: {conflict.status}). Vui lòng chọn hướng dẫn viên khác hoặc điều chỉnh thời gian!"
        )
        return {
            "has_conflict": True,
            "message": conflict_msg,
            "conflicting_departure_id": conflict.id,
            "conflicting_tour_title": tour_title,
            "from_date": str(conflict.departure_date),
            "to_date": str(conflict.return_date)
        }
    return None

def create_departure(db: Session, dep_in: schemas.DepartureCreate) -> models.Departure:
    if dep_in.status not in ('OPEN', 'FULL'):
        raise HTTPException(status_code=400, detail="Chuyến mới phải ở trạng thái mở bán; dùng thao tác khởi hành/kết thúc sau đó.")
    tour = get_tour_by_id(db, dep_in.tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour được chỉ định không tồn tại.")
    
    if dep_in.return_date < dep_in.departure_date:
        raise HTTPException(status_code=400, detail="Ngày về không thể diễn ra trước ngày khởi hành.")

    if dep_in.guide_id:
        conflict = check_guide_schedule_conflict(
            db=db,
            guide_id=dep_in.guide_id,
            departure_date=dep_in.departure_date,
            return_date=dep_in.return_date
        )
        if conflict:
            raise HTTPException(status_code=400, detail=conflict["message"])

    slots = dep_in.total_slots
    dep = models.Departure(
        tour_id=dep_in.tour_id,
        departure_date=dep_in.departure_date,
        return_date=dep_in.return_date,
        total_slots=slots,
        available_slots=dep_in.available_slots if dep_in.available_slots is not None else slots,
        price_override=dep_in.price_override,
        guide_id=dep_in.guide_id,
        status=dep_in.status or "OPEN",
        notes=dep_in.notes
    )
    dep.status = 'FULL' if dep.available_slots == 0 else 'OPEN'
    if dep.status in ["RUNNING", "ON_TOUR"] and dep.guide_id:
        guide = db.query(models.TourGuide).get(dep.guide_id)
        if guide:
            guide.status = "ON_TOUR"

    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep

@_transactional
def update_departure(db: Session, departure_id: int, dep_in: schemas.DepartureUpdate) -> models.Departure:
    dep = get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")

    db.refresh(dep, with_for_update=True)
    old_guide_id = dep.guide_id
    if dep_in.status is not None and dep_in.status != dep.status:
        if not (dep.status in ('OPEN', 'FULL') and dep_in.status == 'CANCELLED'):
            raise HTTPException(status_code=400, detail="Dùng thao tác khởi hành/kết thúc để đổi trạng thái. Không mở lại chuyến đã kết thúc hoặc hủy.")
    if dep.status in ('RUNNING', 'ON_TOUR', 'COMPLETED', 'CANCELLED') and 'guide_id' in dep_in.model_fields_set and dep_in.guide_id != dep.guide_id:
        raise HTTPException(status_code=400, detail="Chỉ đổi hướng dẫn viên trước khi khởi hành.")
    reserved = dep.total_slots - dep.available_slots
    new_total = dep_in.total_slots if dep_in.total_slots is not None else dep.total_slots
    if new_total < reserved:
        raise HTTPException(status_code=400, detail="Sức chứa mới nhỏ hơn số chỗ đã giữ.")
    expected_available = new_total - reserved
    if dep_in.available_slots is not None and dep_in.available_slots != expected_available:
        raise HTTPException(status_code=400, detail="Chỗ còn lại được tính từ sức chứa và số đã giữ.")
    if dep_in.status == "CANCELLED" and any(b.status not in ("CANCELLED", "WAITING_CONFIRM") for b in dep.bookings):
        raise HTTPException(status_code=400, detail="Cần xử lý các booking trước khi hủy chuyến.")
    target_dep_date = dep_in.departure_date if dep_in.departure_date is not None else dep.departure_date
    target_ret_date = dep_in.return_date if dep_in.return_date is not None else dep.return_date
    target_guide_id = dep_in.guide_id if 'guide_id' in dep_in.model_fields_set else dep.guide_id

    if target_ret_date < target_dep_date:
        raise HTTPException(status_code=400, detail="Ngày về không thể diễn ra trước ngày khởi hành.")

    if target_guide_id:
        conflict = check_guide_schedule_conflict(
            db=db,
            guide_id=target_guide_id,
            departure_date=target_dep_date,
            return_date=target_ret_date,
            exclude_departure_id=departure_id
        )
        if conflict:
            raise HTTPException(status_code=400, detail=conflict["message"])

    update_data = dep_in.model_dump(exclude_unset=True)
    update_data["available_slots"] = expected_available
    for field, value in update_data.items():
        setattr(dep, field, value)
    
    if dep.available_slots <= 0 and dep.status == "OPEN":
        dep.status = "FULL"
    elif dep.status == "FULL" and dep.available_slots > 0:
        dep.status = "OPEN"
        
    _sync_guide_status(db, old_guide_id)
    _sync_guide_status(db, dep.guide_id)

    db.flush()
    db.refresh(dep)
    return dep

@_transactional
def start_departure(db: Session, departure_id: int) -> models.Departure:
    dep = get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    db.refresh(dep, with_for_update=True)
    if not dep.guide_id:
        raise HTTPException(status_code=400, detail="Chưa có hướng dẫn viên phụ trách đợt tour này! Vui lòng phân công HDV trước khi khởi hành.")
    
    if dep.status not in ("OPEN", "FULL"):
        raise HTTPException(status_code=400, detail="Chỉ khởi hành chuyến đang mở hoặc đủ chỗ.")
    if any(b.status in ('PENDING', 'DEPOSITED', 'CONFIRMED') and b.paid_amount < b.total_amount for b in dep.bookings):
        raise HTTPException(status_code=400, detail="Cần thanh toán đủ các booking đã duyệt trước khi khởi hành.")
    dep.status = "RUNNING"
    if dep.guide:
        dep.guide.status = "ON_TOUR"
    db.flush()
    db.refresh(dep)
    return dep

@_transactional
def complete_departure(db: Session, departure_id: int) -> models.Departure:
    dep = get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    db.refresh(dep, with_for_update=True)
    
    if dep.status not in ("RUNNING", "ON_TOUR"):
        raise HTTPException(status_code=400, detail="Chỉ kết thúc chuyến đang chạy.")
    if any(b.status in ('PENDING', 'DEPOSITED', 'CONFIRMED') and b.paid_amount < b.total_amount for b in dep.bookings):
        raise HTTPException(status_code=400, detail="Cần xử lý các booking chưa thanh toán đủ trước khi kết thúc.")
    for booking in dep.bookings:
        if booking.status in ('PENDING', 'DEPOSITED', 'CONFIRMED'):
            booking.status = 'COMPLETED'
        elif booking.status == 'WAITING_CONFIRM':
            booking.status = 'CANCELLED'
            booking.cancellation_reason = 'Yêu cầu chưa được duyệt khi chuyến kết thúc.'
    dep.status = "COMPLETED"
    if dep.guide:
        other_active = db.query(models.Departure).filter(
            models.Departure.guide_id == dep.guide_id,
            models.Departure.id != dep.id,
            models.Departure.status.in_(["RUNNING", "ON_TOUR"])
        ).first()
        if not other_active:
            dep.guide.status = "AVAILABLE"
    db.flush()
    db.refresh(dep)
    return dep

def delete_departure(db: Session, departure_id: int, force: bool = False) -> bool:
    dep = get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    if dep.bookings and not force:
        raise HTTPException(
            status_code=400, 
            detail=f"Đợt khởi hành hiện có {len(dep.bookings)} đặt chỗ. Hãy hủy chuyến và hoàn tiền cho khách trước, hoặc dùng tùy chọn Xóa cưỡng chế."
        )
    if dep.bookings and force:
        for b in dep.bookings:
            db.query(models.BookingRequestKey).filter(models.BookingRequestKey.booking_id == b.id).delete()
            db.query(models.Payment).filter(models.Payment.booking_id == b.id).delete()
            db.delete(b)
            
    guide_id = dep.guide_id
    db.delete(dep)
    db.commit()
    if guide_id:
        guide = db.query(models.TourGuide).get(guide_id)
        if guide:
            other_active = db.query(models.Departure).filter(
                models.Departure.guide_id == guide_id,
                models.Departure.status.in_(["RUNNING", "ON_TOUR"])
            ).first()
            if not other_active and guide.status == "ON_TOUR":
                guide.status = "AVAILABLE"
                db.commit()
    return True

# ==================== CUSTOMERS ====================
def get_or_create_customer(
    db: Session,
    phone: str,
    full_name: str,
    email: Optional[str] = None,
    id_card: Optional[str] = None,
    address: Optional[str] = None
) -> models.Customer:
    customer = db.query(models.Customer).filter(models.Customer.phone == phone).first()
    if customer:
        if email and email.strip():
            customer.email = email.strip()
        if full_name and full_name.strip():
            customer.full_name = full_name.strip()
        if id_card:
            customer.id_card = id_card
        if address:
            customer.address = address
        db.flush()
        db.refresh(customer)
        return customer
    
    customer = models.Customer(
        full_name=full_name,
        phone=phone,
        email=email,
        id_card=id_card,
        address=address
    )
    db.add(customer)
    db.flush()
    db.refresh(customer)
    return customer

# ==================== BOOKINGS & SLOTS LOGIC ====================
@_transactional
def create_booking(db: Session, booking_in: schemas.BookingCreate, user_name: str = "Hệ thống") -> models.Booking:
    """
    Nghiệp vụ cốt lõi:
    1. Kiểm tra lịch khởi hành có tồn tại và đang mở không.
    2. Kiểm tra số chỗ còn trống (Tránh overbooking).
    3. Giảm available_slots tương ứng.
    4. Tạo hoặc liên kết khách hàng.
    5. Tính toán tổng tiền, tiền cọc (30%).
    6. Ghi nhận thanh toán ban đầu nếu có.
    """
    departure = get_departure_by_id(db, booking_in.departure_id)
    if not departure:
        raise HTTPException(status_code=404, detail="Lịch khởi hành không tồn tại.")
        
    if departure.status not in ["OPEN", "FULL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lịch khởi hành đang ở trạng thái '{departure.status}', không thể nhận đặt chỗ mới."
        )
        
    # Ràng buộc số chỗ còn (Slot Constraint & Overbooking Prevention)
    if departure.available_slots < booking_in.num_people:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không đủ chỗ trống! Chuyến đi chỉ còn lại {departure.available_slots} chỗ, yêu cầu của bạn là {booking_in.num_people} chỗ."
        )
    
    # Giảm số chỗ trống
    _reserve_slots(db, departure, booking_in.num_people)
        
    # Lấy hoặc tạo khách hàng
    customer = get_or_create_customer(
        db=db,
        phone=booking_in.customer_phone,
        full_name=booking_in.customer_name,
        email=booking_in.customer_email,
        id_card=booking_in.customer_id_card,
        address=booking_in.customer_address
    )
    
    # Tính giá
    unit_price = departure.price_override if departure.price_override is not None else departure.tour.base_price
    total_amount = unit_price * booking_in.num_people
    deposit_amount = vnd(Decimal(total_amount) * Decimal('0.3'))
    
    # Mã đặt chỗ độc nhất
    booking_code = f"BK-{business_today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    paid = 0.0
    booking_status = "PENDING"
    
    booking = models.Booking(
        booking_code=booking_code,
        departure_id=departure.id,
        customer_id=customer.id,
        num_people=booking_in.num_people,
        total_amount=total_amount,
        deposit_amount=deposit_amount,
        paid_amount=0.0,
        status=booking_status,
        special_requests=booking_in.special_requests,
        access_token=uuid.uuid4().hex
    )
    db.add(booking)
    db.flush()
    db.refresh(booking)
    
    # Nếu có thanh toán trước
    if booking_in.initial_payment and booking_in.initial_payment > 0:
        add_payment(
            db=db,
            payment_in=schemas.PaymentCreate(
                booking_id=booking.id,
                payment_type="DEPOSIT" if booking_in.initial_payment < total_amount else "FULL",
                amount=booking_in.initial_payment,
                payment_method=booking_in.payment_method or "BANK_TRANSFER",
                transaction_code=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                note="Thanh toán khi tạo đặt chỗ"
            ),
            created_by=user_name
        )
        db.refresh(booking)
        
    try:
        from backend.app import email_service
        if customer and customer.email:
            email_service.send_booking_confirmation_email(booking, customer, departure, departure.tour)
    except Exception as err:
        logger.error(f"Lỗi gửi email xác nhận đặt tour: {err}")
        
    return booking

@_transactional
def create_guest_booking(db: Session, guest_in: schemas.GuestBookingCreate) -> models.Booking:
    """
    Dành cho khách vãng lai (chưa đăng nhập):
    - Gửi yêu cầu đặt tour vào hàng chờ 'WAITING_CONFIRM'
    - Chưa trừ số chỗ thực tế cho đến khi Nhân viên tư vấn liên hệ và xác nhận giữ chỗ
    """
    departure = get_departure_by_id(db, guest_in.departure_id)
    if not departure:
        raise HTTPException(status_code=404, detail="Lịch khởi hành không tồn tại.")
        
    if departure.status != "OPEN" or departure.available_slots <= 0 or departure.departure_date < business_today() or not departure.tour.is_active:
        raise HTTPException(status_code=400, detail="Đợt khởi hành này không còn nhận đăng ký.")
        
    customer = get_or_create_customer(
        db=db,
        phone=guest_in.customer_phone,
        full_name=guest_in.customer_name,
        email=guest_in.customer_email
    )
    
    unit_price = departure.price_override if departure.price_override is not None else departure.tour.base_price
    total_amount = unit_price * guest_in.num_people
    deposit_amount = vnd(Decimal(total_amount) * Decimal('0.3'))
    
    booking_code = f"REQ-{business_today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    booking = models.Booking(
        booking_code=booking_code,
        departure_id=departure.id,
        customer_id=customer.id,
        num_people=guest_in.num_people,
        total_amount=total_amount,
        deposit_amount=deposit_amount,
        paid_amount=0.0,
        status="WAITING_CONFIRM",
        special_requests=guest_in.special_requests,
        access_token=uuid.uuid4().hex
    )
    db.add(booking)
    db.flush()
    db.refresh(booking)
    try:
        from backend.app import email_service
        if customer and customer.email:
            email_service.send_booking_confirmation_email(booking, customer, departure, departure.tour)
    except Exception as err:
        logger.error(f"Lỗi gửi email xác nhận đặt tour cho khách: {err}")
    return booking

@_transactional
def confirm_guest_booking(db: Session, booking_id: int, confirm_in: schemas.BookingConfirmRequest, user_name: str = "Tư Vấn Viên") -> models.Booking:
    """
    Nhân viên tư vấn hoặc Admin xác nhận yêu cầu từ khách vãng lai:
    - Kiểm tra số chỗ còn trống
    - Trừ chỗ thực tế (available_slots -= num_people)
    - Chuyển trạng thái sang CONFIRMED hoặc PENDING (chờ đặt cọc)
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).with_for_update().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu đặt chỗ.")
        
    if booking.status != "WAITING_CONFIRM":
        raise HTTPException(status_code=400, detail=f"Yêu cầu đang ở trạng thái '{booking.status}', không thể xác nhận lại.")
        
    departure = booking.departure
    if departure.available_slots < booking.num_people:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ chỗ trống để duyệt! Chuyến đi chỉ còn {departure.available_slots} chỗ, yêu cầu của khách là {booking.num_people} chỗ."
        )
        
    # Trừ chỗ
    _reserve_slots(db, departure, booking.num_people)
        
    booking.status = "PENDING" if booking.paid_amount == 0 else ("DEPOSITED" if booking.paid_amount < booking.total_amount else "CONFIRMED")
    
    if confirm_in and confirm_in.note:
        booking.special_requests = f"{booking.special_requests or ''} | [Tư vấn viên {user_name}]: {confirm_in.note}".strip(" | ")
        
    db.flush()
    db.refresh(booking)
    try:
        from backend.app import email_service
        if booking.customer and booking.customer.email:
            email_service.send_booking_confirmation_email(booking, booking.customer, departure, departure.tour)
    except Exception as err:
        logger.error(f"Lỗi gửi email xác nhận đặt tour cho khách: {err}")
    return booking

@_transactional
def reject_guest_booking(db: Session, booking_id: int, reason: str, user_name: str = "Tư Vấn Viên") -> models.Booking:
    """Từ chối yêu cầu đặt chỗ từ khách vãng lai"""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).with_for_update().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu đặt chỗ.")
        
    if booking.status != "WAITING_CONFIRM":
        raise HTTPException(status_code=400, detail="Chỉ được từ chối yêu cầu chưa duyệt.")
    booking.status = "CANCELLED"
    booking.cancellation_reason = f"Tư vấn viên {user_name} từ chối: {reason}"
    db.flush()
    db.refresh(booking)
    try:
        from backend.app import email_service
        if customer and customer.email:
            email_service.send_booking_confirmation_email(booking, customer, departure, departure.tour)
    except Exception as err:
        logger.error(f"Lỗi gửi email xác nhận đặt tour cho khách: {err}")
    return booking

def delete_booking(db: Session, booking_id: int) -> dict:
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt chỗ.")
    
    # Phục hồi chỗ nếu đơn đang giữ chỗ
    if booking.status in ["PENDING", "DEPOSITED", "CONFIRMED"] and booking.departure:
        dep = booking.departure
        dep.available_slots = min(dep.total_slots, dep.available_slots + booking.num_people)
        if dep.status == "FULL" and dep.available_slots > 0:
            dep.status = "OPEN"
    
    # Xóa bản ghi liên kết phụ thuộc
    db.query(models.BookingRequestKey).filter(models.BookingRequestKey.booking_id == booking_id).delete()
    db.query(models.Payment).filter(models.Payment.booking_id == booking_id).delete()
    
    code = booking.booking_code
    db.delete(booking)
    db.commit()
    return {"success": True, "message": f"Đã xóa vĩnh viễn đặt chỗ {code} thành công."}

@_transactional
def cancel_booking(db: Session, booking_id: int, cancel_in: schemas.BookingCancel, user_name: str = "Hệ thống") -> models.Booking:
    """
    Nghiệp vụ hủy tour:
    1. Kiểm tra trạng thái hiện tại.
    2. Phục hồi lại số chỗ trống cho đợt khởi hành.
    3. Tính toán chính sách hoàn tiền dựa trên số ngày trước ngày đi:
       - >= 15 ngày: Hoàn 100% số tiền đã đóng
       - 7 - 14 ngày: Hoàn 70%
       - 3 - 6 ngày: Hoàn 50%
       - < 3 ngày: Không hoàn tiền (0%)
    4. Tạo bản ghi hoàn tiền (REFUND).
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).with_for_update().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt chỗ.")
        
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Đặt chỗ này đã được hủy trước đó.")
    if booking.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Chuyến đi đã hoàn thành, không thể hủy đặt chỗ.")
        
    departure = booking.departure
    # Phục hồi chỗ
    if departure.status in ('RUNNING', 'ON_TOUR', 'COMPLETED'):
        raise HTTPException(status_code=400, detail="Không hủy theo chính sách trước chuyến sau khi đã khởi hành.")
    if booking.status != "WAITING_CONFIRM":
        db.query(models.Departure).filter(models.Departure.id == departure.id).update(
            {models.Departure.available_slots: models.Departure.available_slots + booking.num_people},
            synchronize_session=False,
        )
        db.refresh(departure)
    if departure.status == "FULL" and departure.available_slots > 0:
        departure.status = "OPEN"
        
    # Tính số ngày còn lại đến lúc khởi hành
    days_left = (departure.departure_date - business_today()).days
    refund_rate = 0.0
    if cancel_in.refund_percentage is not None:
        refund_rate = cancel_in.refund_percentage / 100.0
    else:
        if days_left >= 15:
            refund_rate = 1.0
        elif days_left >= 7:
            refund_rate = 0.7
        elif days_left >= 3:
            refund_rate = 0.5
        else:
            refund_rate = 0.0
            
    refund_amount = vnd(Decimal(booking.paid_amount) * Decimal(str(refund_rate)))
    booking.refund_amount = refund_amount
    booking.cancellation_reason = f"{cancel_in.reason} (Hủy trước {days_left} ngày, hoàn {int(refund_rate*100)}%)"
    booking.status = "CANCELLED"
    
    # Ghi nhận hoàn tiền nếu refund_amount > 0
    if refund_amount > 0:
        payment = models.Payment(
            booking_id=booking.id,
            payment_type="REFUND",
            amount=refund_amount,
            payment_method="BANK_TRANSFER",
            status="COMPLETED",
            transaction_code=f"REF-{uuid.uuid4().hex[:8].upper()}",
            note=f"Hoàn trả hủy tour: {booking.cancellation_reason}",
            created_by=user_name
        )
        db.add(payment)
        
    db.flush()
    db.refresh(booking)
    try:
        from backend.app import email_service
        if booking.customer and booking.customer.email:
            email_service.send_cancellation_email(booking, booking.customer)
    except Exception as err:
        logger.error(f"Lỗi gửi email hủy đặt tour cho khách: {err}")
    return booking

def get_bookings(
    db: Session, 
    status_filter: Optional[str] = None, 
    departure_id: Optional[int] = None,
    keyword: Optional[str] = None
) -> List[models.Booking]:
    query = db.query(models.Booking).join(models.Customer, models.Booking.customer_id == models.Customer.id, isouter=True).join(models.Departure, models.Booking.departure_id == models.Departure.id, isouter=True).join(models.Tour, models.Departure.tour_id == models.Tour.id, isouter=True)
    if status_filter and status_filter != "ALL":
        query = query.filter(models.Booking.status == status_filter)
    if departure_id:
        query = query.filter(models.Booking.departure_id == departure_id)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.Booking.booking_code.ilike(kw)) |
            (models.Customer.full_name.ilike(kw)) |
            (models.Customer.phone.ilike(kw)) |
            (models.Customer.email.ilike(kw)) |
            (models.Tour.title.ilike(kw)) |
            (models.Tour.code.ilike(kw))
        )
    return query.order_by(desc(models.Booking.created_at)).all()

# ==================== PAYMENTS ====================
@_transactional
def add_payment(db: Session, payment_in: schemas.PaymentCreate, created_by: str = "Kế toán") -> models.Payment:
    booking = db.query(models.Booking).filter(models.Booking.id == payment_in.booking_id).with_for_update().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt chỗ tương ứng.")
        
    if payment_in.transaction_code:
        existing = db.query(models.Payment).filter(
            models.Payment.booking_id == booking.id,
            models.Payment.transaction_code == payment_in.transaction_code).first()
        if existing:
            if existing.amount != payment_in.amount or existing.payment_type != payment_in.payment_type:
                raise HTTPException(status_code=409, detail="Mã giao dịch đã dùng với nội dung khác.")
            return existing
    if booking.status not in ("PENDING", "DEPOSITED", "CONFIRMED"):
        raise HTTPException(status_code=400, detail="Trạng thái đặt chỗ không cho phép thu tiền.")
    if payment_in.payment_type == "REFUND":
        raise HTTPException(status_code=400, detail="Hoàn tiền phải đi qua nghiệp vụ hủy đặt chỗ.")
    if payment_in.amount <= 0 or payment_in.amount > booking.total_amount - booking.paid_amount:
        raise HTTPException(status_code=400, detail="Số tiền phải dương và không vượt số còn phải thu.")
    payment = models.Payment(
        booking_id=payment_in.booking_id,
        payment_type=payment_in.payment_type,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        status="COMPLETED",
        transaction_code=payment_in.transaction_code or f"PAY-{uuid.uuid4().hex[:8].upper()}",
        note=payment_in.note,
        created_by=created_by
    )
    db.add(payment)
    
    # Cập nhật số tiền đã đóng của booking
    booking.paid_amount += payment_in.amount
    if booking.paid_amount >= booking.total_amount:
        booking.status = "CONFIRMED"
    elif booking.paid_amount >= booking.deposit_amount:
        booking.status = "DEPOSITED"
        
    db.flush()
    db.refresh(payment)
    try:
        from backend.app import email_service
        if booking.customer and booking.customer.email:
            email_service.send_payment_received_email(payment, booking, booking.customer)
    except Exception as err:
        logger.error(f"Lỗi gửi email xác nhận thanh toán: {err}")
    return payment

def get_payments(
    db: Session, 
    booking_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    payment_method: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[models.Payment]:
    query = db.query(models.Payment).join(models.Booking, models.Payment.booking_id == models.Booking.id, isouter=True).join(models.Customer, models.Booking.customer_id == models.Customer.id, isouter=True)
    if booking_id:
        query = query.filter(models.Payment.booking_id == booking_id)
    if payment_type and payment_type != "ALL":
        query = query.filter(models.Payment.payment_type == payment_type)
    if payment_method and payment_method != "ALL":
        query = query.filter(models.Payment.payment_method == payment_method)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.Payment.transaction_code.ilike(kw)) |
            (models.Payment.note.ilike(kw)) |
            (models.Payment.created_by.ilike(kw)) |
            (models.Booking.booking_code.ilike(kw)) |
            (models.Customer.full_name.ilike(kw)) |
            (models.Customer.phone.ilike(kw))
        )
    return query.order_by(desc(models.Payment.created_at)).all()

# ==================== TOUR GUIDES ====================
def get_guides(
    db: Session, 
    status_filter: Optional[str] = None,
    keyword: Optional[str] = None,
    language: Optional[str] = None
) -> List[models.TourGuide]:
    query = db.query(models.TourGuide)
    if status_filter and status_filter != "ALL":
        query = query.filter(models.TourGuide.status == status_filter)
    if language and language != "ALL":
        query = query.filter(models.TourGuide.languages.ilike(f"%{language}%"))
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.TourGuide.full_name.ilike(kw)) |
            (models.TourGuide.phone.ilike(kw)) |
            (models.TourGuide.email.ilike(kw)) |
            (models.TourGuide.languages.ilike(kw)) |
            (models.TourGuide.notes.ilike(kw))
        )
    return query.order_by(desc(models.TourGuide.rating)).all()

def get_guide_by_id(db: Session, guide_id: int) -> Optional[models.TourGuide]:
    return db.query(models.TourGuide).filter(models.TourGuide.id == guide_id).first()

def create_guide(db: Session, guide_in: schemas.TourGuideCreate) -> models.TourGuide:
    guide = models.TourGuide(**guide_in.model_dump())
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide

def update_guide(db: Session, guide_id: int, guide_in: schemas.TourGuideUpdate) -> models.TourGuide:
    guide = get_guide_by_id(db, guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Không tìm thấy hướng dẫn viên.")
    update_data = guide_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(guide, field, val)
    db.commit()
    db.refresh(guide)
    return guide

def delete_guide(db: Session, guide_id: int) -> bool:
    guide = get_guide_by_id(db, guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Không tìm thấy hướng dẫn viên.")
    # Đặt guide_id của các chuyến đi liên quan thành None để tránh lỗi ràng buộc
    db.query(models.Departure).filter(models.Departure.guide_id == guide_id).update({"guide_id": None})
    db.delete(guide)
    db.commit()
    return True

@_transactional
def assign_guide_to_departure(db: Session, departure_id: int, guide_id: int) -> models.Departure:
    departure = get_departure_by_id(db, departure_id)
    if not departure:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    db.refresh(departure, with_for_update=True)
    if departure.status not in ('OPEN', 'FULL'):
        raise HTTPException(status_code=400, detail="Chỉ phân công hướng dẫn viên trước khi khởi hành.")
    guide = db.query(models.TourGuide).filter(models.TourGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Không tìm thấy hướng dẫn viên.")
    conflict = check_guide_schedule_conflict(db, guide_id, departure.departure_date, departure.return_date, departure.id)
    if conflict:
        raise HTTPException(status_code=400, detail=conflict['message'])
    old_guide_id = departure.guide_id
    departure.guide_id = guide_id
    _sync_guide_status(db, old_guide_id)
    _sync_guide_status(db, guide_id)
    db.flush()
    db.refresh(departure)
    return departure

# ==================== FEEDBACKS ====================
def create_feedback(db: Session, fb_in: schemas.FeedbackCreate) -> models.Feedback:
    sentiment = "POSITIVE" if fb_in.rating >= 4 else ("NEUTRAL" if fb_in.rating == 3 else "NEGATIVE")
    fb = models.Feedback(
        tour_id=fb_in.tour_id,
        booking_id=fb_in.booking_id,
        customer_name=fb_in.customer_name,
        rating=fb_in.rating,
        comments=fb_in.comments,
        guide_rating=fb_in.guide_rating,
        sentiment=sentiment
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def get_feedbacks(
    db: Session, 
    tour_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    rating: Optional[int] = None,
    keyword: Optional[str] = None
) -> List[models.Feedback]:
    query = db.query(models.Feedback).join(models.Tour, models.Feedback.tour_id == models.Tour.id, isouter=True)
    if tour_id:
        query = query.filter(models.Feedback.tour_id == tour_id)
    if sentiment and sentiment != "ALL":
        query = query.filter(models.Feedback.sentiment == sentiment)
    if rating:
        query = query.filter(models.Feedback.rating == rating)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (models.Feedback.customer_name.ilike(kw)) |
            (models.Feedback.comments.ilike(kw)) |
            (models.Tour.title.ilike(kw))
        )
    return query.order_by(desc(models.Feedback.created_at)).all()

# ==================== DASHBOARD & STATS ====================
def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    total_tours = db.query(func.count(models.Tour.id)).filter(models.Tour.is_active == True).scalar() or 0
    active_departures = db.query(func.count(models.Departure.id)).filter(models.Departure.status.in_(["OPEN", "FULL"])).scalar() or 0
    total_bookings = db.query(func.count(models.Booking.id)).scalar() or 0
    
    # Doanh thu dự tính từ các booking hợp lệ (không tính đơn hủy)
    valid_bookings = db.query(models.Booking).filter(models.Booking.status.in_(["PENDING", "DEPOSITED", "CONFIRMED", "COMPLETED"])).all()
    total_revenue = sum(b.total_amount for b in valid_bookings)
    receipts = db.query(func.sum(models.Payment.amount)).filter(models.Payment.status == 'COMPLETED', models.Payment.payment_type != 'REFUND').scalar() or 0
    refunds = db.query(func.sum(models.Payment.amount)).filter(models.Payment.status == 'COMPLETED', models.Payment.payment_type == 'REFUND').scalar() or 0
    total_collected = receipts - refunds
    average_rating = db.query(func.avg(models.Feedback.rating)).scalar()
    
    # Tỷ lệ lấp đầy bình quân (Occupancy Rate)
    departures = db.query(models.Departure).filter(models.Departure.status.in_(["OPEN", "FULL", "COMPLETED"])).all()
    if departures:
        total_slots = sum(d.total_slots for d in departures)
        booked_slots = sum(d.total_slots - d.available_slots for d in departures)
        avg_occupancy = round((booked_slots / total_slots) * 100, 1) if total_slots > 0 else 0.0
    else:
        avg_occupancy = 0.0
        
    # Top 5 tour bán chạy
    top_tours_query = (
        db.query(
            models.Tour.title,
            models.Tour.code,
            models.Tour.destination,
            func.count(models.Booking.id).label("booking_count"),
            func.sum(models.Booking.num_people).label("total_passengers"),
            func.sum(models.Booking.total_amount).label("revenue")
        )
        .join(models.Departure, models.Tour.id == models.Departure.tour_id)
        .join(models.Booking, models.Departure.id == models.Booking.departure_id)
        .filter(models.Booking.status.in_(["PENDING", "DEPOSITED", "CONFIRMED", "COMPLETED"]))
        .group_by(models.Tour.id)
        .order_by(desc("booking_count"))
        .limit(5)
        .all()
    )
    
    top_tours = [
        {
            "title": t.title,
            "code": t.code,
            "destination": t.destination,
            "booking_count": t.booking_count,
            "total_passengers": t.total_passengers or 0,
            "revenue": float(t.revenue or 0.0)
        }
        for t in top_tours_query
    ]
    
    recent_bookings = (
        db.query(models.Booking)
        .order_by(desc(models.Booking.created_at))
        .limit(5)
        .all()
    )
    
    return {
        "total_tours": total_tours,
        "active_departures": active_departures,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "total_collected": total_collected,
        "average_rating": round(float(average_rating), 1) if average_rating is not None else None,
        "average_occupancy_rate": avg_occupancy,
        "top_tours": top_tours,
        "recent_bookings": [
            {
                "id": b.id,
                "code": b.booking_code,
                "customer": b.customer.full_name if b.customer else "Khách",
                "tour": b.departure.tour.title if b.departure and b.departure.tour else "",
                "num_people": b.num_people,
                "total": b.total_amount,
                "status": b.status,
                "created_at": b.created_at.strftime("%d/%m/%Y %H:%M")
            }
            for b in recent_bookings
        ]
    }

# ==================== USER MANAGEMENT (ADMIN ONLY) ====================
def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).order_by(models.User.id.asc()).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tên đăng nhập '{user_in.username}' đã tồn tại.")
        
    user = models.User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        email=user_in.email,
        phone=user_in.phone,
        role=user_in.role.upper(),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, user_in: schemas.UserUpdateAdmin) -> models.User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if user.role == 'ADMIN' and user.is_active and (user_in.is_active is False or (user_in.role is not None and user_in.role != 'ADMIN')):
        other_admin = db.query(models.User).filter(models.User.id != user.id, models.User.role == 'ADMIN', models.User.is_active == True).first()
        if not other_admin:
            raise HTTPException(status_code=400, detail="Không thể vô hiệu hóa hoặc hạ quyền Admin hoạt động cuối cùng.")
        
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.role is not None:
        user.role = user_in.role.upper()
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password:
        user.hashed_password = hash_password(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int, current_user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
        
    if user.id == current_user_id:
        raise HTTPException(status_code=400, detail="Bạn không thể xóa chính tài khoản đang đăng nhập.")
        
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản Quản trị viên gốc.")
        
    db.delete(user)
    db.commit()
    return True
