import json
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app import models, schemas, ai_service

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    today = date.today()
    
    # 1. Tour Biển còn chỗ
    tour_bien = models.Tour(
        code="TOUR-BIEN-01",
        title="Tour Biển Nha Trang Cát Trắng",
        destination="Nha Trang",
        category="BIEN_DAO",
        duration_days=3,
        duration_nights=2,
        base_price=3500000,
        highlights="Tắm biển, lặn san hô, hải sản tươi sống"
    )
    # 2. Tour Núi còn chỗ
    tour_nui = models.Tour(
        code="TOUR-NUI-02",
        title="Tour Sa Pa Săn Mây Fansipan",
        destination="Sa Pa",
        category="TAY_BAC",
        duration_days=3,
        duration_nights=2,
        base_price=3200000,
        highlights="Chinh phục Fansipan, ngắm ruộng bậc thang"
    )
    # 3. Tour Biển ĐÃ HẾT CHỖ (available_slots = 0)
    tour_full = models.Tour(
        code="TOUR-FULL-03",
        title="Tour Phú Quốc Cao Cấp (Đã Kín)",
        destination="Phú Quốc",
        category="BIEN_DAO",
        duration_days=4,
        duration_nights=3,
        base_price=6000000
    )
    session.add_all([tour_bien, tour_nui, tour_full])
    session.commit()
    
    # Lịch khởi hành
    dep_bien = models.Departure(
        tour_id=tour_bien.id,
        departure_date=today + timedelta(days=5),
        return_date=today + timedelta(days=8),
        total_slots=20,
        available_slots=10,
        status="OPEN"
    )
    dep_nui = models.Departure(
        tour_id=tour_nui.id,
        departure_date=today + timedelta(days=7),
        return_date=today + timedelta(days=10),
        total_slots=20,
        available_slots=8,
        status="OPEN"
    )
    dep_full = models.Departure(
        tour_id=tour_full.id,
        departure_date=today + timedelta(days=4),
        return_date=today + timedelta(days=8),
        total_slots=15,
        available_slots=0, # HẾT CHỖ
        status="FULL"
    )
    session.add_all([dep_bien, dep_nui, dep_full])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def mock_ai_api_calls(monkeypatch):
    """Giả lập phản hồi Gemini API trong môi trường unit test để kiểm tra logic mà không tốn quota/phụ thuộc mạng"""
    def fake_gemini(system_prompt, prompt):
        p_str = str(prompt).lower()
        if "đà lạt" in p_str or "itinerary_summary" in str(system_prompt).lower():
            return json.dumps({
                "description": "Khám phá Đà Lạt ngàn hoa với không khí trong lành.",
                "itinerary_summary": "Ngày 1: Khám phá Cầu Đất. Ngày 2: Thác Datanla. Ngày 3: Vườn dâu tây.",
                "marketing_slogan": "Đà Lạt - Nơi tình yêu bắt đầu trọn vẹn từng khoảnh khắc.",
                "packing_tips": "Nên mang theo áo khoác ấm, kem chống nắng và giày thể thao êm ái."
            })
        elif "positive_highlights" in p_str or "toàn bộ dữ liệu" in p_str:
            return json.dumps({
                "positive_highlights": ["Khách khen đồ ăn ngon và hướng dẫn viên chu đáo nhiệt tình."],
                "improvement_areas": ["Xe di chuyển hơi xóc cần kiểm tra lại lộ trình."],
                "guide_performance_summary": "Hướng dẫn viên được đánh giá rất tốt và tận tâm.",
                "executive_recommendation": "Tiếp tục duy trì chất lượng phục vụ và bảo dưỡng xe định kỳ."
            })
        elif "200k" in p_str or "200.000" in p_str:
            return "Với ngân sách 200.000 VNĐ cho 5 ngày, hệ thống hiện chưa có tour trọn gói phù hợp. Quý khách có thể tham khảo thêm các gói hỗ trợ khác."
        else:
            return json.dumps({
                "advice_text": "Dựa trên ngân sách 5 triệu và sở thích biển, VietJourney gợi ý cho bạn tour biển Nha Trang 3 ngày 2 đêm.",
                "ranked_tour_ids": [1],
                "recommended_tours": [
                    {
                        "tour_id": 1,
                        "departure_id": 1,
                        "code": "TOUR-BIEN-01",
                        "match_reason": "Tour biển 3 ngày còn 10 chỗ trống, giá trọn gói 3.500.000 VNĐ phù hợp ngân sách."
                    }
                ]
            })
    
    from backend.app import ai_service
    monkeypatch.setattr(ai_service, "call_gemini_api", fake_gemini)
    monkeypatch.setattr(ai_service, "call_openai_api", fake_gemini)


