import os
import json
import re
from datetime import date
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app import models, schemas
from backend.app.business_time import today as business_today

# ==================== PROMPT TEMPLATES ====================

SYSTEM_CONSULT_PROMPT = """Bạn là chuyên viên tư vấn tour du lịch thông minh, tận tâm của công ty lữ hành VietJourney.
QUY TẮC BẮT BUỘC:
1. Luôn đề xuất từ 1 đến 3 tour phù hợp nhất có trong danh sách CSDL được cung cấp dưới đây. Tuyệt đối không bịa tour ngoài danh sách.
2. Trình bày rõ ràng: Mã tour, tên tour, điểm đến, thời lượng (ngày đêm), mức giá niêm yết (VNĐ/khách) và ngày khởi hành khả dụng.
3. Nếu ngân sách khách hàng nêu chênh lệch nhẹ với giá tour, hãy phân tích và tư vấn khéo léo về giá trị trọn gói (vé tham quan, khách sạn, hướng dẫn viên, xe đưa đón).
4. Phản hồi thân thiện, nhiệt tình bằng định dạng Markdown rõ ràng, dễ nhìn.
5. Luôn nhắc khách hàng bấm 'Đặt ngay' ở thẻ tour bên dưới hoặc liên hệ tư vấn viên để giữ chỗ sớm.
"""

USER_CONSULT_TEMPLATE = """Yêu cầu của khách hàng:
- Thời gian mong muốn: {days_str}
- Ngân sách: {budget_str}
- Sở thích / Điểm đến mong muốn: {query}

Danh sách các tour đang MỞ BÁN và CÒN CHỖ THỰC TẾ trong hệ thống:
{available_tours_json}

Hãy phân tích và gợi ý tối đa 3 tour tốt nhất cho khách hàng trên.
BẮT BUỘC trả về định dạng JSON gồm 2 trường:
1. "advice_text": Toàn bộ bài tư vấn nhiệt tình, phân tích chi tiết vì sao các tour này phù hợp với khách, điểm nổi bật, giá trị trọn gói và hướng dẫn đặt chỗ (định dạng Markdown phong phú).
2. "ranked_tour_ids": Mảng danh sách id số nguyên của tối đa 3 tour được chọn từ danh sách trên (ví dụ: [1, 2]).
"""

SYSTEM_DESC_PROMPT = """Bạn là chuyên gia tiếp thị du lịch và điều hành tour lữ hành (Tour Operations Specialist) quốc tế và nội địa hàng đầu.
Nhiệm vụ của bạn là xây dựng nội dung bài viết giới thiệu tour truyền cảm hứng sâu sắc và thiết kế LỊCH TRÌNH CHI TIẾT TỪNG NGÀY chuyên nghiệp, chuẩn xác và bám sát thực tế theo đúng ĐIỂM ĐẾN được yêu cầu.

QUY TẮC BẮT BUỘC:
1. ĐIỂM ĐẾN LÀ TRỌNG TÂM TUYỆT ĐỐI:
   - Bạn PHẢI viết bài giới thiệu và thiết kế toàn bộ lịch trình 100% bám sát vào ĐIỂM ĐẾN và TÊN TOUR được yêu cầu.
   - Nếu điểm đến là Quốc tế (như Nước Mỹ, Hoa Kỳ, Châu Âu, Nhật Bản, Hàn Quốc, Thái Lan, Úc, Singapore...): Toàn bộ các địa danh, thành phố, điểm tham quan, hoạt động, trải nghiệm, ẩm thực PHẢI thuộc quốc gia đó (ví dụ nếu là Nước Mỹ: New York, Washington D.C., Los Angeles, Las Vegas, Tượng Nữ Thần Tự Do, Quảng Trường Thời Đại, Cầu Cổng Vàng...; nếu là Nhật Bản: Tokyo, Núi Phú Sĩ, Kyoto...).
   - TUYỆT ĐỐI KHÔNG ĐƯỢC nhầm lẫn hoặc sinh nội dung của Côn Đảo hay bất kỳ địa phương nào khác nếu điểm đến không phải là Côn Đảo.
   - Nếu danh sách điểm nhấn (highlights) có nội dung mâu thuẫn hoặc không thuộc điểm đến (ví dụ: điểm đến là Nước Mỹ hay Đà Nẵng nhưng highlights lại chứa Côn Đảo, mộ Cô Sáu), BẮT BUỘC BỎ QUA các điểm nhấn sai lệch đó và tự động thay thế bằng các điểm tham quan nổi tiếng, đặc trưng nhất của chính điểm đến yêu cầu.
2. Lịch trình PHẢI CÓ ĐÚNG CHÍNH XÁC số ngày đã yêu cầu, từ Ngày 1 đến ngày cuối cùng (đầy đủ {duration_days} ngày). Tuyệt đối không được thừa hoặc thiếu ngày so với thời lượng đã khai báo.
3. Mỗi ngày PHẢI trình bày rõ ràng, chi tiết từng buổi theo mẫu:
   Ngày X: [Tiêu đề hành trình ngắn gọn bám sát địa danh]
   - Buổi sáng: [Hoạt động cụ thể / điểm tham quan / di chuyển / bữa sáng]
   - Buổi chiều: [Hoạt động trải nghiệm / điểm nhấn chính / bữa trưa]
   - Buổi tối: [Khám phá đêm / ẩm thực đặc sản / nghỉ ngơi]
4. Ngày 1: Đón khách tại điểm hẹn / sân bay, di chuyển/bay đến điểm đến và nhận phòng.
5. Ngày cuối: Mua sắm quà lưu niệm/đặc sản địa phương, làm thủ tục trả phòng và tiễn khách về điểm đón ban đầu. Không tự ý bịa các tỉnh thành đón khách cố định nếu không có trong yêu cầu.
"""

