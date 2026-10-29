from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/guides", tags=["Quản lý Hướng dẫn viên"])

@router.get("", response_model=List[schemas.TourGuideOut])
def list_guides(
    status_filter: Optional[str] = Query(None, description="AVAILABLE, ON_TOUR, OFF"),
    keyword: Optional[str] = Query(None, description="Tìm theo tên, điện thoại, email, ngôn ngữ, ghi chú"),
    language: Optional[str] = Query(None, description="Lọc theo ngôn ngữ"),
    db: Session = Depends(get_db)
):
    return crud.get_guides(db, status_filter=status_filter, keyword=keyword, language=language)

@router.get("/{guide_id}", response_model=schemas.TourGuideOut)
def get_guide(guide_id: int, db: Session = Depends(get_db)):
    guide = crud.get_guide_by_id(db, guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Không tìm thấy hướng dẫn viên.")
    return guide

@router.post("", response_model=schemas.TourGuideOut)
def create_new_guide(
    guide_in: schemas.TourGuideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    return crud.create_guide(db, guide_in)

@router.put("/{guide_id}", response_model=schemas.TourGuideOut)
def update_guide_info(
    guide_id: int,
    guide_in: schemas.TourGuideUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    return crud.update_guide(db, guide_id, guide_in)

@router.delete("/{guide_id}")
def delete_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    crud.delete_guide(db, guide_id)
    return {"message": "Đã xóa hướng dẫn viên thành công."}
