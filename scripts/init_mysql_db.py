"""
Script khởi tạo và nạp dữ liệu mẫu vào cơ sở dữ liệu MySQL (VietJourney AI)
Cách chạy:
    python scripts/init_mysql_db.py
"""
import sys
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Đảm bảo in tiếng Việt có dấu an toàn trên Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pymysql
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import init_db

def main():
    print("=" * 60)
    print("  KHỞI TẠO CƠ SỞ DỮ LIỆU MYSQL - VIETJOURNEY AI")
    print("=" * 60)
    print(f"Host:     {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"User:     {settings.DB_USER}")
    print(f"Database: {settings.DB_NAME}")
    print("-" * 60)

    # 1. Đảm bảo Database đã tồn tại trên MySQL
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset="utf8mb4"
        )
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        print(f"[1/3] Đã xác thực / tạo Database MySQL: `{settings.DB_NAME}` thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể kết nối tới MySQL Server: {e}")
        sys.exit(1)

    # 2. Tạo toàn bộ bảng theo SQLAlchemy Models
    print("[2/3] Đang tạo các bảng dữ liệu...")
    Base.metadata.create_all(bind=engine)
    print("      -> Đã tạo tất cả các bảng thành công!")

    # 3. Nạp dữ liệu mẫu
    print("[3/3] Đang kiểm tra và nạp dữ liệu mẫu (Users, Tours, Guides, Departures, Feedbacks)...")
    db = SessionLocal()
    try:
        init_db(db)
        print("      -> Đã hoàn tất nạp dữ liệu mẫu!")
    finally:
        db.close()

    print("=" * 60)
    print("  HOÀN TẤT THIẾT LẬP MYSQL THÀNH CÔNG!")
    print("  Bạn có thể khởi động hệ thống bằng file start.bat")
    print("=" * 60)

if __name__ == "__main__":
    main()