SYSTEM_FEEDBACK_PROMPT = """Bạn là Giám đốc Kiểm soát Chất lượng Dịch vụ Du lịch (QA & Customer Experience Director) của công ty lữ hành VietJourney.
Nhiệm vụ của bạn là đọc và phân tích CHÍNH XÁC, TRUNG THỰC 100% dựa trên DỮ LIỆU PHẢN HỒI THỰC TẾ của khách hàng được cung cấp dưới đây.

QUY TẮC BẮT BUỘC:
1. TRUNG THỰC VÀ BÁM SÁT 100% Ý KIẾN THẬT CỦA KHÁCH:
   - Toàn bộ nội dung phân tích (khen, chê, đánh giá hướng dẫn viên, đề xuất cải tiến) PHẢI bắt nguồn trực tiếp từ các câu nhận xét thực tế của khách hàng trong danh sách.
   - Tuyệt đối KHÔNG ĐƯỢC bịa đặt hoặc suy diễn các sự cố, địa danh hoặc lời khen không có trong phản hồi thực tế.
   - Hãy trích dẫn hoặc nêu rõ các bằng chứng từ nhận xét của khách (ví dụ: 'Khách hàng [Tên khách] đánh giá...', 'Du khách phản ánh về...').
2. 'positive_highlights': Danh sách chi tiết các điểm sáng dịch vụ được du khách khen ngợi (nêu dẫn chứng từ nhận xét thực tế).
3. 'improvement_areas': Danh sách chi tiết các điểm du khách phản ánh chưa hài lòng hoặc cần cải thiện (nêu rõ nguyên nhân từ nhận xét thực tế).
4. 'guide_performance_summary': Đánh giá trung thực về đội ngũ Hướng dẫn viên dựa trên điểm số và lời nhận xét thực tế của khách.
5. 'executive_recommendation': Bản đề xuất chiến lược chi tiết cho Ban Giám Đốc giải quyết trực diện những vấn đề khách vừa phản ánh:
   - Các hành động khắc phục ngay lập tức (Quick Wins).
   - Chiến lược nâng cao chỉ số hài lòng và chất lượng dịch vụ dài hạn."""


# ==================== EXTERNAL API CLIENTS ====================

