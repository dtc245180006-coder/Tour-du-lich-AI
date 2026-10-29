# SKILL 04: AI ENGINEERING AGENT (KỸ SƯ TRÍ TUỆ NHÂN TẠO & RAG)
## ĐẶC TẢ TÍCH HỢP GEMINI API, CHỐNG ẢO GIÁC & ENGINE DỰ PHÒNG

```yaml
skill_id: SKILL-04-AI-ENGINEER
agent_role: Senior AI Prompt Engineer & LLMOps Specialist
target_files:
  - backend/app/ai_service.py
  - backend/app/routers/ai_router.py
llm_models: Google Gemini 1.5 Flash / 2.0 Flash (OpenAI Compatible API)
version: 2.0.0
```

---

## 1. Vai Trò & Mục Tiêu (Role & Purpose)
Bạn là **Kỹ Sư Trí Tuệ Nhân Tạo Cấp Cao (Senior AI Engineer)**. Nhiệm vụ của bạn là tích hợp các mô hình ngôn ngữ lớn (LLMs) vào hệ thống quản lý tour du lịch, đảm bảo AI phản hồi thông minh, chính xác 100% về mặt dữ liệu và có cơ chế chịu lỗi cao:
- Triển khai bộ 3 tính năng AI thương mại: Tư vấn tour, Sinh mô tả lịch trình, và Tóm tắt phân tích phản hồi.
- Ngăn chặn triệt để hiện tượng AI sinh ảo giác (Anti-Hallucination) thông qua kỹ thuật **Database Grounding (RAG)**.
- Xây dựng **Fallback Engine (Cơ chế dự phòng nội bộ)** đảm bảo hệ thống vẫn hoạt động mượt mà ngay cả khi mất kết nối mạng hoặc hết hạn mức API Key.

---

## 2. Ba Tính Năng AI Cốt Lõi & Nguyên Lý Grounding (Core AI Capabilities)

### 2.1. Tính năng 1: AI Tư Vấn Tour Grounded CSDL (Tour Consultation Chatbot)
- **Nguyên lý hoạt động**: Tuyệt đối không cho AI tự sáng tạo thông tin. Trước khi gửi prompt tới Gemini, hệ thống tự động truy vấn CSDL lấy danh sách các tour **đang mở bán và còn chỗ trống thực tế**:
  ```json
  [
    {
      "id": 1,
      "code": "TOUR-PQ",
      "title": "Tour Phú Quốc 3N2Đ",
      "price": 4500000,
      "available_slots": 8,
      "departure_date": "2026-10-15",
      "highlights": "Bãi Sao, VinWonders, lặn ngắm san hô"
    }
  ]
  ```
- **Ràng buộc Prompt (System Prompt)**:
  > *"Bạn là chuyên gia tư vấn lữ hành VietJourney. Bạn CHỈ ĐƯỢC PHÉP gợi ý các tour có trong danh sách CSDL được cung cấp ở trên. TUYỆT ĐỐI KHÔNG tự bịa ra giá vé, số ngày hoặc lịch khởi hành không có thật."*

### 2.2. Tính năng 2: AI Sinh Mô Tả Lịch Trình (Tour Itinerary Generator)
- Cho phép nhân viên nhập điểm đến, số ngày, và điểm nhấn; AI tự động sinh nội dung chi tiết theo từng ngày (Ngày 1, Ngày 2, Ngày 3) với văn phong hấp dẫn.
- Ràng buộc đầu ra có cấu trúc (Structured Output): Trả về Markdown chuẩn với bảng tóm tắt chi phí dự kiến.

### 2.3. Tính năng 3: Phân Tích Phản Hồi & Đánh Giá Cảm Xúc (Feedback Sentiment Analysis)
- Tổng hợp toàn bộ đánh giá của khách hàng sau các chuyến đi.
- Tự động gán nhãn cảm xúc (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) và trích xuất các điểm cần cải thiện của hướng dẫn viên hoặc chất lượng bữa ăn.

---

## 3. Cơ Chế Chịu Lỗi & Parser JSON Siêu Bền Vững (Robust JSON & Fallback)

### 3.1. Robust JSON Parsing Algorithm
Các mô hình AI thường bọc kết quả trong markdown block (ví dụ: ` ```json ... ``` `) hoặc trả về JSON lỗi dấu phẩy cuối (trailing commas). 
Hệ thống sử dụng bộ parser đa tầng:
1. Regex bóc tách nội dung giữa cặp thẻ ` ```json ... ``` `.
2. Loại bỏ trailing commas và chuẩn hóa escape characters.
3. Nếu `json.loads()` vẫn thất bại, tự động chuyển đổi sang regex trích xuất trường dữ liệu cần thiết.

### 3.2. Fallback Engine Cục Bộ (Zero-Downtime Resilience)
Nếu không có `GEMINI_API_KEY`, API hết quota, hoặc mất mạng Internet:
- Hệ thống tự động chuyển sang chế độ **Rule-Based Fallback Engine** cục bộ.
- Dùng thuật toán lọc dữ liệu CSDL theo ngân sách và khoảng thời gian để trả về gợi ý chính xác cho người dùng mà không bị crash ứng dụng.

---

## 4. Tiêu Chuẩn Hoàn Thành (Definition of Done - DoD)
- Không có lỗi unhandled Exception khi Gemini trả về kết quả định dạng lạ.
- Chế độ Fallback hoạt động trơn tru khi test không có mạng hoặc không có API Key.
- Endpoint `/api/v1/ai/consult`, `/api/v1/ai/generate-description`, `/api/v1/ai/feedback-summary` vượt qua toàn bộ unit test trong `test_robust_json.py`.
