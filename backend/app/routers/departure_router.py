from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/departures", tags=["Lịch khởi hành & Số chỗ"])

@router.get("", response_model=List[schemas.DepartureOut])
def list_departures(
    tour_id: Optional[int] = Query(None, description="Lọc theo Tour ID"),
    status_filter: Optional[str] = Query(None, description="OPEN, FULL, RUNNING, COMPLETED, CANCELLED"),
    keyword: Optional[str] = Query(None, description="Tìm theo tên tour, mã tour, điểm đến, tên HDV, ghi chú"),
    guide_id: Optional[int] = Query(None, description="Lọc theo Hướng dẫn viên"),
    from_date: Optional[date] = Query(None, description="Từ ngày khởi hành (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Đến ngày khởi hành (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    departures = crud.get_departures(
        db=db, 
        tour_id=tour_id, 
        status_filter=status_filter,
        keyword=keyword,
        guide_id=guide_id,
        from_date=from_date,
        to_date=to_date
    )
    result = []
    for d in departures:
        d_out = schemas.DepartureOut.model_validate(d)
        if d.tour:
            d_out.tour_title = d.tour.title
            d_out.tour_code = d.tour.code
        if d.guide:
            d_out.guide_name = d.guide.full_name
        result.append(d_out)
    return result

@router.get("/check-conflict")
def check_guide_conflict(
    guide_id: int = Query(..., description="ID hướng dẫn viên cần kiểm tra"),
    departure_date: date = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    return_date: date = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    exclude_id: Optional[int] = Query(None, description="Bỏ qua ID đợt khởi hành hiện tại khi sửa"),
    db: Session = Depends(get_db)
):
    conflict = crud.check_guide_schedule_conflict(
        db=db,
        guide_id=guide_id,
        departure_date=departure_date,
        return_date=return_date,
        exclude_departure_id=exclude_id
    )
    if conflict:
        return conflict
    return {"has_conflict": False, "message": "Hướng dẫn viên hoàn toàn rảnh lịch trong khoảng thời gian này."}

@router.get("/{departure_id}", response_model=schemas.DepartureOut)
def get_departure(departure_id: int, db: Session = Depends(get_db)):
    dep = crud.get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.tour:
        d_out.tour_title = dep.tour.title
        d_out.tour_code = dep.tour.code
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out

@router.post("", response_model=schemas.DepartureOut)
def create_departure(
    dep_in: schemas.DepartureCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    dep = crud.create_departure(db, dep_in)
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.tour:
        d_out.tour_title = dep.tour.title
        d_out.tour_code = dep.tour.code
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out

@router.put("/{departure_id}", response_model=schemas.DepartureOut)
def update_departure(
    departure_id: int,
    dep_in: schemas.DepartureUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    dep = crud.update_departure(db, departure_id, dep_in)
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.tour:
        d_out.tour_title = dep.tour.title
        d_out.tour_code = dep.tour.code
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out

@router.post("/{departure_id}/start", response_model=schemas.DepartureOut)
def start_departure_tour(
    departure_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    dep = crud.start_departure(db, departure_id)
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.tour:
        d_out.tour_title = dep.tour.title
        d_out.tour_code = dep.tour.code
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out

@router.post("/{departure_id}/complete", response_model=schemas.DepartureOut)
def complete_departure_tour(
    departure_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    dep = crud.complete_departure(db, departure_id)
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.tour:
        d_out.tour_title = dep.tour.title
        d_out.tour_code = dep.tour.code
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out

@router.delete("/{departure_id}")
def delete_departure_item(
    departure_id: int,
    force: bool = Query(False, description="Xóa cưỡng chế đợt khởi hành và các đặt chỗ liên quan"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    crud.delete_departure(db, departure_id, force=force)
    return {"message": "Đã xóa đợt khởi hành thành công"}

@router.get("/{departure_id}/customers")
def get_departure_customers(
    departure_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"]))
):
    """Lấy danh sách khách hàng trong chuyến đi để phục vụ liên hệ khẩn cấp hoặc xử lý hủy tour."""
    dep = crud.get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    
    customers_list = []
    for b in dep.bookings:
        customers_list.append({
            "booking_id": b.id,
            "booking_code": b.booking_code,
            "customer_name": b.customer.full_name if b.customer else "N/A",
            "customer_phone": b.customer.phone if b.customer else "N/A",
            "customer_email": b.customer.email if b.customer else "",
            "num_people": b.num_people,
            "total_amount": float(b.total_amount),
            "paid_amount": float(b.paid_amount),
            "status": b.status,
            "created_at": b.created_at.strftime("%d/%m/%Y %H:%M") if b.created_at else ""
        })
    return {
        "departure_id": dep.id,
        "tour_title": dep.tour.title if dep.tour else "",
        "tour_code": dep.tour.code if dep.tour else "",
        "departure_date": str(dep.departure_date),
        "return_date": str(dep.return_date),
        "status": dep.status,
        "total_slots": dep.total_slots,
        "available_slots": dep.available_slots,
        "booked_count": len(customers_list),
        "customers": customers_list
    }

@router.post("/{departure_id}/cancel-emergency")
def cancel_departure_emergency(
    departure_id: int,
    reason: str = Query(..., description="Lý do hủy chuyến khẩn cấp"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Hủy chuyến khẩn cấp: Chuyển chuyến sang CANCELLED, hủy toàn bộ booking, hoàn 100% tiền và giải phóng HDV."""
    dep = crud.get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    
    dep.status = "CANCELLED"
    dep.notes = (dep.notes or "") + f" [HỦY KHẨN CẤP: {reason}]"
    
    cancelled_count = 0
    refund_total = 0.0
    for b in dep.bookings:
        if b.status in ["PENDING", "DEPOSITED", "CONFIRMED", "WAITING_CONFIRM"]:
            b.status = "CANCELLED"
            b.cancellation_reason = f"Công ty hủy chuyến khẩn cấp: {reason}"
            if b.paid_amount > 0:
                b.refund_amount = b.paid_amount
                refund_total += float(b.paid_amount)
                refund_tx = models.Payment(
                    booking_id=b.id,
                    payment_type="REFUND",
                    amount=b.paid_amount,
                    payment_method="BANK_TRANSFER",
                    status="COMPLETED",
                    transaction_code=f"REF-EMERGENCY-{b.booking_code}",
                    note=f"Hoàn 100% tiền hủy chuyến khẩn cấp: {reason}",
                    created_by=current_user.full_name
                )
                db.add(refund_tx)
            cancelled_count += 1
    
    if dep.guide_id:
        guide = db.query(models.TourGuide).get(dep.guide_id)
        if guide and guide.status == "ON_TOUR":
            guide.status = "AVAILABLE"
            
    db.commit()
    return {
        "success": True,
        "message": f"Đã hủy chuyến khẩn cấp thành công. Đã hủy {cancelled_count} đặt chỗ, ghi nhận hoàn tiền {refund_total:,.0f} đ.",
        "cancelled_bookings": cancelled_count,
        "refund_total": refund_total
    }

@router.post("/{departure_id}/assign-guide/{guide_id}", response_model=schemas.DepartureOut)
def assign_guide(
    departure_id: int,
    guide_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    dep = crud.get_departure_by_id(db, departure_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khởi hành.")
    
    conflict = crud.check_guide_schedule_conflict(
        db=db,
        guide_id=guide_id,
        departure_date=dep.departure_date,
        return_date=dep.return_date,
        exclude_departure_id=departure_id
    )
    if conflict:
        raise HTTPException(status_code=400, detail=conflict["message"])
        
    dep = crud.assign_guide_to_departure(db, departure_id, guide_id)
    d_out = schemas.DepartureOut.model_validate(dep)
    if dep.guide:
        d_out.guide_name = dep.guide.full_name
    return d_out