def _extract_json_from_llm(text: str) -> Optional[Dict[str, Any]]:
    """Trích xuất đối tượng JSON từ kết quả phản hồi của LLM một cách an toàn và tự động phục hồi lỗi"""
    if not text:
        return None

    # 1. Trích xuất khối ứng viên JSON
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    candidate = match.group(1) if match else None

    if not candidate:
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidate = text[first_brace:last_brace + 1]
        else:
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            candidate = cleaned.strip()

    # 2. Parse thông thường với strict=False
    try:
        res = json.loads(candidate, strict=False)
        if isinstance(res, dict):
            return res
    except Exception:
        pass

    # 3. Thử sửa lỗi dấu phẩy thừa trước ngoặc đóng (trailing commas)
    try:
        no_trailing = re.sub(r',\s*([\]\}])', r'\1', candidate)
        res = json.loads(no_trailing, strict=False)
        if isinstance(res, dict):
            return res
    except Exception:
        pass

    # 4. Phục hồi qua Regex trường dữ liệu trọng yếu
    result = {}
    known_keys = [
        'marketing_slogan', 'description', 'itinerary_summary', 'packing_tips',
        'ranked_tour_ids', 'advice_text', 'positive_highlights',
        'improvement_areas', 'guide_performance_summary', 'executive_recommendation'
    ]
    for k in known_keys:
        m_str = re.search(rf'"{k}"\s*:\s*"((?:\\.|[^"\\])*)"', candidate, re.DOTALL)
        if m_str:
            result[k] = m_str.group(1).replace('\\"', '"').replace('\\n', '\n')
            continue
        m_obj = re.search(rf'"{k}"\s*:\s*(\[.*?\]|\{{.*?\}})', candidate, re.DOTALL)
        if m_obj:
            try:
                result[k] = json.loads(m_obj.group(1), strict=False)
            except Exception:
                result[k] = m_obj.group(1)

    return result if result else None


def call_gemini_api(system_instruction: str, prompt: str) -> Optional[str]:
    """Gọi Google Gemini API chính thức qua google-genai SDK hoặc HTTP REST endpoint"""
    from backend.app.config import reload_ai_settings
    reload_ai_settings()
    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
    
    if not api_key or len(api_key) < 15:
        return None
        
    preferred_model = getattr(settings, "DEFAULT_AI_MODEL", "gemini-3.1-flash-lite") or "gemini-3.1-flash-lite"
    candidate_models = [
        preferred_model,
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-flash-latest"
    ]
    candidate_models = list(dict.fromkeys(candidate_models))

    # 1. Thử gọi bằng google.genai SDK chính thức
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1beta", timeout=15000))
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3
        ) if system_instruction else None
        
        for m in candidate_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as inner_e:
                err_str = str(inner_e).lower()
                if "quota" in err_str or "resource_exhausted" in err_str or "429" in err_str:
                    print(f"[AI Service] Gemini quota exceeded (429): {inner_e}")
                    return None
                continue
    except Exception as e:
        print(f"[AI Service] google.genai client error: {e}")

    # 2. Fallback sang HTTP REST trực tiếp tới endpoint generativelanguage.googleapis.com
    try:
        import httpx
        for m in candidate_models[:3]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
            contents = [{"parts": [{"text": prompt}]}]
            body = {"contents": contents}
            if system_instruction:
                body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            try:
                res = httpx.post(url, headers=headers, json=body, timeout=15.0)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                elif res.status_code in (429, 403):
                    return None
            except Exception:
                continue
    except Exception:
        pass

    return None


def call_openai_api(system_instruction: str, prompt: str) -> Optional[str]:
    """Gọi OpenAI API dự phòng nếu có cấu hình API KEY"""
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        res = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20.0)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[AI Service] OpenAI API call error: {e}")
        return None


# ==================== MAIN AI FUNCTIONS ====================

