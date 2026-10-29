import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.config import settings, reload_ai_settings, BASE_DIR
from typing import Optional
from backend.app import schemas, ai_service, auth, models

router = APIRouter(prefix="/ai", tags=["Trung tâm Trí tuệ Nhân tạo (AI Assistant)"])

def _update_env_file(key: str, value: str):
    """Cập nhật hoặc thêm biến cấu hình vào file .env ở thư mục gốc"""
    if "\n" in value or "\r" in value:
        raise HTTPException(status_code=422, detail="Giá trị cấu hình không được xuống dòng.")
    env_file = BASE_DIR / ".env"
    lines = []
    found = False
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{key}={value}\n")
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

def get_available_gemini_models(api_key: str) -> list[str]:
    """Truy vấn danh sách model được cấp phép trực tiếp từ Google API theo Key"""
    models_found = []
    
    # 1. Thử qua google.genai với v1beta và v1
    for ver in ["v1beta", "v1"]:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version=ver, timeout=6000))
            for m in client.models.list():
                actions = getattr(m, "supported_actions", None) or []
                if not actions or "generateContent" in actions:
                    name = (m.name or "").removeprefix("models/")
                    if name and name not in models_found:
                        models_found.append(name)
            if models_found:
                return models_found
        except Exception:
            pass

    # 2. Thử qua google.generativeai
    try:
        import google.generativeai as gai
        gai.configure(api_key=api_key)
        for m in gai.list_models():
            methods = getattr(m, "supported_generation_methods", None) or []
            if not methods or "generateContent" in methods:
                name = (m.name or "").removeprefix("models/")
                if name and name not in models_found:
                    models_found.append(name)
        if models_found:
            return models_found
    except Exception:
        pass

    # 3. Thử qua HTTP REST trực tiếp
    try:
        import httpx
        for ver in ["v1beta", "v1"]:
            url = f"https://generativelanguage.googleapis.com/{ver}/models"
            resp = httpx.get(url, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"}, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("models", []):
                    methods = m.get("supportedGenerationMethods", [])
                    if not methods or "generateContent" in methods:
                        name = m.get("name", "").removeprefix("models/")
                        if name and name not in models_found:
                            models_found.append(name)
                if models_found:
                    return models_found
    except Exception:
        pass

    return models_found

def test_gemini_model_call(api_key: str, model_name: str) -> Optional[str]:
    """Kiểm tra gọi thử sinh nội dung qua nhiều giao thức (google.genai, httpx REST)"""
    if not api_key or len(api_key) < 15:
        return None
        
    test_prompt = "Chào bạn, hãy phản hồi ngắn gọn 'OK' để xác nhận kết nối thành công."
    
    # 1. Thử google.genai với v1beta
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1beta", timeout=6000))
        res = client.models.generate_content(model=model_name, contents=test_prompt)
        if res and res.text:
            return res.text.strip()
    except Exception:
        pass

    # 2. Thử HTTP REST trực tiếp
    try:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": test_prompt}]}]}
        res = httpx.post(url, headers=headers, json=body, timeout=6.0)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"].strip()
    except Exception:
        pass

    return None

@router.get("/status", response_model=schemas.AIStatusResponse)
def get_ai_status(current_user: Optional[models.User] = Depends(auth.get_optional_current_user)):
    """Kiểm tra trạng thái động cơ AI hiện tại (Google Gemini Cloud hay Local Engine).
    Chỉ Quản trị viên (Admin) mới có thể xem masked_key.
    """
    reload_ai_settings()
    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip()
    is_active = bool(api_key and len(api_key) >= 15)
    
    # Chỉ Admin mới xem được masked key
    is_admin = bool(current_user and current_user.role == "ADMIN")
    masked = None
    if is_active and is_admin:
        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) >= 10 else "******"
    
    model_name = settings.DEFAULT_AI_MODEL or "gemini-3.1-flash-lite"
    return schemas.AIStatusResponse(
        is_gemini_active=is_active,
        masked_key=masked,
        active_engine=f"Google Gemini ({model_name}) Cloud AI" if is_active else "Google Gemini Cloud AI (Chưa kích hoạt)",
        model_name=model_name,
        mode="cloud" if is_active else "inactive",
        description="Đang kết nối trực tiếp với Google Gemini Cloud AI" if is_active else "Chưa nhập API Key. Vui lòng cấu hình Google Gemini API Key để kích hoạt trợ lý AI."
    )