def test_ai_consultation_only_suggests_available_tours(db):
    """
    Kiểm tra RÀNG BUỘC CHỐNG ẢO GIÁC (Grounding constraint):
    AI CHỈ gợi ý tour CÒN CHỖ. Tuyệt đối không gợi ý tour đã FULL (TOUR-FULL-03).
    """
    req = schemas.AIConsultRequest(
        query="Tôi muốn đi tour biển 3 ngày, ngân sách 5 triệu, thích tắm biển và hải sản",
        budget=5000000,
        days=3
    )
    res = ai_service.consult_tour_ai(db, req)
    
    assert len(res.recommended_tours) > 0
    recommended_codes = [t.code for t in res.recommended_tours]
    
    # Phải có TOUR-BIEN-01 vì còn 10 chỗ và hợp tiêu chí
    assert "TOUR-BIEN-01" in recommended_codes
    
    # TUYỆT ĐỐI KHÔNG ĐƯỢC có TOUR-FULL-03 vì đã hết chỗ
    assert "TOUR-FULL-03" not in recommended_codes
    
    # Tất cả tour được gợi ý phải có available_slots > 0
    for t in res.recommended_tours:
        assert t.available_slots > 0
        assert t.price > 0

def test_ai_consultation_handles_impossible_request(db):
    """
    Kiểm tra xử lý yêu cầu phi thực tế / không có tour nào thỏa mãn:
    (Ngân sách chỉ 200.000 VNĐ nhưng muốn đi 5 ngày)
    AI không được tự bịa tour giá 200.000 VNĐ!
    """
    req = schemas.AIConsultRequest(
        query="Tôi chỉ có 200k và muốn đi 5 ngày",
        budget=200000,
        days=5
    )
    res = ai_service.consult_tour_ai(db, req)
    # AI phải đưa ra phản hồi rõ ràng hoặc gợi ý các tour có sẵn cùng giải thích
    assert res.advice_text is not None
    assert len(res.advice_text) > 20

def test_ai_generate_description():
    """Kiểm tra AI sinh mô tả tour và tóm tắt lịch trình"""
    req = schemas.AIDescriptionRequest(
        tour_title="Khám phá Đà Lạt Mộng Mơ",
        destination="Đà Lạt",
        duration_days=3,
        duration_nights=2,
        highlights="Săn mây Cầu Đất, Thác Datanla, Vườn dâu tây"
    )
    res = ai_service.generate_tour_description_ai(req)
    assert "Đà Lạt" in res.description
    assert "Ngày 1" in res.itinerary_summary
    assert "Ngày 2" in res.itinerary_summary
    assert "Ngày 3" in res.itinerary_summary
    assert len(res.marketing_slogan) > 10
    assert len(res.packing_tips) > 10