def consult_tour_ai(db: Session, request: schemas.AIConsultRequest) -> schemas.AIConsultResponse:
    """
    Chức năng AI 1: Tư vấn tour theo ngân sách, thời gian, sở thích.
    - Hoạt động 100% bằng Google Gemini Cloud AI.
    - Grounding chặt chẽ theo các tour còn chỗ thực tế trong CSDL.
    - Không dùng bất kỳ chế độ giả lập / rule-based nội bộ nào.
    """
    today = business_today()
    open_departures = (
        db.query(models.Departure)
        .filter(models.Departure.status == "OPEN")
        .filter(models.Departure.available_slots > 0)
        .filter(models.Departure.departure_date >= today)
        .order_by(models.Departure.departure_date.asc(), models.Departure.id.asc())
        .all()
    )
    
    # Gom nhóm theo Tour
    available_tours_dict = {}
    for dep in open_departures:
        tour = dep.tour
        if not tour or not tour.is_active:
            continue
        if tour.id not in available_tours_dict:
            available_tours_dict[tour.id] = {
                "id": tour.id,
                "departure_id": dep.id,
                "code": tour.code,
                "title": tour.title,
                "destination": tour.destination,
                "category": tour.category,
                "duration_days": tour.duration_days,
                "duration_nights": tour.duration_nights,
                "price": dep.price_override if dep.price_override is not None else tour.base_price,
                "available_slots": dep.available_slots,
                "next_departure": dep.departure_date.strftime("%d/%m/%Y"),
                "highlights": tour.highlights or ""
            }
            
    available_tours = list(available_tours_dict.values())
    if not available_tours:
        return schemas.AIConsultResponse(
            advice_text=(
                "Chào bạn! Rất tiếc hiện tại hệ thống chưa có lịch khởi hành mở bán nào còn chỗ trống phù hợp. "
                "Bạn vui lòng quay lại sau hoặc liên hệ bộ phận tư vấn để được hỗ trợ mở thêm lịch khởi hành mới nhé!"
            ),
            recommended_tours=[],
            engine_used=f"Google Gemini ({settings.DEFAULT_AI_MODEL}) Cloud AI"
        )
        
    days_str = f"{request.days} ngày" if request.days else "Linh hoạt"
    budget_str = f"{request.budget:,.0f} VNĐ" if request.budget else "Linh hoạt"
    
    external_prompt = USER_CONSULT_TEMPLATE.format(
        days_str=days_str,
        budget_str=budget_str,
        query=request.query,
        available_tours_json=json.dumps(available_tours, ensure_ascii=False, indent=2)
    )
    
    external_res = call_gemini_api(SYSTEM_CONSULT_PROMPT, external_prompt) or call_openai_api(SYSTEM_CONSULT_PROMPT, external_prompt)
    if not external_res:
        raise HTTPException(
            status_code=503,
            detail="Hệ thống chỉ sử dụng mô hình Google Gemini Cloud AI chính thức. Hiện tại chưa cấu hình API Key hoặc không thể kết nối tới Google AI Studio. Vui lòng cấu hình API Key để tiếp tục."
        )
        
    parsed = _extract_json_from_llm(external_res)
    advice_text = ""
    ranked_ids = []
    if parsed and isinstance(parsed, dict):
        advice_text = str(parsed.get("advice_text", "")).strip()
        ids = parsed.get("ranked_tour_ids", [])
        if isinstance(ids, list):
            ranked_ids = [int(x) for x in ids if isinstance(x, (int, str)) and str(x).isdigit()]
            
    if not advice_text:
        advice_text = external_res.strip()
        advice_text = re.sub(r"^```(?:json)?\s*", "", advice_text)
        advice_text = re.sub(r"\s*```$", "", advice_text)
        
    # Tạo danh sách các tour gợi ý thực tế từ DB để hiển thị thẻ tương tác
    valid_map = {t["id"]: t for t in available_tours}
    code_map = {t["code"].lower(): t for t in available_tours}
    
    chosen_ids = []
    for tid in ranked_ids:
        if tid in valid_map and tid not in chosen_ids:
            chosen_ids.append(tid)
            
    if not chosen_ids:
        for code, t in code_map.items():
            if code in advice_text.lower() and t["id"] not in chosen_ids:
                chosen_ids.append(t["id"])
                if len(chosen_ids) >= 3:
                    break

    recommended_items: List[schemas.RecommendedTourItem] = []
    for tid in chosen_ids[:3]:
        t = valid_map[tid]
        recommended_items.append(schemas.RecommendedTourItem(
            tour_id=t["id"],
            departure_id=t.get("departure_id"),
            code=t["code"],
            title=t["title"],
            destination=t["destination"],
            duration=f"{t['duration_days']}N{t['duration_nights']}Đ",
            price=float(t["price"]),
            available_slots=t["available_slots"],
            next_departure_date=t.get("next_departure"),
            match_reason=f"Được Google Gemini tuyển chọn theo yêu cầu: {request.query[:50]}"
        ))
        
    return schemas.AIConsultResponse(
        advice_text=advice_text,
        recommended_tours=recommended_items,
        engine_used=f"Google Gemini ({settings.DEFAULT_AI_MODEL}) Cloud AI"
    )


