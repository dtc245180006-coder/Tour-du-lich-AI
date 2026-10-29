"""
Script sao chép toàn bộ dữ liệu từ MySQL sang SQLite (tour_management.db)
Cách chạy:
    python scripts/migrate_mysql_to_sqlite.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from backend.app.config import settings
from backend.app import models
from backend.app.database import Base

def migrate():
    sqlite_path = BASE_DIR / "tour_management.db"
    
    print("=" * 65)
    print("  ĐỒNG BỘ DỮ LIỆU TỪ MYSQL SANG SQLITE - VIETJOURNEY AI")
    print("=" * 65)

    # 1. Kết nối MySQL
    mysql_url = settings.DATABASE_URL
    if "mysql" not in mysql_url.lower():
        encoded_pw = quote_plus(settings.DB_PASSWORD)
        mysql_url = f"mysql+pymysql://{settings.DB_USER}:{encoded_pw}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

    try:
        mysql_engine = create_engine(mysql_url, pool_pre_ping=True)
        MysqlSession = sessionmaker(bind=mysql_engine)
        mysql_db = MysqlSession()
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể kết nối tới MySQL ({e}). Bỏ qua bước đồng bộ từ MySQL.")
        return

    # 2. Kết nối SQLite và đảm bảo bảng đã được tạo
    sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=sqlite_engine)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SqliteSession()

    order_of_models = [
        ("Users", models.User),
        ("Tour Guides", models.TourGuide),
        ("Tours", models.Tour),
        ("Departures", models.Departure),
        ("Customers", models.Customer),
        ("Bookings", models.Booking),
        ("Payments", models.Payment),
        ("Feedbacks", models.Feedback),
        ("AI Session Logs", models.AISessionLog),
    ]

    try:
        for name, model_cls in order_of_models:
            src_records = mysql_db.query(model_cls).all()
            if not src_records:
                print(f"[-] {name:15}: Không có bản ghi nào trong MySQL.")
                continue

            migrated_count = 0
            for item in src_records:
                existing = sqlite_db.query(model_cls).filter(model_cls.id == item.id).first()
                data = {c.name: getattr(item, c.name) for c in model_cls.__table__.columns}
                if existing:
                    for k, v in data.items():
                        setattr(existing, k, v)
                else:
                    new_obj = model_cls(**data)
                    sqlite_db.add(new_obj)
                    migrated_count += 1

            sqlite_db.commit()
            print(f"[+] {name:15}: Đã nạp/cập nhật {len(src_records)} bản ghi (mới thêm {migrated_count}).")

        print("=" * 65)
        print("  ĐỒNG BỘ DỮ LIỆU MYSQL -> SQLITE HOÀN TẤT THÀNH CÔNG!")
        print("=" * 65)
    except Exception as e:
        sqlite_db.rollback()
        print(f"[LỖI] Trong quá trình đồng bộ: {e}")
    finally:
        mysql_db.close()
        sqlite_db.close()

if __name__ == "__main__":
    migrate()
