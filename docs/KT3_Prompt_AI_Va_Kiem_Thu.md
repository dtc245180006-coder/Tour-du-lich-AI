# BÁO CÁO KT3: THIẾT KẾ PROMPT AI & KIỂM THỬ CHỐNG ẢO GIÁC
## DỰ ÁN: HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)

---

## 1. Thách thức Ảo giác (Hallucination) trong Bài toán Du lịch

Khi tích hợp các Mô hình Ngôn ngữ Lớn (LLM) vào việc tư vấn du lịch, nguy cơ lớn nhất là mô hình **tự tạo ra giá tour**, **tự bịa ngày khởi hành**, hoặc **gợi ý các chuyến đi đã hết sạch chỗ** trong hệ thống. Điều này gây tổn hại nghiêm trọng đến trải nghiệm khách hàng và uy tín doanh nghiệp.

**Giải pháp kỹ thuật của VietJourney AI**:
1. **Neo dữ liệu thực tế (Strict Grounding)**: Trước khi gửi prompt đến AI, hệ thống tự động truy vấn SQLite để lấy danh sách các tour **CÒN CHỖ THỰC TẾ** (`available_slots > 0` và ngày đi $\ge$ hôm nay).
2. **Kẹp ngữ cảnh bắt buộc (Context Injection)**: Đưa toàn bộ danh sách tour khả dụng dưới dạng JSON vào trường `{{available_tours}}`.
3. **Chỉ thị cấm đoán mạnh (Negative Constraints)**: Cấm rõ ràng việc bịa đặt dữ liệu trong System Prompt.
4. **Local Fallback Engine**: Tích hợp bộ suy luận dựa trên quy tắc thông minh (Keyword & Regex Scoring) đảm bảo hệ thống phản hồi chính xác 100% dữ liệu CSDL ngay cả khi mất kết nối Internet.

---

## 2. Thiết kế Bộ Prompt Mẫu Chuẩn

### 2.1. Prompt Mẫu 1: AI Tư Vấn Tour Theo Ngân Sách, Thời Gian, Sở Thích

**System Prompt:**
```text
Bạn là trợ lý tư vấn tour du lịch chuyên nghiệp của VietJourney.
QUY TẮC BẮT BUỘC:
1. CHỈ gợi ý các tour CÒN CHỖ (available_slots > 0) có trong danh sách dữ liệu được cung cấp dưới đây.
2. TUYỆT ĐỐI KHÔNG tự tạo hoặc bịa đặt giá tour, ngày khởi hành hoặc mã tour không có trong dữ liệu.
3. Nếu khách yêu cầu mức ngân sách hoặc thời gian không có tour nào thỏa mãn, hãy nêu rõ lý do và gợi ý tour có sẵn gần phù hợp nhất.
4. Gợi ý tối đa 3 tour phù hợp nhất, kèm lý do tại sao phù hợp và các ngày khởi hành khả dụng.
```

**User Prompt Template:**
```text
Khách muốn đi {{days}} ngày, ngân sách {{budget}} triệu, sở thích {{preferences}}.
Danh sách các tour đang MỞ BÁN và CÒN CHỖ THỰC TẾ:
{{available_tours}}

Hãy phân tích và gợi ý tối đa 3 tour tốt nhất cho khách hàng trên.
```

---

### 2.2. Prompt Mẫu 2: AI Sinh Mô Tả Tour & Lịch Trình Tóm Tắt

**System Prompt:**
```text
Bạn là chuyên gia tiếp thị và biên tập nội dung du lịch hàng đầu Việt Nam.
Nhiệm vụ: Viết bài mô tả tour du lịch hấp dẫn, chuyên nghiệp và lịch trình tóm tắt theo từng ngày.
```

**User Prompt Template:**
```text
Hãy viết nội dung cho tour du lịch sau:
- Tên tour: {{tour_title}}
- Điểm đến: {{destination}}
- Thời lượng: {{duration_days}} ngày {{duration_nights}} đêm
- Điểm nhấn: {{highlights}}
- Đối tượng khách: {{target_audience}}

Yêu cầu trả về định dạng JSON gồm các trường:
1. 'marketing_slogan': Slogan ngắn gọn, cuốn hút.
2. 'description': Bài giới thiệu tour truyền cảm hứng.
3. 'itinerary_summary': Lịch trình tóm tắt chi tiết từng ngày (Ngày 1, Ngày 2...).
4. 'packing_tips': Gợi ý hành lý và trang phục phù hợp.
```

---

### 2.3. Prompt Mẫu 3: AI Tóm Tắt Phản Hồi Khách Hàng (Feedback QA)

**System Prompt:**
```text
Bạn là chuyên gia kiểm soát chất lượng dịch vụ du lịch (Quality Assurance).
Nhiệm vụ: Phân tích và tóm tắt toàn bộ phản hồi của khách hàng sau các chuyến tour để ban giám đốc nắm bắt.
```

**User Prompt Template:**
```text
Phân tích dữ liệu {{total_feedbacks}} phản hồi của khách hàng sau tour du lịch:
{{feedback_texts}}

Hãy trả về định dạng JSON gồm:
1. 'positive_highlights': Danh sách các điểm khách khen ngợi nhiều nhất.
2. 'improvement_areas': Danh sách các điểm khách chưa hài lòng hoặc cần cải thiện.
3. 'guide_performance_summary': Tóm tắt chất lượng phục vụ của hướng dẫn viên.
4. 'executive_recommendation': Đề xuất hành động cho ban quản trị công ty.
```

---

## 3. Kết Quả Kiểm Thử Chất Lượng AI (AI Evaluation Tests)

Đã được kiểm thử tự động trong `backend/tests/test_ai_prompts.py`:

| Tên Test Case | Kịch bản kiểm thử | Kỳ vọng & Kết quả |
|---|---|---|
| `test_ai_consultation_only_suggests_available_tours` | Khách hỏi tour biển. CSDL có tour biển còn chỗ (`TOUR-BIEN-01`) và tour biển đã hết chỗ (`TOUR-FULL-03`). | AI **chỉ** gợi ý `TOUR-BIEN-01`. Tuyệt đối **không** có `TOUR-FULL-03`. 👉 **PASSED** ✅ |
| `test_ai_consultation_handles_impossible_request` | Khách yêu cầu ngân sách 200k đi 5 ngày (yêu cầu phi thực tế). | AI không bịa tour 200k; phản hồi lịch sự giải thích ngân sách chưa đủ và đề xuất phương án. 👉 **PASSED** ✅ |
| `test_ai_generate_description` | Sinh nội dung tour mới dựa trên tiêu chí nhập vào. | Sinh đầy đủ Slogan, Mô tả hấp dẫn, Lịch trình Ngày 1, Ngày 2, Ngày 3 và Mẹo hành lý. 👉 **PASSED** ✅ |
| `test_ai_summarize_feedback` | Tổng hợp đánh giá của khách hàng cho tour. | Phân loại đúng cảm xúc (Positive/Negative), tính điểm trung bình và tóm tắt ưu/nhược điểm. 👉 **PASSED** ✅ |
