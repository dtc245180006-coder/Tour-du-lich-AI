from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import crud, models, auth

router = APIRouter(prefix="/stats", tags=["Thống kê & Báo cáo doanh thu"])

@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Trả về các chỉ số KPI: Doanh thu, Tỷ lệ lấp đầy, Tour bán chạy, Booking gần đây.
    Khách vãng lai và Nhân viên tư vấn (CONSULTANT) không được xem số liệu doanh thu."""
    stats = crud.get_dashboard_stats(db)
    can_view_revenue = bool(current_user and current_user.role in ["ADMIN", "ACCOUNTANT"])
    if not can_view_revenue:
        stats["total_revenue"] = 0
        stats["total_collected"] = 0
        stats["recent_bookings"] = []
        if "top_tours" in stats:
            for t in stats["top_tours"]:
                t["revenue"] = 0.0
    return stats
