from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/payments", tags=["Thanh toán & Kế toán"])

@router.get("", response_model=List[schemas.PaymentOut])
def list_payments(
    booking_id: Optional[int] = Query(None, description="Lọc theo Booking ID"),
    payment_type: Optional[str] = Query(None, description="DEPOSIT, FINAL, FULL, REFUND"),
    payment_method: Optional[str] = Query(None, description="BANK_TRANSFER, CASH, CREDIT_CARD, MOMO, VNPAY"),
    keyword: Optional[str] = Query(None, description="Tìm theo mã giao dịch, ghi chú, người thu, mã booking, tên khách"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "ACCOUNTANT", "CONSULTANT"]))
):
    return crud.get_payments(db, booking_id=booking_id, payment_type=payment_type, payment_method=payment_method, keyword=keyword)

@router.post("", response_model=schemas.PaymentOut)
def record_payment(
    payment_in: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN", "ACCOUNTANT"]))
):
    """Ghi nhận thanh toán đặt cọc hoặc đợt cuối (Kế toán & Admin)"""
    return crud.add_payment(db, payment_in, created_by=current_user.full_name)
