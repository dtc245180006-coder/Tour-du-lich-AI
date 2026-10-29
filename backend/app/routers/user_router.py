from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas, crud, auth

router = APIRouter(prefix="/users", tags=["Quản lý Người dùng & Phân quyền (Admin Only)"])

@router.get("", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Admin xem danh sách toàn bộ tài khoản trong hệ thống"""
    return crud.get_users(db)

@router.post("", response_model=schemas.UserOut)
def create_new_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Admin thêm tài khoản mới và phân quyền (ADMIN, CONSULTANT, ACCOUNTANT)"""
    return crud.create_user(db, user_in)

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user_info(
    user_id: int,
    user_in: schemas.UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Admin chỉnh sửa thông tin, đổi vai trò, đổi mật khẩu hoặc khóa tài khoản"""
    return crud.update_user(db, user_id, user_in)

@router.delete("/{user_id}")
def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Admin xóa tài khoản người dùng khỏi hệ thống"""
    crud.delete_user(db, user_id, current_user_id=current_user.id)
    return {"message": "Đã xóa tài khoản thành công."}