def _sanitize_destination_and_highlights(title: str, destination: str, highlights: Optional[str] = None):
    """
    Chuẩn hóa và đồng bộ Điểm đến & Điểm nhấn.
    Khắc phục triệt để lỗi khi giao diện còn sót giá trị Côn Đảo mặc định
    hoặc khi tên tour ghi Nước Mỹ / Nhật Bản... nhưng form điểm đến hoặc highlights bị dính Côn Đảo.
    """
    KNOWN_DESTS = [
        ('mỹ', 'Nước Mỹ'),
        ('hoa kỳ', 'Nước Mỹ'),
        ('usa', 'Nước Mỹ'),
        ('united states', 'Nước Mỹ'),
        ('nhật bản', 'Nhật Bản'),
        ('japan', 'Nhật Bản'),
        ('hàn quốc', 'Hàn Quốc'),
        ('korea', 'Hàn Quốc'),
        ('thái lan', 'Thái Lan'),
        ('thailand', 'Thái Lan'),
        ('châu âu', 'Châu Âu'),
        ('europe', 'Châu Âu'),
        ('pháp', 'Pháp'),
        ('paris', 'Pháp'),
        ('úc', 'Úc (Australia)'),
        ('australia', 'Úc (Australia)'),
        ('trung quốc', 'Trung Quốc'),
        ('china', 'Trung Quốc'),
        ('singapore', 'Singapore'),
        ('đài loan', 'Đài Loan'),
        ('taiwan', 'Đài Loan'),
        ('đà nẵng', 'Đà Nẵng'),
        ('hội an', 'Hội An'),
        ('hà giang', 'Hà Giang'),
        ('sa pa', 'Sa Pa'),
        ('sapa', 'Sa Pa'),
        ('đà lạt', 'Đà Lạt'),
        ('nha trang', 'Nha Trang'),
        ('hạ long', 'Hạ Long'),
        ('phú quốc', 'Phú Quốc'),
        ('miền tây', 'Miền Tây'),
        ('cần thơ', 'Cần Thơ'),
        ('cà mau', 'Cà Mau'),
        ('côn đảo', 'Côn Đảo')
    ]
    title_lower = (title or '').lower()
    dest_lower = (destination or '').lower().strip()

    detected_in_title = None
    for kw, norm_dest in KNOWN_DESTS:
        if kw in title_lower and kw != 'côn đảo':
            detected_in_title = norm_dest
            break

    final_dest = (destination or '').strip()
    if (not dest_lower or dest_lower in ('côn đảo', 'con dao')) and detected_in_title:
        final_dest = detected_in_title
    elif not final_dest and title:
        final_dest = title

    final_highlights = highlights.strip() if highlights else None
    if final_highlights and ('côn đảo' not in (final_dest or '').lower()):
        con_dao_kws = ['cô sáu', 'côn đảo', 'hàng dương', 'đầm trầu', 'nhà tù côn đảo', 'mứt hạt bàng']
        if any(k in final_highlights.lower() for k in con_dao_kws):
            final_highlights = None

    return final_dest or "Điểm đến du lịch", final_highlights


