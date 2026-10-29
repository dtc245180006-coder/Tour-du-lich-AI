from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.seed_data import init_db
from backend.app.routers import (
    auth_router,
    tour_router,
    departure_router,
    booking_router,
    payment_router,
    guide_router,
    feedback_router,
    stats_router,
    ai_router,
    user_router
)

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    try:
        from backend.app.database import SessionLocal
        from backend.app.seed_data import ensure_fresh_departures
        db = SessionLocal()
        try:
            ensure_fresh_departures(db)
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning('Lỗi tự động cập nhật ngày khởi hành: %s', e)
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống Quản lý Tour Du lịch kết hợp Trợ lý Trí tuệ Nhân tạo (VietJourney AI Hub)"
)

@app.get('/api/v1/app-config', include_in_schema=False)
def public_app_config():
    import os
    return {'demo_mode': os.getenv('APP_ENV', 'development') != 'production'}

@app.exception_handler(IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={'detail': 'Dữ liệu bị trùng hoặc đang được tham chiếu. Vui lòng tải lại và kiểm tra.'})

@app.exception_handler(OperationalError)
async def database_busy(request, exc):
    return JSONResponse(status_code=503, content={'detail': 'Cơ sở dữ liệu đang bận hoặc chưa sẵn sàng. Vui lòng thử lại.'})

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def disable_cache_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path in PAGE_ROUTES or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Đăng ký các Router API
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(user_router.router, prefix=settings.API_V1_STR)
app.include_router(tour_router.router, prefix=settings.API_V1_STR)
app.include_router(departure_router.router, prefix=settings.API_V1_STR)
app.include_router(booking_router.router, prefix=settings.API_V1_STR)
app.include_router(payment_router.router, prefix=settings.API_V1_STR)
app.include_router(guide_router.router, prefix=settings.API_V1_STR)
app.include_router(feedback_router.router, prefix=settings.API_V1_STR)
app.include_router(stats_router.router, prefix=settings.API_V1_STR)
app.include_router(ai_router.router, prefix=settings.API_V1_STR)

# Cung cấp Static files của frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

PAGE_ROUTES = [
    "/",
    "/home",
    "/login",
    "/ai",
    "/queue",
    "/tours",
    "/departures",
    "/bookings",
    "/payments",
    "/guides",
    "/feedbacks",
    "/analytics",
    "/users",
    "/sdlc"
]

def _serve_page(page_name: str = "home"):
    clean_name = page_name.strip("/").lower()
    if clean_name.endswith(".html"):
        clean_name = clean_name[:-5]
    if not clean_name:
        clean_name = "home"

    if clean_name not in {"index", *[route.strip("/") for route in PAGE_ROUTES]}:
        raise HTTPException(status_code=404, detail="Page Not Found")
    page_file = FRONTEND_DIR / f"{clean_name}.html"
    if page_file.exists():
        return FileResponse(page_file)
    
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
        
    return {"message": "VietJourney Tour Management API is running. Visit /docs for Swagger documentation."}

def _make_page_handler(p_name: str):
    def handler():
        return _serve_page(p_name)
    return handler

# Đăng ký route riêng cho từng trang hiển thị ngữ nghĩa
for route_path in PAGE_ROUTES:
    page_key = route_path.strip("/") or "home"
    app.add_api_route(route_path, _make_page_handler(page_key), methods=["GET"], include_in_schema=False)

# Route bắt giữ (catch-all) hỗ trợ mở trực tiếp file HTML hoặc route URL
@app.get("/{full_path:path}", include_in_schema=False)
def catch_all_frontend_pages(full_path: str):
    # Bỏ qua các endpoint API và Swagger
    if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
        raise HTTPException(status_code=404, detail="Resource Not Found")
    
    # Kiểm tra xem có phải file tĩnh trực tiếp (css, js, html...)
    direct_file = (FRONTEND_DIR / full_path).resolve()
    if not direct_file.is_relative_to(FRONTEND_DIR.resolve()):
        raise HTTPException(status_code=404, detail="Resource Not Found")
    if direct_file.is_file():
        return FileResponse(direct_file)

    return _serve_page(full_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