def test_ai_summarize_feedback(db):
    """Kiểm tra AI tóm tắt phản hồi của khách và tính chỉ số cảm xúc"""
    tour = db.query(models.Tour).first()
    
    # Tạo feedback mẫu
    fb1 = models.Feedback(
        tour_id=tour.id,
        customer_name="Nguyễn Văn A",
        rating=5,
        comments="Chuyến đi rất vui, hướng dẫn viên chu đáo và nhiệt tình!",
        guide_rating=5,
        sentiment="POSITIVE"
    )
    fb2 = models.Feedback(
        tour_id=tour.id,
        customer_name="Trần Thị B",
        rating=4,
        comments="Cảnh đẹp đồ ăn ngon, tuy nhiên xe đi hơi xóc.",
        guide_rating=4,
        sentiment="POSITIVE"
    )
    db.add_all([fb1, fb2])
    db.commit()
    
    req = schemas.AIFeedbackSummaryRequest(tour_id=tour.id)
    res = ai_service.summarize_feedback_ai(db, req)
    
    assert res.total_feedbacks == 2
    assert res.average_rating == 4.5
    assert res.sentiment_breakdown["POSITIVE"] == 2
    assert len(res.positive_highlights) > 0
    assert len(res.guide_performance_summary) > 0

def test_ai_status_and_configuration():
    """Kiểm tra API kiểm tra trạng thái và thiết lập AI Key (Chỉ dành cho ADMIN)"""
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app import auth, models
    client = TestClient(app)
    
    # 1. Kiểm tra status khi chưa đăng nhập (khách vãng lai): masked_key phải là None
    res = client.get("/api/v1/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_gemini_active" in data
    assert "active_engine" in data
    assert "model_name" in data
    assert data.get("masked_key") is None  # Khách không nhìn thấy key
    
    # 2. Người chưa đăng nhập gọi configure-key -> phải bị từ chối 401
    unauth_res = client.post("/api/v1/ai/configure-key", json={"api_key": ""})
    assert unauth_res.status_code in (401, 403)

    # 3. User không phải ADMIN (ví dụ CONSULTANT 'tuvan') gọi configure-key -> phải bị từ chối 403
    tuvan_token = auth.create_access_token(data={"sub": "tuvan", "role": "CONSULTANT"})
    forbidden_res = client.post(
        "/api/v1/ai/configure-key",
        headers={"Authorization": f"Bearer {tuvan_token}"},
        json={"api_key": ""}
    )
    assert forbidden_res.status_code == 403

    # 4. ADMIN gọi status -> masked_key có thể hiển thị
    admin_token = auth.create_access_token(data={"sub": "admin", "role": "ADMIN"})
    admin_status = client.get(
        "/api/v1/ai/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_status.status_code == 200

    # 5. ADMIN Reset về Local
    res_reset = client.post(
        "/api/v1/ai/configure-key",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"api_key": ""}
    )
    assert res_reset.status_code == 200
    reset_data = res_reset.json()
    assert reset_data["success"] is True
    assert reset_data["is_gemini_active"] is False

def test_extract_json_from_llm():
    """Kiểm tra độ bền vững khi bóc tách JSON từ phản hồi LLM"""
    from backend.app.ai_service import _extract_json_from_llm
    
    # 1. Khối markdown chuẩn ```json ... ```
    raw_1 = "```json\n{\"description\": \"Tour tuyệt vời\", \"slogan\": \"Đi để trải nghiệm\"}\n```"
    parsed_1 = _extract_json_from_llm(raw_1)
    assert parsed_1 is not None
    assert parsed_1["description"] == "Tour tuyệt vời"
    
    # 2. Markdown kèm lời chào của LLM
    raw_2 = "Dưới đây là kết quả của bạn:\n```json\n{\"key\": 123}\n```\nChúc bạn ngày tốt lành!"
    parsed_2 = _extract_json_from_llm(raw_2)
    assert parsed_2 is not None
    assert parsed_2["key"] == 123
    
    # 3. Chuỗi JSON thuần
    raw_3 = '{"status": "ok"}'
    parsed_3 = _extract_json_from_llm(raw_3)
    assert parsed_3 is not None
    assert parsed_3["status"] == "ok"
