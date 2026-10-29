from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

def _ensure_mysql_db_exists():
    """Tự động kiểm tra và tạo database trên MySQL Server nếu chưa tồn tại"""
    if settings.DB_TYPE != "mysql" and "mysql" not in settings.DATABASE_URL.lower():
        return
    try:
        import pymysql
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset="utf8mb4"
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        print(f"[DATABASE] Da ket noi va dam bao database MySQL '{settings.DB_NAME}' san sang.")
    except Exception as e:
        print(f"[DATABASE WARNING] Khong the tu dong kiem tra/tao CSDL MySQL: {e}")

# Tự động chuẩn bị database MySQL nếu dùng MySQL
# Database creation is an explicit administrative operation.

# Cấu hình engine kết nối tối ưu cho cả SQLite và MySQL
db_url = settings.DATABASE_URL
if "sqlite" in db_url.lower():
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    # Cấu hình Connection Pool cho MySQL để tránh timeout và tối ưu tải
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency cung cấp session CSDL cho từng request và tự động đóng sau khi hoàn tất"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

