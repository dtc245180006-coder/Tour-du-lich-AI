# HỆ THỐNG QUẢN LÝ TOUR DU LỊCH CÓ TÍCH HỢP AI (VIETJOURNEY AI)
## TÀI LIỆU HƯỚNG DẪN SỬ DỤNG – V1.0

> **Đơn vị phát triển**: Nhóm 17 (Bùi Văn Trường, Hà Thành Duy)  
> **Phiên bản hệ thống**: V1.0 - Tháng 10/2026  
> **Địa chỉ chạy hệ thống**: `http://127.0.0.1:8000`  
> **Chuẩn tài liệu**: IEEE / Kỹ nghệ phần mềm ứng dụng AI  

---

## MỤC LỤC
1. [GIỚI THIỆU ỨNG DỤNG](#1-giới-thiệu-ứng-dụng)
2. [CẤU HÌNH PHẦN CỨNG - PHẦN MỀM](#2-cấu-hình-phần-cứng---phần-mềm)
   - 2.1 [Phần cứng](#21-phần-cứng)
   - 2.2 [Phần mềm & Hướng dẫn cài đặt / khởi chạy](#22-phần-mềm--hướng-dẫn-cài-đặt--khởi-chạy)
3. [CÁC CHỨC NĂNG CHÍNH (THEO DANH SÁCH ACTORS)](#3-các-chức-năng-chính)
   - 3.1 [Chức năng của Quản trị viên (Admin)](#31-chức-năng-của-quản-trị-viên-admin)
   - 3.2 [Chức năng của Nhân viên tư vấn (Consultant)](#32-chức-năng-của-nhân-viên-tư-vấn-consultant)
   - 3.3 [Chức năng của Kế toán (Accountant)](#33-chức-năng-của-kế-toán-accountant)
   - 3.4 [Chức năng của Khách vãng lai (Guest)](#34-chức-năng-của-khách-vãng-lai-guest)
4. [HƯỚNG DẪN XỬ LÝ SỰ CỐ & LƯU Ý VẬN HÀNH AN TOÀN](#4-hướng-dẫn-xử-lý-sự-cố--lưu-ý-vận-hành-an-toàn)

---

## 1. GIỚI THIỆU ỨNG DỤNG

**VietJourney AI** là hệ thống quản lý và điều hành tour du lịch lữ hành nội địa chuyên nghiệp, được tích hợp trí tuệ nhân tạo tạo sinh (**Google Gemini AI Engine**) nhằm tự động hóa và nâng cao năng suất các nghiệp vụ cốt lõi: giới thiệu tour, tư vấn khách hàng thông minh, quản lý số chỗ khả dụng, lập đơn đặt chỗ, thanh toán - đặt cọc, điều phối hướng dẫn viên và phân tích chất lượng dịch vụ sau chuyến đi.

### 1.1 Mục tiêu hệ thống
- **Tự động hóa tư vấn & Bán tour**: Cung cấp trợ lý ảo AI RAG tra cứu trực tiếp dữ liệu tour còn chỗ theo thời gian thực, gợi ý tuyến điểm theo ngân sách và thời lượng của khách hàng.
- **Kiểm soát chỗ trống tuyệt đối (Chống Overbooking)**: Áp dụng cơ chế khóa dữ liệu bi quan (*Pessimistic Locking*) và chống gửi lặp (*Idempotency Key*), đảm bảo không bao giờ xảy ra tình trạng bán quá số ghế mở bán.
- **Minh bạch tài chính & Phân quyền chặt chẽ (RBAC)**: Phân tách rành mạch quyền hạn giữa các bộ phận: Tư vấn viên chỉ giữ chỗ, Kế toán lập phiếu thu/chi, Quản trị viên điều hành tổng thể.
- **Hỗ trợ tạo nội dung & Phân tích phản hồi**: Ứng dụng AI để tự động viết mô tả/lịch trình tour hấp dẫn và tóm tắt cảm xúc (*Sentiment Analysis*) từ hàng trăm nhận xét của du khách.

### 1.2 Quy trình nghiệp vụ tổng quát
$$\text{Khách chọn tour / Hỏi AI} \xrightarrow{\text{Gửi yêu cầu}} \text{Hàng chờ (WAITING\_CONFIRM)} \xrightarrow{\text{Tư vấn duyệt}} \text{Giữ chỗ (PENDING, Trừ ghế)} \xrightarrow{\text{Kế toán thu tiền}} \text{Đã cọc (DEPOSITED) / Đã xác nhận (CONFIRMED)} \xrightarrow{\text{Admin khởi hành}} \text{Hoàn tất chuyến đi}$$

---

## 2. CẤU HÌNH PHẦN CỨNG - PHẦN MỀM

### 2.1 Phần cứng
Để triển khai máy chủ dịch vụ và vận hành ứng dụng một cách ổn định, cấu hình đề xuất như sau:

| Thành phần | Cấu hình tối thiểu (Demo / Cục bộ) | Cấu hình khuyến nghị (Production / Doanh nghiệp) |
| :--- | :--- | :--- |
| **Bộ vi xử lý (CPU)** | Intel Core i3 / AMD Ryzen 3 (2 nhân, 4 luồng) | Intel Core i5 / AMD Ryzen 5 hoặc Cloud vCPU 4 Cores |
| **Bộ nhớ trong (RAM)** | 4 GB | 8 GB trở lên |
| **Ổ cứng lưu trữ** | 2 GB dung lượng trống (SSD) | 20 GB SSD trở lên |
| **Màn hình hiển thị** | Độ phân giải 1366 × 768 | Full HD (1920 × 1080) để thao tác bảng biểu tối ưu |
| **Kết nối mạng** | Kết nối Internet (gọi Gemini API) | Băng thông tối thiểu 20 Mbps ổn định |

### 2.2 Phần mềm & Hướng dẫn cài đặt / khởi chạy

#### A. Yêu cầu môi trường
- **Hệ điều hành**: Windows 10/11, Linux (Ubuntu 20.04+) hoặc macOS.
- **Nền tảng thực thi**: Python phiên bản **3.10 trở lên** (khuyến nghị Python 3.11/3.12).
- **Hệ quản trị CSDL**: SQLite 3 (mặc định tích hợp sẵn) hoặc MySQL Server 8.0+.
- **Trình duyệt Web**: Google Chrome, Microsoft Edge, Mozilla Firefox hoặc Safari phiên bản mới nhất hỗ trợ JavaScript và CSS Grid.

#### B. Các bước cài đặt và khởi chạy hệ thống
1. **Bước 1**: Mở thư mục gốc của dự án `tourdulichAI`, mở cửa sổ lệnh (PowerShell hoặc Terminal).
2. **Bước 2**: Tạo và kích hoạt môi trường ảo Python:
   ```bash
   py -m venv .venv
   # Trên Windows:
   .venv\Scripts\activate
   ```
3. **Bước 3**: Cài đặt các gói thư viện phụ thuộc:
   ```bash
   pip install -r requirements-lock.txt
   ```
4. **Bước 4**: Khởi tạo cơ sở dữ liệu mẫu (Demo seed data):
   ```bash
   python scripts/setup_database.py --demo
   ```
   *(Hệ thống sẽ tự động khởi tạo 10 bảng dữ liệu, 7 tour du lịch, 12 đợt khởi hành, hồ sơ hướng dẫn viên và 3 tài khoản người dùng demo)*.
5. **Bước 5**: Khởi chạy ứng dụng:
   - Trên Windows: Chạy file `start.bat` hoặc gõ lệnh:
     ```bash
     uvicorn backend.app.main.app --reload --host 127.0.0.1 --port 8000
     ```
6. **Bước 6**: Mở trình duyệt web và truy cập địa chỉ: `http://127.0.0.1:8000`.

#### C. Bảng tài khoản người dùng thử nghiệm (Demo Accounts)

| Vai trò (Role) | Tên đăng nhập (Username) | Mật khẩu mặc định | Phân hệ truy cập chính |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (ADMIN)** | `admin` | `admin123` | Toàn quyền: Tour, Lịch đi, HDV, Tài khoản, AI Hub, Báo cáo |
| **Nhân viên tư vấn (CONSULTANT)** | `tuvan` | `tuvan123` | Hàng chờ tư vấn, Quản lý Đặt chỗ, Tra cứu khách hàng |
| **Kế toán (ACCOUNTANT)** | `ketoan` | `ketoan123` | Kế toán & Thu tiền, Lịch sử giao dịch, Thống kê doanh thu |
| **Khách vãng lai (GUEST)** | *(Không cần đăng nhập)* | *(Không cần)* | Trang chủ, Tra cứu tour, Trợ lý AI Gemini, Gửi đặt tour |

---

## 3. CÁC CHỨC NĂNG CHÍNH

### 3.1 Chức năng của Quản trị viên (Admin)
Quản trị viên là tác nhân nắm giữ quyền hạn cao nhất trong hệ thống, chịu trách nhiệm thiết lập danh mục sản phẩm, điều hành lịch trình, quản lý nhân sự và cấu hình trí tuệ nhân tạo.

#### 3.1.1 Đăng nhập & Bảng điều khiển trung tâm
- **Thao tác**: Truy cập `/login` $\to$ Nhập username `admin` và mật khẩu $\to$ Bấm **"Đăng nhập"**.
- **Kết quả**: Hệ thống xác thực mã băm PBKDF2, cấp phát JWT Access Token và hiển thị đầy đủ thanh Menu điều hướng bên trái dành riêng cho Admin.

#### 3.1.2 Quản lý danh mục Tour & Tích hợp AI viết mô tả
- **Xem danh sách**: Vào menu **"Quản Lý Tour"** (`/tours_admin.html`) để xem toàn bộ danh mục, tìm kiếm theo tên, mã tour (`code`), điểm đến hoặc danh mục (Biển đảo, Tây Bắc, Miền Tây, Di sản).
- **Thêm tour mới**:
  1. Bấm nút **"+ Thêm tour mới"**.
  2. Nhập các thông tin cơ bản: Tên tour, Điểm đến, Thời lượng (số ngày, số đêm), Giá niêm yết cơ bản.
  3. **Kích hoạt AI viết mô tả**: Bấm nút **"AI Viết mô tả tour"** $\to$ Hệ thống gửi prompt tới Gemini AI Engine $\to$ AI tự động sinh đoạn văn giới thiệu du lịch cuốn hút và lịch trình tóm tắt từng ngày $\to$ Tự động điền vào form.
  4. Quản trị viên duyệt lại nội dung, chỉnh sửa nếu cần và nhấn **"Lưu Tour"**.
- **Chính sách xóa tour**: Hệ thống áp dụng ràng buộc `ON DELETE RESTRICT` – Tuyệt đối ngăn chặn xóa nếu tour đã phát sinh lịch khởi hành hoặc đơn booking trong lịch sử.

#### 3.1.3 Quản lý Lịch khởi hành & Vòng đời chuyến đi
- **Mở đợt khởi hành mới**:
  1. Truy cập menu **"Lịch Khởi Hành & Chỗ"** (`/departures.html`) $\to$ Bấm **"+ Mở đợt khởi hành mới"**.
  2. Chọn Tour gốc, Ngày xuất phát (`departure_date`), Ngày kết thúc (`return_date`), Tổng số chỗ ngồi mở bán (`total_slots`), và chỉ định Hướng dẫn viên phụ trách.
  3. Hệ thống tự động kiểm tra xung đột: Ngày kết thúc phải sau ngày xuất phát; Hướng dẫn viên không được trùng lịch với bất kỳ đoàn nào khác.
  4. Sau khi lưu, hệ thống tự động gán `available_slots = total_slots` và đặt trạng thái là **`OPEN`** (Mở bán).
- **Điều hành vòng đời chuyến đi**:
  - **Bắt đầu chuyến đi**: Đến ngày khởi hành, Admin bấm **"Bắt đầu"** $\to$ Chuyến chuyển sang **`RUNNING`**, đồng thời trạng thái của HDV phụ trách tự động chuyển thành **`ON_TOUR`**.
  - **Hoàn tất chuyến đi**: Khi đoàn về an toàn, Admin bấm **"Hoàn tất"** $\to$ Chuyến chuyển sang **`COMPLETED`**, HDV tự động quay về trạng thái **`AVAILABLE`** (Sẵn sàng nhận tour mới).

#### 3.1.4 Quản lý Hướng dẫn viên (Tour Guides)
- **Truy cập**: Menu **"Hướng Dẫn Viên"** (`/guides.html`).
- **Nghiệp vụ**: Thêm mới hồ sơ, cập nhật số điện thoại, trình độ ngoại ngữ (Anh, Pháp, Trung...), thâm niên kinh nghiệm và ghi chú chuyên môn.
- **Giám sát trạng thái**: Theo dõi nhãn trạng thái trực quan:
  - `AVAILABLE` (Xanh lá): Sẵn sàng điều phối.
  - `ON_TOUR` (Vàng cam): Đang dẫn tour thực tế.
  - `OFF` (Xám): Đang nghỉ phép.

#### 3.1.5 Quản lý Tài khoản & Phân quyền bảo mật (RBAC)
- **Truy cập**: Menu **"Quản Lý Tài Khoản"** (`/users.html`).
- **Nghiệp vụ**: Tạo tài khoản cho nhân sự mới, chỉ định vai trò (`ADMIN`, `CONSULTANT`, `ACCOUNTANT`), khóa/kích hoạt tài khoản hoặc đặt lại mật khẩu.
- **Cơ chế an toàn**: Hệ thống có cơ chế bảo vệ tài khoản Quản trị viên cuối cùng (không cho phép tự khóa hoặc tự xóa tài khoản Admin duy nhất đang hoạt động).

#### 3.1.6 AI Hub - Phân tích cảm xúc & Tóm tắt đánh giá du khách
- **Truy cập**: Menu **"AI Hub & Phản Hồi"** (`/ai_hub.html`).
- **Nghiệp vụ**:
  1. Chọn Tour cần phân tích từ danh sách.
  2. Bấm nút **"Bắt Đầu Phân Tích & Tóm Tắt AI"**.
  3. Hệ thống gom toàn bộ nhận xét của du khách, gửi tới Gemini AI để trích xuất 4 khối báo cáo thông minh:
     - **Chỉ số cảm xúc (Sentiment)**: Tỷ lệ Tích cực / Tiêu cực / Trung lập.
     - **Điểm nổi bật được khen ngợi**: Điểm du lịch, khách sạn, ẩm thực.
     - **Điểm khách phản ánh cần khắc phục**: Xe đưa đón, thời gian tham quan...
     - **Đánh giá chất lượng HDV & Đề xuất hành động**: Báo cáo phục vụ Ban Giám Đốc cải tiến chất lượng dịch vụ.

---

### 3.2 Chức năng của Nhân viên tư vấn (Consultant)
Nhân viên tư vấn chịu trách nhiệm tiếp nhận nhu cầu của khách hàng, xử lý hàng chờ tư vấn, xác nhận giữ chỗ và chăm sóc khách hàng.

> [!IMPORTANT]
> **Giới hạn quyền hạn nghiệp vụ**: Nhân viên tư vấn **tuyệt đối không có quyền thu tiền hay lập phiếu thu**. Sau khi giữ chỗ thành công, tư vấn viên bàn giao mã đơn cho bộ phận Kế toán để thực hiện các giao dịch tài chính.

#### 3.2.1 Tiếp nhận & Xử lý Hàng chờ tư vấn
1. Mở menu **"Hàng Chờ Tư Vấn"** (`/consultations.html`).
2. Quan sát danh sách các đơn yêu cầu do khách vãng lai gửi lên từ trang chủ (mang trạng thái **`WAITING_CONFIRM`**).
3. Tư vấn viên bấm gọi điện thoại/liên hệ với khách để xác nhận thông tin: số lượng người, lịch trình, giá vé và điều kiện cọc.
4. **Xử lý kết quả**:
   - **Trường hợp Khách đồng ý**: Nhấn nút **"Xác Nhận Giữ Chỗ"** $\to$ Hệ thống kích hoạt khóa bi quan (*Pessimistic Lock*), kiểm tra số ghế trống $\to$ Trừ số ghế tương ứng (`available_slots -= num_people`) $\to$ Đơn chuyển sang trạng thái chính thức **`PENDING`** (Chờ thanh toán).
   - **Trường hợp Khách hủy / Không liên lạc được**: Nhấn nút **"Từ chối"**, nhập lý do hủy $\to$ Đơn chuyển sang **`CANCELLED`** (Không ảnh hưởng đến số chỗ của chuyến).

#### 3.2.2 Quản lý Đặt chỗ (Bookings) & Khách hàng
1. Mở menu **"Quản Lý Đặt Chỗ"** (`/bookings.html`).
2. Tra cứu danh sách đơn booking theo mã đặt chỗ (`BK-...`), tên khách hàng hoặc số điện thoại.
3. Theo dõi nhãn trạng thái trực quan:
   - 🟡 `WAITING_CONFIRM`: Đơn chờ tư vấn liên hệ (chưa giữ ghế).
   - 🟠 `PENDING`: Đã duyệt giữ chỗ, đang chờ khách thanh toán tiền cọc.
   - 🔵 `DEPOSITED`: Đã đóng tiền đặt cọc (tối thiểu 30% giá trị đơn).
   - 🟢 `CONFIRMED`: Đã thanh toán đủ 100% chi phí tour, sẵn sàng khởi hành.
   - 🔴 `CANCELLED`: Đơn đã bị hủy bỏ.
4. **Tạo đặt chỗ trực tiếp**: Trường hợp khách liên hệ trực tiếp qua quầy giao dịch, tư vấn viên chọn tour, chọn đợt khởi hành còn mở bán, nhập thông tin khách hàng và bấm **"Tạo Đặt Chỗ"** để giữ ghế ngay lập tức.

#### 3.2.3 Hủy booking & Tự động hoàn trả chỗ trống
1. Khi khách hàng có yêu cầu hủy chuyến đã giữ chỗ (ở trạng thái `PENDING`, `DEPOSITED` hoặc `CONFIRMED`), tư vấn viên tìm đúng đơn booking.
2. Bấm nút **"Hủy đơn"**, nhập lý do khách hủy.
3. **Cơ chế hoàn ghế tự động**: Hệ thống lập tức cộng hoàn trả lại số ghế vào đợt khởi hành (`available_slots += num_people`), đồng thời nếu chuyến từng bị gắn mác "Hết chỗ" (`FULL`) thì sẽ tự động mở bán lại (`OPEN`).

---

### 3.3 Chức năng của Kế toán (Accountant)
Kế toán là tác nhân chịu trách nhiệm độc quyền về phân hệ tài chính, ghi nhận dòng tiền thu/chi, quản lý đặt cọc, đối soát giao dịch và lập báo cáo doanh thu.

#### 3.3.1 Quản lý Thu tiền & Lập phiếu thanh toán
1. Mở menu **"Kế Toán & Thu Tiền"** (`/payments.html`) hoặc bấm nút **"Thu tiền"** trên màn hình quản lý đơn đặt chỗ.
2. Kiểm tra thông tin đơn: Mã booking, Tổng giá trị tour, Số tiền đã thanh toán (`paid_amount`) và Số tiền còn nợ (`total_amount - paid_amount`).
3. Nhập các thông số giao dịch:
   - **Số tiền thu thực tế (VNĐ)**: Phải là số dương và không vượt quá số dư nợ còn lại.
   - **Phương thức thanh toán**: Chuyển khoản ngân hàng (`BANK_TRANSFER`), Tiền mặt (`CASH`), hoặc Thẻ tín dụng (`CREDIT_CARD`).
   - **Phân loại thu**: Thu tiền đặt cọc (`DEPOSIT`), Thu tiền đợt cuối, hoặc Thu toàn bộ 100% (`FULL`).
4. Nhấn **"Xác Nhận Thu Tiền"**:
   - Hệ thống tự sinh mã giao dịch duy nhất (`transaction_code: PAY-...`), ghi nhận người lập phiếu (`created_by`).
   - Tự động cộng dồn: `paid_amount += amount`.
   - **Tự động cập nhật trạng thái đơn booking**:
     - Nếu đã thanh toán đủ 100% $\to$ Đơn chuyển sang **`CONFIRMED`** (Đã xác nhận).
     - Nếu số tiền đã đóng đạt từ 30% trở lên $\to$ Đơn chuyển sang **`DEPOSITED`** (Đã cọc).

#### 3.3.2 Xử lý Hoàn tiền khi hủy tour (Refund Management)
Khi khách hàng hủy chuyến trước ngày khởi hành, hệ thống áp dụng bảng chính sách hoàn tiền tự động dựa trên khoảng thời gian báo trước:
- Báo trước $\ge 15$ ngày khởi hành: **Hoàn 100%** số tiền đã đóng.
- Báo trước từ 7 đến dưới 15 ngày: **Hoàn 70%** số tiền đã đóng.
- Báo trước từ 3 đến dưới 7 ngày: **Hoàn 50%** số tiền đã đóng.
- Báo trước dưới 3 ngày hoặc sau khởi hành: **Hoàn 0%** (không hoàn lại).
Kế toán kiểm tra số tiền hoàn dự kiến, duyệt lập phiếu chi hoàn tiền (`payment_type = 'REFUND'`) và thực hiện đối soát ngân quỹ thực tế.

#### 3.3.3 Lịch sử giao dịch & Đối soát tài chính
- Quản lý bảng sổ cái điện tử ghi nhận từng đợt thu/chi kèm thời gian tạo chính xác (`created_at`).
- Tìm kiếm và đối soát theo mã giao dịch (`PAY-...`) hoặc mã booking (`BK-...`), đảm bảo doanh thu khớp tuyệt đối giữa phần mềm và tài khoản ngân hàng.

#### 3.3.4 Báo cáo Thống kê & Phân tích hiệu quả kinh doanh
1. Truy cập menu **"Thống Kê Doanh Thu"** (`/stats.html`).
2. Theo dõi các chỉ số tài chính tổng hợp theo thời gian thực:
   - **Tổng thực thu**: Doanh thu thực tế đã thu vào trừ đi tổng tiền đã hoàn trả.
   - **Doanh thu dự kiến**: Tổng tiền từ các đơn đã xác nhận giữ chỗ.
   - **Biểu đồ cột "Top Tour Đóng Góp Doanh Thu Cao Nhất"**: Trực quan hóa những tuyến tour mang lại dòng tiền lớn nhất (có tooltip hiển thị chi tiết số liệu khi rê chuột).
   - **Biểu đồ tròn "Tỷ Lệ Lấp Đầy Chỗ Ngồi"**: Phân tích phần trăm ghế đã đặt so với tổng dung lượng mở bán trên toàn hệ thống.

---

### 3.4 Chức năng của Khách vãng lai (Guest)
Khách vãng lai là người dùng đầu cuối truy cập trang web để tra cứu thông tin và trải nghiệm dịch vụ du lịch mà không cần phải đăng nhập tài khoản.

#### 3.4.1 Tra cứu Tour & Lịch trình chi tiết
- Truy cập Trang chủ (`/tours.html` hoặc `/index.html`).
- Xem toàn bộ danh sách các chương trình tour, lọc theo điểm đến, thời lượng (ví dụ: 3N2Đ, 4N3Đ) và mức giá niêm yết.
- Bấm **"Xem chi tiết"** để xem lộ trình từng ngày, điểm nhấn nổi bật, danh sách các đợt khởi hành còn mở bán kèm số chỗ còn trống khả dụng.

#### 3.4.2 Trợ lý ảo AI Gemini tư vấn thông minh (RAG Engine)
- Bấm vào nút biểu tượng **"Trợ lý AI Gemini"** ở góc phải màn hình để mở Drawer hội thoại.
- Nhập nhu cầu du lịch thực tế bằng ngôn ngữ tự nhiên, ví dụ:
  > *"Tôi có ngân sách khoảng 4 triệu đồng, muốn đi nghỉ dưỡng biển đảo 3 ngày cùng gia đình thì nên đi tour nào?"*
- AI Gemini sử dụng kỹ thuật RAG neo dữ liệu, tra cứu các tour đang có trong CSDL còn số chỗ trống và phản hồi chính xác tên tour, mã tour, mức giá và ngày khởi hành phù hợp nhất.

#### 3.4.3 Gửi đơn đăng ký đặt tour nhanh
1. Tại bảng lịch khởi hành của tour mong muốn, khách bấm nút **"Đặt tour"**.
2. Nhập họ và tên, số điện thoại liên hệ, email, số lượng khách đi cùng và ghi chú đặc biệt (ví dụ: ăn chay, có trẻ nhỏ).
3. Bấm **"Gửi yêu cầu"** $\to$ Hệ thống xuất mã yêu cầu theo dõi (`REQ-...`).
4. Đơn được lưu vào hệ thống ở trạng thái **`WAITING_CONFIRM`** và chuyển sang Hàng chờ tư vấn để nhân viên chăm sóc khách hàng chủ động gọi điện hỗ trợ.

#### 3.4.4 Gửi đánh giá sau chuyến đi
- Sau khi hoàn thành hành trình, khách hàng có thể gửi đánh giá: chấm điểm chất lượng tour (1 đến 5 sao), chấm điểm chất lượng Hướng dẫn viên (1 đến 5 sao) và để lại bình luận chi tiết. Dữ liệu này sẽ được nạp vào đường ống AI Hub để phân tích chất lượng dịch vụ.

---

## 4. HƯỚNG DẪN XỬ LÝ SỰ CỐ & LƯU Ý VẬN HÀNH AN TOÀN

### 4.1 Xử lý các sự cố thường gặp

| Hiện tượng sự cố | Nguyên nhân khả dĩ | Cách khắc phục |
| :--- | :--- | :--- |
| **Không mở được trang web (`127.0.0.1:8000`)** | Máy chủ Uvicorn chưa được bật hoặc file `start.bat` bị tắt | Mở lại cửa sổ dòng lệnh, kích hoạt `.venv` và gõ lệnh chạy máy chủ `uvicorn backend.app.main:app --reload`. |
| **Báo lỗi đăng nhập "Tên đăng nhập hoặc mật khẩu không chính xác"** | Nhập sai thông tin hoặc tài khoản đã bị vô hiệu hóa (`is_active = False`) | Kiểm tra lại phím CapsLock; sử dụng tài khoản demo chuẩn (`admin/admin123`, `tuvan/tuvan123`, `ketoan/ketoan123`) hoặc liên hệ Admin kiểm tra bảng `users`. |
| **Không bấm được nút "Thu tiền"** | Đang đăng nhập bằng tài khoản Tư vấn viên (`tuvan`) | Đây là tính năng phân quyền: Tư vấn viên không có quyền thu tiền. Đăng xuất và đăng nhập bằng tài khoản Kế toán (`ketoan`) hoặc Admin. |
| **Báo lỗi "Số chỗ trống không đủ" khi duyệt giữ chỗ** | Đợt khởi hành đã hết chỗ hoặc có người khác vừa giữ chỗ trước | Kiểm tra cột `available_slots`. Đề xuất khách chuyển sang ngày khởi hành khác gần nhất của cùng tuyến tour. |
| **AI không phản hồi hoặc trả về thông báo lỗi** | Máy tính mất kết nối Internet hoặc chưa cấu hình API Key của Google Gemini | Kiểm tra lại kết nối mạng; đăng nhập quyền Admin vào AI Hub kiểm tra trạng thái Gemini API Key. |

### 4.2 Các nguyên tắc vận hành an toàn dữ liệu
1. **Bảo mật phiên làm việc**: Luôn bấm nút **"Đăng xuất"** sau khi kết thúc ca làm việc, đặc biệt trên các máy tính dùng chung tại văn phòng.
2. **Quy trình thanh toán độc lập**: Tuyệt đối không thu tiền bằng lời hứa miệng; mọi khoản thu phải lập phiếu trên phần mềm để đảm bảo tự động tính toán trạng thái `DEPOSITED` và `CONFIRMED`.
3. **Sao lưu cơ sở dữ liệu định kỳ**: Định kỳ sao lưu file `tour_management.db` (đối với SQLite) hoặc backup dump (đối với MySQL) trước mỗi đợt nâng cấp hoặc bảo trì hệ thống.
