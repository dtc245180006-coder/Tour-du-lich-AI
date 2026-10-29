import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Tải file .env nếu có
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

def _secret_key():
    supplied = os.getenv("SECRET_KEY", "").strip()
    if supplied and supplied != "tour_dulich_ai_secret_key_super_secure_2026":
        if len(supplied) < 32:
            raise RuntimeError("SECRET_KEY phải có ít nhất 32 ký tự ngẫu nhiên.")
        return supplied
    if os.getenv("APP_ENV", "development") == "production":
        raise RuntimeError("Cần cấu hình SECRET_KEY riêng cho production.")
    # Keep development sessions valid across reloads and workers.
    path = BASE_DIR / ".jwt_secret"
    try:
        with path.open("x", encoding="ascii") as file:
            file.write(secrets.token_urlsafe(48))
    except FileExistsError:
        pass
    return path.read_text(encoding="ascii").strip()

class Settings:
    PROJECT_NAME: str = "Hệ thống Quản lý Tour Du lịch AI - VietJourney"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Secret key cho JWT Token
    SECRET_KEY: str = _secret_key()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 giờ
    
    # Cấu hình Cơ sở dữ liệu: Hỗ trợ linh hoạt chuyển đổi giữa SQLite và MySQL
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").strip().lower()
    DB_HOST: str = os.getenv("DB_HOST", "localhost").strip()
    DB_PORT: int = int(os.getenv("DB_PORT", "3306").strip() or 3306)
    DB_USER: str = os.getenv("DB_USER", "root").strip()
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "").strip()
    DB_NAME: str = os.getenv("DB_NAME", "tour_management").strip()

    DB_PATH: Path = BASE_DIR / "tour_management.db"

    @property
    def DATABASE_URL(self) -> str:
        """Trả về connection string SQLAlchemy phù hợp theo cấu hình môi trường"""
        explicit_url = os.getenv("DATABASE_URL", "").strip()
        if explicit_url:
            return explicit_url
        if self.DB_TYPE == "mysql":
            from urllib.parse import quote_plus
            encoded_password = quote_plus(self.DB_PASSWORD)
            return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        return f"sqlite:///{self.DB_PATH.as_posix()}"
    
    # Cấu hình AI Engine
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "gemini-3.1-flash-lite")
    # Cấu hình SMTP Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587").strip() or 587)
    SMTP_USER: str = os.getenv("SMTP_USER", "").strip()
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "").strip()
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "VietJourney Lữ Hành Thông Minh").strip()
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "").strip()
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000").strip().rstrip("/")

settings = Settings()

def reload_ai_settings():
    """Tải lại biến môi trường từ .env để cập nhật API Key mới nhất mà không cần khởi động lại server"""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    settings.DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "gemini-3.1-flash-lite").strip() or "gemini-3.1-flash-lite"
    return settings

