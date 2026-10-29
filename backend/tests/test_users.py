import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from backend.app.database import Base
from backend.app import models, schemas, crud

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Tạo Admin gốc
    admin = models.User(
        username="admin",
        hashed_password="hashed_admin_pass",
        full_name="Quản Trị Viên Gốc",
        role="ADMIN",
        is_active=True
    )
    session.add(admin)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_admin_user_crud(db):
    """Kiểm tra Admin có thể thêm, sửa, xóa và phân quyền tài khoản"""
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    
    # 1. Thêm tài khoản mới với vai trò CONSULTANT
    user_in = schemas.UserCreate(
        username="nhanvien_moi",
        password="secretpassword123",
        full_name="Nguyễn Văn Tư Vấn Mới",
        email="tuvanmoi@test.vn",
        phone="0901112233",
        role="CONSULTANT"
    )
    new_user = crud.create_user(db, user_in)
    assert new_user.id is not None
    assert new_user.username == "nhanvien_moi"
    assert new_user.role == "CONSULTANT"
    assert new_user.is_active == True
    
    # 2. Cập nhật và phân quyền lại sang ACCOUNTANT
    update_in = schemas.UserUpdateAdmin(
        role="ACCOUNTANT",
        full_name="Nguyễn Văn Kế Toán Chuyển Đổi"
    )
    updated_user = crud.update_user(db, new_user.id, update_in)
    assert updated_user.role == "ACCOUNTANT"
    assert updated_user.full_name == "Nguyễn Văn Kế Toán Chuyển Đổi"
    
    # 3. Lấy danh sách tài khoản
    all_users = crud.get_users(db)
    assert len(all_users) == 2
    
    # 4. Bảo vệ tài khoản admin không được xóa
    with pytest.raises(HTTPException) as exc_info:
        crud.delete_user(db, admin.id, current_user_id=new_user.id)
    assert exc_info.value.status_code == 400
    
    # 5. Xóa tài khoản nhân viên mới
    deleted = crud.delete_user(db, new_user.id, current_user_id=admin.id)
    assert deleted == True
    assert db.query(models.User).count() == 1
