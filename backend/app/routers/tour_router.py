from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/tours", tags=["Quản lý Tour & Lịch trình"])

@router.get("", response_model=List[schemas.TourOut])
def list_tours(
    category: Optional[str] = Query(None, description="Danh mục tour (BIEN_DAO, TAY_BAC, MIEN_TAY, DI_SAN...)"),
    destination: Optional[str] = Query(None, description="Lọc theo điểm đến"),
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm (mã, tên, điểm đến, điểm nổi bật...)"),
    min_price: Optional[float] = Query(None, description="Giá thấp nhất"),
    max_price: Optional[float] = Query(None, description="Giá cao nhất"),
    db: Session = Depends(get_db)
):
    return crud.get_tours(db=db, category=category, destination=destination, keyword=keyword, min_price=min_price, max_price=max_price)

@router.get("/{tour_id}", response_model=schemas.TourOut)
def get_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = crud.get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Không tìm thấy tour.")
    return tour

@router.post("", response_model=schemas.TourOut)
def create_new_tour(
    tour_in: schemas.TourCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    return crud.create_tour(db, tour_in)

@router.put("/{tour_id}", response_model=schemas.TourOut)
def update_tour_info(
    tour_id: int,
    tour_in: schemas.TourUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    return crud.update_tour(db, tour_id, tour_in)

@router.delete("/{tour_id}")
def delete_existing_tour(
    tour_id: int,
    force: bool = Query(False, description="Xóa cưỡng chế toàn bộ lịch và đặt chỗ liên quan"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    return crud.delete_tour(db, tour_id, force=force)