def generate_tour_description_ai(request: schemas.AIDescriptionRequest) -> schemas.AIDescriptionResponse:
    """
    Chức năng AI 2: Sinh mô tả tour và lịch trình tóm tắt theo từng ngày.
    - Hoạt động 100% bằng Google Gemini Cloud AI.
    - Lịch trình chi tiết từng buổi (Sáng, Chiều, Tối), bám sát 100% số ngày {duration_days} và số đêm {duration_nights}.
    - Tuyệt đối chuẩn xác theo đúng điểm đến, không bị thiên lệch hay gán nhầm sang Côn Đảo.
    """
    final_dest, final_highlights = _sanitize_destination_and_highlights(
        request.tour_title, request.destination, request.highlights
    )

    prompt = (
        f"Hãy thiết kế nội dung bài viết và lịch trình tour du lịch chuyên nghiệp, hấp dẫn:\n"
        f"- Tên tour: {request.tour_title}\n"
        f"- Điểm đến CHÍNH XÁC: {final_dest}\n"
        f"- Thời lượng bắt buộc: {request.duration_days} ngày {request.duration_nights} đêm (Yêu cầu phải có đầy đủ lịch trình chi tiết từ Ngày 1 đến Ngày {request.duration_days})\n"
        f"- Điểm nhấn trong tour: {final_highlights or f'Khám phá danh thắng, nét văn hóa đặc trưng và ẩm thực biểu tượng của {final_dest}'}\n"
        f"- Đối tượng khách hướng đến: {request.target_audience or 'Gia đình, bạn bè và du khách mọi lứa tuổi'}\n\n"
        f"Yêu cầu trả về định dạng JSON gồm các trường:\n"
        f"1. 'marketing_slogan': Slogan ngắn gọn, cuốn hút, giàu sức gợi cảm xúc du lịch cho {final_dest}.\n"
        f"2. 'description': Bài giới thiệu tour truyền cảm hứng sâu sắc (2-3 đoạn văn hoàn chỉnh, nêu bật cảnh đẹp thiên nhiên, nét văn hóa và chất lượng dịch vụ trọn gói của {final_dest}).\n"
        f"3. 'itinerary_summary': Lịch trình chi tiết từng ngày từ Ngày 1 đến Ngày {request.duration_days} tại {final_dest}. Mỗi ngày trình bày đầy đủ các buổi (Buổi sáng, Buổi chiều, Buổi tối) và hoạt động tương ứng.\n"
        f"4. 'packing_tips': Gợi ý chi tiết trang phục, giấy tờ tùy thân, đồ dùng cá nhân và mẹo chuẩn bị phù hợp nhất với điểm đến {final_dest}."
    )
    
    external_res = call_gemini_api(SYSTEM_DESC_PROMPT, prompt) or call_openai_api(SYSTEM_DESC_PROMPT, prompt)
    if not external_res:
        raise HTTPException(
            status_code=503,
            detail="Không thể tạo mô tả tour: Google Gemini Cloud AI chưa được cấu hình hoặc gặp sự cố kết nối."
        )
        
    data = _extract_json_from_llm(external_res)
    if not data or not isinstance(data, dict):
        raise HTTPException(
            status_code=502,
            detail="Google Gemini Cloud AI không phản hồi đúng định dạng JSON yêu cầu."
        )
        
    raw_slogan = data.get("marketing_slogan", "")
    slogan_str = " ".join(str(s) for s in raw_slogan) if isinstance(raw_slogan, list) else str(raw_slogan or "")

    raw_desc = data.get("description", "")
    desc_str = "\n\n".join(str(d) for d in raw_desc) if isinstance(raw_desc, list) else str(raw_desc or "")

    raw_itin = data.get("itinerary_summary", "")
    if isinstance(raw_itin, dict):
        itin_lines = []
        for k, v in raw_itin.items():
            if isinstance(v, list):
                itin_lines.append(f"{k}:\n" + "\n".join(f"  • {x}" for x in v))
            elif isinstance(v, dict):
                itin_lines.append(f"{k}:\n" + "\n".join(f"  - {subk}: {subv}" for subk, subv in v.items()))
            else:
                itin_lines.append(f"{k}: {v}")
        itin_str = "\n\n".join(itin_lines)
    elif isinstance(raw_itin, list):
        itin_blocks = []
        for idx, item in enumerate(raw_itin, 1):
            if isinstance(item, dict):
                day_title = item.get("title") or item.get("name") or ""
                day_num = item.get("day") or idx
                header = f"Ngày {day_num}: {day_title}".strip(": ")
                activities = []
                for k, v in item.items():
                    if k.lower() in ("day", "title", "name"):
                        continue
                    activities.append(f"- {str(k).capitalize()}: {v}")
                itin_blocks.append(f"{header}\n" + "\n".join(activities))
            else:
                itin_blocks.append(str(item))
        itin_str = "\n\n".join(itin_blocks)
    else:
        itin_str = str(raw_itin or "").strip()

    raw_tips = data.get("packing_tips", "")
    if isinstance(raw_tips, list):
        tips_str = ", ".join(str(item) for item in raw_tips)
    elif isinstance(raw_tips, dict):
        tips_str = "; ".join(f"{k}: {v}" for k, v in raw_tips.items())
    else:
        tips_str = str(raw_tips or "")

    return schemas.AIDescriptionResponse(
        description=desc_str,
        itinerary_summary=itin_str,
        marketing_slogan=slogan_str,
        packing_tips=tips_str,
        engine_used=f"Google Gemini ({settings.DEFAULT_AI_MODEL}) Cloud AI"
    )