@router.get("/models")
def get_models_list(current_user: models.User = Depends(auth.require_roles(["ADMIN"]))):
    """Lấy danh sách các mô hình khả dụng theo API Key hiện tại (Dành riêng cho ADMIN)"""
    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        return {"models": ["gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]}
    discovered = get_available_gemini_models(api_key)
    return {"models": discovered or ["gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]}

@router.post("/configure-key")
def configure_gemini_key(
    req: schemas.AIConfigureKeyRequest,
    current_user: models.User = Depends(auth.require_roles(["ADMIN"]))
):
    """Thiết lập hoặc cập nhật Google Gemini API Key.
    BẢO MẬT: Chỉ tài khoản có vai trò ADMIN mới được phép thực hiện!
    """
    key = req.api_key.strip().strip('"').strip("'")
    
    # Nếu xóa key (trống)
    if not key:
        settings.GEMINI_API_KEY = ""
        os.environ["GEMINI_API_KEY"] = ""
        _update_env_file("GEMINI_API_KEY", "")
        return {
            "success": True,
            "message": "Đã xóa Google Gemini API Key. Trợ lý AI đang ở trạng thái chưa kích hoạt.",
            "is_gemini_active": False,
            "active_engine": "Google Gemini Cloud AI (Chưa kích hoạt)"
        }

    # 1. Tự động truy vấn các model khả dụng cho API Key này
    discovered_models = get_available_gemini_models(key)
    
    requested_model = req.model_name or settings.DEFAULT_AI_MODEL or "gemini-3.1-flash-lite"
    candidate_models = []
    if requested_model:
        candidate_models.append(requested_model)
    if discovered_models:
        flash_models = [m for m in discovered_models if "flash" in m.lower()]
        other_models = [m for m in discovered_models if "flash" not in m.lower()]
        candidate_models.extend(flash_models + other_models)
    
    # Bổ sung các model phổ thông dự phòng
    fallback_defaults = [
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-flash-latest"
    ]
    candidate_models.extend(fallback_defaults)
    candidate_models = list(dict.fromkeys(candidate_models))

    
    test_res_text = None
    used_model = requested_model
    
    for m in candidate_models:
        reply = test_gemini_model_call(key, m)
        if reply:
            test_res_text = reply
            used_model = m
            break

    if not test_res_text:
        return {
            "success": False,
            "message": f"Không thể kích hoạt với các mô hình thử nghiệm {candidate_models[:3]}. Vui lòng kiểm tra lại tính hợp lệ của API Key từ Google AI Studio (https://aistudio.google.com/app/apikey).",
            "is_gemini_active": False
        }
        
    # Cập nhật thành công
    settings.GEMINI_API_KEY = key
    settings.DEFAULT_AI_MODEL = used_model
    os.environ["GEMINI_API_KEY"] = key
    _update_env_file("GEMINI_API_KEY", key)
    _update_env_file("DEFAULT_AI_MODEL", used_model)
    
    return {
        "success": True,
        "message": f"Kết nối Google Gemini thành công! Đã tự động kích hoạt mô hình {used_model}.",
        "is_gemini_active": True,
        "active_engine": f"Google Gemini ({used_model})",
        "model_name": used_model,
        "available_models": discovered_models,
        "test_reply": test_res_text
    }


@router.post("/consult", response_model=schemas.AIConsultResponse)
def consult_tour(request: schemas.AIConsultRequest, db: Session = Depends(get_db)):
    """
    1. AI Tư vấn tour theo ngân sách, thời gian, sở thích:
    - Bắt buộc grounding theo các tour còn chỗ thực tế trong DB.
    - Không bịa giá, không bịa ngày khởi hành.
    """
    return ai_service.consult_tour_ai(db, request)

@router.post("/generate-description", response_model=schemas.AIDescriptionResponse)
def generate_tour_description(request: schemas.AIDescriptionRequest, current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"]))):
    """
    2. AI Sinh mô tả tour và lịch trình tóm tắt theo từng ngày:
    - Giúp nhân viên tiết kiệm thời gian soạn thảo nội dung bán tour.
    """
    return ai_service.generate_tour_description_ai(request)

@router.post("/summarize-feedback", response_model=schemas.AIFeedbackSummaryResponse)
def summarize_feedback(request: schemas.AIFeedbackSummaryRequest, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_roles(["ADMIN", "CONSULTANT"]))):
    """
    3. AI Tóm tắt phản hồi khách hàng:
    - Phân tích cảm xúc, khen/chê, đánh giá HDV và đề xuất hành động.
    """
    return ai_service.summarize_feedback_ai(db, request)
