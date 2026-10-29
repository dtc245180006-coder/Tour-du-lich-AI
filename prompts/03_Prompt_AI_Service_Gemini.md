# PROMPT 03: PHÁT TRIỂN MODULE TRÍ TUỆ NHÂN TẠO GEMINI (COMPOUND AI)
## (GROUNDED TOUR CONSULTATION, ROBUST JSON PARSER & FEEDBACK ANALYTICS)

---

### BỐI CẢNH & VAI TRÒ CỦA AI:
Bạn là **Kỹ Sư Trí Tuệ Nhân Tạo & Chuyên Gia Prompt Cấp Cao (Senior AI Prompt & GenAI Specialist)**.
Nhiệm vụ của bạn là tích hợp mô hình **Google Gemini (gemini-2.5-flash)** vào hệ thống VietJourney AI để cung cấp bộ 3 tính năng AI thương mại, tuân thủ nghiêm ngặt nguyên lý **Grounding CSDL Chống Ảo Giác (Anti-Hallucination)** và có **Fallback Engine** dự phòng khi mất mạng.

---

### BỘ 3 TÍNH NĂNG AI CẦN HIỆN THỰC CHI TIẾT:

#### 1. Tính Năng 1: Chatbot Tư Vấn Tour Grounded CSDL (Tour Consultation Chatbot)
- **Nguyên lý Grounding CSDL (Data-Grounded RAG Lite)**:
  - Trước khi gửi câu hỏi của khách hàng sang Gemini, backend truy vấn CSDL lấy danh sách toàn bộ các tour **CÒN CHỖ VÀ ĐANG MỞ BÁN**:
    ```python
    # Trích xuất dữ liệu thực tế từ bảng tours và departures:
    available_tours = [
        {
            "id": t.id,
            "code": t.code,
            "title": t.title,
            "destination": t.destination,
            "price": d.price_override or t.base_price,
            "slots_left": d.available_slots,
            "departure_date": str(d.departure_date),
            "highlights": t.highlights
        }
        for (t, d) in active_departures
    ]
    ```
- **System Prompt Bắt Buộc (Strict Anti-Hallucination Prompt)**:
  > *"Bạn là trợ lý ảo tư vấn du lịch thông minh của VietJourney AI. Nhiệm vụ của bạn là tư vấn cho khách hàng những tour du lịch phù hợp nhất.*
  > *QUY TẮC BẤT DI BẤT DỊCH:*
  > *1. CHỈ ĐƯỢC PHÉP gợi ý tối đa 3 tour có trong danh sách CSDL được cung cấp dưới đây.*
  > *2. TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ BỊA RA bất kỳ mức giá, ngày đi hoặc địa điểm nào không có trong danh sách.*
  > *3. Nếu khách yêu cầu mức ngân sách quá thấp mà không tour nào đáp ứng, hãy giải thích lịch sự và gợi ý tour có mức giá gần nhất hiện có.*
  > *4. Luôn trả về phản hồi định dạng Markdown kèm danh sách `RECOMMENDED_IDS: [id1, id2]` ở cuối."*
- **Xử lý phản hồi**:
  - Tách nội dung Markdown thân thiện cho người dùng.
  - Trích xuất mảng danh sách `tour_ids` để trả về cho Frontend, giúp UI tự động render các thẻ tour có nút "Xem chi tiết" và "Đặt ngay".
- **Bộ máy dự phòng (Heuristic Fallback Engine)**:
  - Nếu `GEMINI_API_KEY` chưa cấu hình, hoặc mạng bị ngắt kết nối:
  - Tự động kích hoạt thuật toán heuristic viết bằng Python thuần: Lọc danh sách `available_tours` theo ngân sách và từ khóa điểm đến, sau đó sinh câu trả lời mẫu chỉn chu.
  - **TUYỆT ĐỐI KHÔNG ĐƯỢC CRASH BACKEND VỚI HTTP 500**.

