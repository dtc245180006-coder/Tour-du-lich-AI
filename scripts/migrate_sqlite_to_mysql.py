"""
Script sao chép toàn bộ dữ liệu từ SQLite (tour_management.db) sang MySQL
Cách chạy:
    python scripts/migrate_sqlite_to_mysql.py
"""
import sys
from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Đảm bảo in tiếng Việt có dấu an toàn trên Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings
from backend.app import models
from backend.app.database import Base

def migrate():
    sqlite_path = BASE_DIR / "tour_management.db"
    if not sqlite_path.exists():
        print(f"[THÔNG BÁO] Không tìm thấy file SQLite tại {sqlite_path}.")
        return

    print("=" * 65)
    print("  CHUYỂN DỮ LIỆU TỪ SQLITE SANG MYSQL - VIETJOURNEY AI")
    print("=" * 65)

    # 1. Kết nối SQLite
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SqliteSession()

    # 2. Kết nối MySQL
    mysql_url = settings.DATABASE_URL
    if "mysql" not in mysql_url.lower():
        from urllib.parse import quote_plus
        encoded_pw = quote_plus(settings.DB_PASSWORD)
        mysql_url = f"mysql+pymysql://{settings.DB_USER}:{encoded_pw}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

    mysql_engine = create_engine(mysql_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=mysql_engine)
    MysqlSession = sessionmaker(bind=mysql_engine)
    mysql_db = MysqlSession()

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
            src_records = sqlite_db.query(model_cls).all()
            if not src_records:
                print(f"[-] {name:15}: Không có bản ghi nào trong SQLite.")
                continue

            migrated_count = 0
            for item in src_records:
                # Kiểm tra bản ghi đã tồn tại chưa theo ID
                existing = mysql_db.query(model_cls).filter(model_cls.id == item.id).first()
                if not existing:
                    # Trích xuất toàn bộ column data
                    data = {c.name: getattr(item, c.name) for c in model_cls.__table__.columns}
                    new_obj = model_cls(**data)
                    mysql_db.add(new_obj)
                    migrated_count += 1
            
            mysql_db.commit()
            print(f"[+] {name:15}: Đã đồng bộ {migrated_count}/{len(src_records)} bản ghi.")

        print("=" * 65)
        print("  ĐỒNG BỘ DỮ LIỆU SQLITE -> MYSQL HOÀN TẤT!")
        print("=" * 65)
    except Exception as e:
        mysql_db.rollback()
        print(f"[LỖI] Trong quá trình đồng bộ: {e}")
    finally:
        sqlite_db.close()
        mysql_db.close()

if __name__ == "__main__":
    migrate()