def summarize_feedback_ai(db: Session, request: schemas.AIFeedbackSummaryRequest) -> schemas.AIFeedbackSummaryResponse:
    """
    Chức năng AI 3: Tóm tắt phản hồi khách hàng sau tour.
    - Hoạt động 100% bằng Google Gemini Cloud AI.
    - Phân tích chuyên sâu về chất lượng dịch vụ, khen ngợi, góp ý, HDV và đề xuất chiến lược Ban Giám Đốc.
    """
    query = db.query(models.Feedback)
    tour_title = "Toàn bộ hệ thống"
    if request.tour_id:
        query = query.filter(models.Feedback.tour_id == request.tour_id)
        t = db.query(models.Tour).filter(models.Tour.id == request.tour_id).first()
        if t:
            tour_title = f"Tour [{t.code}] {t.title}"
        
    feedbacks = query.all()
    if not feedbacks:
        return schemas.AIFeedbackSummaryResponse(
            total_feedbacks=0,
            average_rating=0.0,
            sentiment_breakdown={"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0},
            positive_highlights=[
                f"Hiện tại {tour_title} chưa có phản hồi nào được ghi nhận từ du khách đã hoàn thành chuyến đi."
            ],
            improvement_areas=[
                f"Chưa có dữ liệu phản ánh về điểm cần cải thiện cho {tour_title}."
            ],
            guide_performance_summary="Chưa có đánh giá về hướng dẫn viên cho tuyến tour này.",
            executive_recommendation=(
                "Đề xuất hành động cho Ban Giám Đốc:\n"
                "  • Hành động ngay: Kích hoạt tin nhắn SMS/Zalo tự động gửi link biểu mẫu khảo sát chất lượng dịch vụ (CSAT) kèm mã ưu đãi 5% cho khách hàng sau khi tour kết thúc.\n"
                "  • Kế hoạch dài hạn: Thiết lập cơ chế kiểm tra gọi điện thoại ngẫu nhiên (Care-call) từ bộ phận CSKH để thu thập ý kiến trực tiếp của du khách."
            ),
            engine_used=f"Google Gemini ({settings.DEFAULT_AI_MODEL}) Cloud AI"
        )
        
    total = len(feedbacks)
    avg_rating = round(sum(f.rating for f in feedbacks) / total, 2)
    guide_avg = round(sum(f.guide_rating for f in feedbacks) / total, 2)
    
    pos_count = sum(1 for f in feedbacks if f.sentiment == "POSITIVE")
    neu_count = sum(1 for f in feedbacks if f.sentiment == "NEUTRAL")
    neg_count = sum(1 for f in feedbacks if f.sentiment == "NEGATIVE")
    
    feedback_texts = "\n".join([
        f"- [Khách hàng: {f.customer_name}] (Đánh giá tour: {f.rating}/5 sao, Điểm HDV: {f.guide_rating}/5 sao): \"{f.comments}\""
        for f in feedbacks
    ])
    
    prompt = (
        f"DƯỚI ĐÂY LÀ TOÀN BỘ DỮ LIỆU {total} PHẢN HỒI THỰC TẾ CỦA KHÁCH HÀNG SAU CHUYẾN ĐI ({tour_title}):\n"
        f"{feedback_texts}\n\n"
        f"BẮT BUỘC: Bạn PHẢI đọc kỹ từng phản hồi trên và lập báo cáo phân tích 100% dựa trên các nhận xét thật này.\n"
        f"Yêu cầu trả về định dạng JSON gồm các trường:\n"
        f"1. 'positive_highlights': mảng chuỗi các điểm sáng dịch vụ khách khen ngợi (nêu dẫn chứng từ nhận xét thực tế của khách).\n"
        f"2. 'improvement_areas': mảng chuỗi các điểm khách chưa hài lòng hoặc góp ý cần nâng cấp (nêu rõ lý do từ nhận xét thực tế).\n"
        f"3. 'guide_performance_summary': Đánh giá trung thực chất lượng phục vụ của Hướng dẫn viên theo đúng các nhận xét thực tế trên.\n"
        f"4. 'executive_recommendation': Đề xuất hành động cho Ban Giám Đốc giải quyết trực tiếp các vấn đề khách vừa phản ánh."
    )
    
    external_res = call_gemini_api(SYSTEM_FEEDBACK_PROMPT, prompt) or call_openai_api(SYSTEM_FEEDBACK_PROMPT, prompt)
    if not external_res:
        raise HTTPException(
            status_code=503,
            detail="Không thể tóm tắt phản hồi: Google Gemini Cloud AI chưa được cấu hình hoặc gặp sự cố kết nối."
        )
        
    data = _extract_json_from_llm(external_res)
    if not data or not isinstance(data, dict):
        raise HTTPException(
            status_code=502,
            detail="Google Gemini Cloud AI không phản hồi đúng định dạng JSON phân tích yêu cầu."
        )
        
    raw_rec = data.get("executive_recommendation", "")
    if isinstance(raw_rec, list):
        rec_str = "\n".join(f"• {item}" for item in raw_rec)
    elif isinstance(raw_rec, dict):
        rec_lines = []
        for k, v in raw_rec.items():
            k_lower = str(k).lower()
            if "quick" in k_lower or "ngay" in k_lower:
                heading = "Các giải pháp khắc phục ngay lập tức (Quick Wins)"
            elif "long" in k_lower or "dai" in k_lower or "strat" in k_lower:
                heading = "Chiến lược nâng cao chất lượng dài hạn"
            else:
                heading = str(k).replace("_", " ").title()
            rec_lines.append(f"{heading}:")
            if isinstance(v, list):
                rec_lines.extend(f"  • {item}" for item in v)
            elif isinstance(v, dict):
                rec_lines.extend(f"  • {subk}: {subv}" for subk, subv in v.items())
            else:
                rec_lines.append(f"  • {v}")
        rec_str = "\n".join(rec_lines)
    else:
        rec_str = str(raw_rec or "")

    raw_guide = data.get("guide_performance_summary", "")
    if isinstance(raw_guide, list):
        guide_str = "\n".join(f"• {item}" for item in raw_guide)
    elif isinstance(raw_guide, dict):
        guide_str = "\n".join(f"• {k}: {v}" for k, v in raw_guide.items())
    else:
        guide_str = str(raw_guide or f"Đánh giá bình quân: {guide_avg}/5 sao.")

    raw_pos = data.get("positive_highlights", [])
    pos_list = [str(x) for x in raw_pos] if isinstance(raw_pos, list) else [str(raw_pos)]

    raw_imp = data.get("improvement_areas", [])
    imp_list = [str(x) for x in raw_imp] if isinstance(raw_imp, list) else [str(raw_imp)]

    return schemas.AIFeedbackSummaryResponse(
        total_feedbacks=total,
        average_rating=avg_rating,
        sentiment_breakdown={"POSITIVE": pos_count, "NEUTRAL": neu_count, "NEGATIVE": neg_count},
        positive_highlights=pos_list,
        improvement_areas=imp_list,
        guide_performance_summary=guide_str,
        executive_recommendation=rec_str,
        engine_used=f"Google Gemini ({settings.DEFAULT_AI_MODEL}) Cloud AI"
    )