#### 2. Tính Năng 2: Tự Động Sinh Nội Dung & Lịch Trình Tour (Tour Content Generator)
- **Đầu vào (Input)**:
  - `title`: Tên sơ bộ của tour.
  - `destination`: Tỉnh/Thành phố điểm đến.
  - `duration_days` và `duration_nights`: Số ngày và số đêm.
  - `highlights`: Điểm nhấn hoặc yêu cầu đặc biệt từ nhân viên.
- **Yêu cầu đầu ra (Structured JSON Output)**:
  Yêu cầu LLM trả về đúng định dạng JSON:
  ```json
  {
    "title_ad": "Tiêu đề quảng cáo giật tít, thu hút, chuẩn SEO",
    "slogan": "Câu slogan ấn tượng, ngắn gọn",
    "description": "Bài viết giới thiệu truyền cảm hứng du lịch từ 150-250 từ",
    "itinerary_summary": "Ngày 1: Khám phá địa điểm A... | Ngày 2: Trải nghiệm hoạt động B... | Ngày 3: Tự do mua sắm và chia tay..."
  }
  ```
- **Hàm bóc tách JSON siêu bền bỉ (`_extract_json_from_llm`)**:
  - LLM thường có thói quen bọc JSON trong Markdown Codeblock ````json ... ```` hoặc thêm lời chào trước/sau.
  - Viết hàm dùng Regex tìm từ dấu ngoặc `{` đầu tiên đến dấu `}` cuối cùng.
  - Bọc trong khối `try...except json.JSONDecodeError`.
  - Nếu không parse được JSON, kích hoạt Fallback sinh template mặc định chuẩn để nhân viên vẫn có thể bấm nút "Dán vào biểu mẫu" mà không bị lỗi.

#### 3. Tính Năng 3: Phân Tích Cảm Xúc & Đánh Giá Sau Tour (Feedback Analytics)
- **Đầu vào**: Toàn bộ mảng nhận xét từ bảng `feedbacks` trong CSDL.
- **Yêu cầu phân tích**:
  - Phân loại tỷ lệ cảm xúc: Tích cực (`POSITIVE`), Trung lập (`NEUTRAL`), Tiêu cực (`NEGATIVE`).
  - Top 3 khía cạnh khách hàng hài lòng nhất (ví dụ: thái độ hướng dẫn viên, phương tiện di chuyển, phong cảnh).
  - Top các điểm khách phàn nàn nhiều nhất (ví dụ: thực đơn ăn uống chưa phong phú, khách sạn cách xa trung tâm).
  - Khuyến nghị 3 hành động cụ thể để Giám đốc điều hành chỉ đạo cải thiện ngay trong quý tới.
- **Đầu ra**: Trả về cấu trúc JSON để Frontend render thành các thẻ trực quan và thanh phần trăm cảm xúc.

---

### YÊU CẦU FILE ĐẦU RA (OUTPUT DELIVERABLES):

Hãy xuất ra mã nguồn hoàn chỉnh cho:
1. **`backend/app/ai_service.py`**:
   - Khởi tạo client Gemini qua `google.genai` SDK (hoặc `google.generativeai`).
   - Hàm `consult_tour_ai(db, user_message)`: Grounding CSDL + Fallback.
   - Hàm `generate_tour_content(tour_data)`: Sinh JSON bài viết & lịch trình + Parser an toàn.
   - Hàm `summarize_feedbacks(db)`: Phân tích đánh giá sau tour.
   - Hàm `_extract_json_from_llm(raw_text)`: Bóc tách JSON chống crash.
2. **`backend/app/routers/ai_router.py`**:
   - Router `/api/ai/consult`: API cho Chatbot khách hàng (Public).
   - Router `/api/ai/generate-tour-content`: API sinh nội dung cho Tư vấn viên/Admin.
   - Router `/api/ai/analyze-feedbacks`: API phân tích cho Quản trị viên/Ban giám đốc.
   - Router `/api/ai/status`: Trả về trạng thái hoạt động của AI Engine (Model name, Key configured, Fallback available).

