from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.app.database import engine, Base, SessionLocal
from backend.app import models
from backend.app.auth import hash_password

def ensure_fresh_departures(db: Session):
    """Đảm bảo các lịch khởi hành trong hệ thống luôn có ngày trong tương lai và các tour đang bán đều có chỗ"""
    today = date.today()
    departures = db.query(models.Departure).all()
    
    # 1. Nếu toàn bộ lịch khởi hành đã quá khứ, tự động tịnh tiến sang tương lai
    if departures:
        max_dep_date = max(d.departure_date for d in departures)
        if max_dep_date < today:
            shift_days = (today - max_dep_date).days + 3
            for d in departures:
                d.departure_date = d.departure_date + timedelta(days=shift_days)
                if d.return_date:
                    d.return_date = d.return_date + timedelta(days=shift_days)
                if d.status != "FULL" and d.available_slots <= 0:
                    d.available_slots = max(5, d.total_slots - 5)
            db.commit()
            print(f"[SEED] Da tinh tien cac lich khoi hanh sang tuong lai (+{shift_days} ngay).")

    # 2. Đảm bảo mọi tour đang kích hoạt (is_active=True) đều có ít nhất 1 lịch khởi hành mở bán còn chỗ
    active_tours = db.query(models.Tour).filter(models.Tour.is_active == True).all()
    guides = db.query(models.TourGuide).all()
    for idx, tour in enumerate(active_tours):
        has_any_dep = db.query(models.Departure).filter(models.Departure.tour_id == tour.id).first()
        if not has_any_dep:
            new_dep = models.Departure(
                tour_id=tour.id,
                departure_date=today + timedelta(days=3 + (idx % 6)),
                return_date=today + timedelta(days=3 + (idx % 6) + tour.duration_days),
                total_slots=25,
                available_slots=15,
                guide_id=guides[idx % len(guides)].id if guides else None,
                status="OPEN",
                notes=f"Lịch khởi hành định kỳ cho tour {tour.code} ({tour.destination})."
            )
            db.add(new_dep)
    db.commit()

def init_db(db: Session = None):
    """Khởi tạo bảng và nạp dữ liệu mẫu ban đầu"""
    Base.metadata.create_all(bind=engine)
    
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True
        
    try:
        # 1. Tạo Users nếu chưa có
        if db.query(models.User).count() == 0:
            users = [
                models.User(
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    full_name="Nguyễn Văn Quản Trị",
                    email="admin@vietjourney.vn",
                    phone="0901234567",
                    role="ADMIN"
                ),
                models.User(
                    username="tuvan",
                    hashed_password=hash_password("tuvan123"),
                    full_name="Trần Thị Mỹ Duyên (Tư Vấn)",
                    email="tuvan@vietjourney.vn",
                    phone="0912345678",
                    role="CONSULTANT"
                ),
                models.User(
                    username="ketoan",
                    hashed_password=hash_password("ketoan123"),
                    full_name="Lê Hoàng Minh (Kế Toán)",
                    email="ketoan@vietjourney.vn",
                    phone="0923456789",
                    role="ACCOUNTANT"
                )
            ]
            db.add_all(users)
            db.commit()
            print("[SEED] Da tao 3 tai khoan mau: admin, tuvan, ketoan (mat khau: <ten>123).")

        # 2. Tạo Hướng dẫn viên
        if db.query(models.TourGuide).count() == 0:
            guides = [
                models.TourGuide(
                    full_name="Hoàng Quốc Bảo",
                    phone="0987111222",
                    email="bao.hoang@vietjourney.vn",
                    languages="Tiếng Việt, Tiếng Anh",
                    experience_years=5,
                    status="AVAILABLE",
                    rating=4.9,
                    notes="Chuyên các tuyến miền Trung và Tây Nguyên, vui vẻ nhiệt tình."
                ),
                models.TourGuide(
                    full_name="Phạm Thanh Thảo",
                    phone="0987333444",
                    email="thao.pham@vietjourney.vn",
                    languages="Tiếng Việt, Tiếng Pháp",
                    experience_years=4,
                    status="ON_TOUR",
                    rating=4.8,
                    notes="Chuyên tuyến Tây Bắc, Đông Bắc và Di sản Miền Trung."
                ),
                models.TourGuide(
                    full_name="Võ Văn Hùng",
                    phone="0987555666",
                    email="hung.vo@vietjourney.vn",
                    languages="Tiếng Việt, Tiếng Hoa",
                    experience_years=6,
                    status="AVAILABLE",
                    rating=4.7,
                    notes="Am hiểu ẩm thực và văn hóa Miền Tây Nam Bộ và Phú Quốc."
                ),
                models.TourGuide(
                    full_name="Đặng Thúy Nga",
                    phone="0987777888",
                    email="nga.dang@vietjourney.vn",
                    languages="Tiếng Việt, Tiếng Hàn",
                    experience_years=3,
                    status="AVAILABLE",
                    rating=4.9,
                    notes="Chuyên nghiệp, chụp ảnh đẹp cho khách du lịch."
                )
            ]
            db.add_all(guides)
            db.commit()

        # 3. Tạo Danh sách Tour
        if db.query(models.Tour).count() == 0:
            tours_data = [
                models.Tour(
                    code="VN-DN01",
                    title="Đà Nẵng - Bà Nà Hills - Phố Cổ Hội An - Cù Lao Chàm",
                    destination="Đà Nẵng",
                    category="BIEN_DAO",
                    duration_days=3,
                    duration_nights=2,
                    base_price=4200000,
                    description="Khám phá thành phố đáng sống nhất Việt Nam với Cầu Vàng Bà Nà Hills, vẻ đẹp hoài niệm của Phố cổ Hội An và biển xanh ngắt tại đảo Cù Lao Chàm.",
                    itinerary_summary="Ngày 1: Đón sân bay - Bán đảo Sơn Trà - Ngũ Hành Sơn - Check-in Phố cổ Hội An.\nNgày 2: Chinh phục đỉnh Bà Nà Hills - Cầu Vàng - Check-in Fantasy Park - Tắm biển Mỹ Khê.\nNgày 3: Lặn ngắm san hô Cù Lao Chàm - Chợ Hàn mua đặc sản - Tiễn sân bay.",
                    highlights="Cầu Vàng Bà Nà, Lặn ngắm san hô, Thưởng thức cao lầu, mì Quảng",
                    image_url="https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-PQ02",
                    title="Phú Quốc Thiên Đường Đảo Ngọc - Sunset Town & Grand World",
                    destination="Phú Quốc",
                    category="BIEN_DAO",
                    duration_days=4,
                    duration_nights=3,
                    base_price=6800000,
                    description="Nghỉ dưỡng đẳng cấp tại đảo ngọc Phú Quốc, khám phá thành phố không ngủ Grand World, ngắm hoàng hôn rực rỡ tại Thị trấn Hoàng Hôn Sunset Town và cáp treo Hòn Thơm.",
                    itinerary_summary="Ngày 1: Đón sân bay Phú Quốc - Check-in Sunset Sanato ngắm hoàng hôn - Chợ đêm Dinh Cậu.\nNgày 2: Tour cano 4 đảo - Công viên san hô Nam Đảo - Cáp treo vượt biển Hòn Thơm.\nNgày 3: Safari Phú Quốc - Khám phá Grand World & show diễn Tinh hoa Việt Nam.\nNgày 4: Thăm vườn tiêu, nhà thùng nước mắm truyền thống - Tiễn sân bay.",
                    highlights="Cáp treo 3 dây dài nhất thế giới, Tiệc BBQ trên đảo hoang, Grand World",
                    image_url="https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-SP03",
                    title="Sa Pa Thị Trấn Sương Mờ - Chinh Phục Đỉnh Fansipan Hùng Vĩ",
                    destination="Sa Pa",
                    category="TAY_BAC",
                    duration_days=3,
                    duration_nights=2,
                    base_price=3500000,
                    description="Hành trình hòa mình vào thiên nhiên Tây Bắc hùng vĩ, ngắm nhìn ruộng bậc thang Mường Hoa, săn mây trên nóc nhà Đông Dương Fansipan và trải nghiệm văn hóa người H'Mông.",
                    itinerary_summary="Ngày 1: Xe giường nằm cao cấp Hà Nội đi Sa Pa - Bản Cát Cát xinh đẹp - Thưởng thức lẩu cá tầm.\nNgày 2: Chinh phục đỉnh Fansipan 3.143m bằng cáp treo hiện đại - Thung lũng Mường Hoa - Nhà thờ Đá Sa Pa.\nNgày 3: Núi Hàm Rồng ngắm toàn cảnh Sa Pa - Mua sắm đặc sản hạt dẻ, thịt trâu gác bếp - Khởi hành về Hà Nội.",
                    highlights="Cáp treo Fansipan, Bản Cát Cát mộng mơ, Lẩu cá hồi Tây Bắc nóng hổi",
                    image_url="https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-HG04",
                    title="Hà Giang Mùa Hoa Tam Giác Mạch - Kỳ Vĩ Đèo Mã Pí Lèng - Hẻm Tu Sản",
                    destination="Hà Giang",
                    category="TAY_BAC",
                    duration_days=4,
                    duration_nights=3,
                    base_price=4900000,
                    description="Cung đường phượt huyền thoại qua Cao nguyên đá Đồng Văn, dòng sông Nho Quế màu ngọc bích, cổng trời Quản Bạ và cột cờ Lũng Cú linh thiêng.",
                    itinerary_summary="Ngày 1: Hà Nội - Hà Giang - Cổng trời Quản Bạ - Rừng thông Yên Minh.\nNgày 2: Dốc Thẩm Mã - Nhà của Pao - Dinh họ Vương - Cột cờ Lũng Cú cực Bắc.\nNgày 3: Chinh phục Đèo Mã Pí Lèng - Du thuyền Hẻm Tu Sản sông Nho Quế - Thị trấn Mèo Vạc.\nNgày 4: Chợ phiên Đồng Văn - Khởi hành về Hà Nội.",
                    highlights="Sông Nho Quế ngọc bích, Đèo Mã Pí Lèng hùng vĩ, Cột cờ Lũng Cú",
                    image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-MT05",
                    title="Miền Tây Sông Nước Cần Thơ - Chợ Nổi Cái Răng - Đất Mũi Cà Mau",
                    destination="Cần Thơ",
                    category="MIEN_TAY",
                    duration_days=3,
                    duration_nights=2,
                    base_price=2900000,
                    description="Về phương Nam hòa mình cùng thiên nhiên sông nước miệt vườn, nghe đờn ca tài tử, xuôi thuyền ghe chợ nổi và đặt chân đến mốc tọa độ cực Nam Tổ quốc.",
                    itinerary_summary="Ngày 1: TP.HCM - Mỹ Tho - Bến Tre - Cù lao Thới Sơn - Cần Thơ - Bến Ninh Kiều.\nNgày 2: Chợ nổi Cái Răng - Sóc Trăng viếng Chùa Dơi - Bạc Liêu thăm nhà Công tử - Cà Mau.\nNgày 3: Rừng ngập mặn Năm Căn - Đất Mũi Cà Mau - Mua khô cá lóc, cua Cà Mau - Về lại TP.HCM.",
                    highlights="Chợ nổi Cái Răng tấp nập, Thưởng thức bánh xèo giòn rụm, Cực Nam Cà Mau",
                    image_url="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-HL06",
                    title="Hạ Long Kỳ Quan Thế Giới - Trải Nghiệm Du Thuyền 5 Sao Đẳng Cấp",
                    destination="Hạ Long",
                    category="DI_SAN",
                    duration_days=2,
                    duration_nights=1,
                    base_price=3200000,
                    description="Chiêm ngưỡng vẻ đẹp hàng nghìn đảo đá vôi kỳ vĩ trên Vịnh Hạ Long, nghỉ đêm trên du thuyền sang trọng, chèo kayak khám phá Hang Sửng Sốt và Đảo Ti Tốp.",
                    itinerary_summary="Ngày 1: Hà Nội - Cảng Tuần Châu - Check-in Du thuyền 5 sao - Hang Sửng Sốt - Chèo Kayak tại Hang Luồn - Tiệc trà chiều ngắm hoàng hôn trên vịnh.\nNgày 2: Tập Thái Cực Quyền đón bình minh - Tắm biển Đảo Ti Tốp - Thưởng thức buffet trưa - Cập bến về Hà Nội.",
                    highlights="Du thuyền 5 sao sang trọng, Chèo thuyền Kayak xuyên hang, Tiệc BBQ hải sản",
                    image_url="https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-NT07",
                    title="Nha Trang Biển Xanh Cát Trắng - VinWonders Đảo Hòn Tre",
                    destination="Nha Trang",
                    category="BIEN_DAO",
                    duration_days=3,
                    duration_nights=2,
                    base_price=3950000,
                    description="Kỳ nghỉ biển sôi động với các bãi tắm cát trắng thoai thoải, lặn ngắm san hô Hòn Mun, thư giãn tắm khoáng bùn I-Resort và vui chơi không giới hạn tại VinWonders.",
                    itinerary_summary="Ngày 1: Đón sân bay Cam Ranh - Tháp Bà Ponagar - Tắm bùn khoáng nóng thư giãn.\nNgày 2: Du ngoạn Vịnh Nha Trang - Bãi Tranh - Vui chơi trọn ngày tại VinWonders Hòn Tre.\nNgày 3: Viếng Chùa Long Sơn - Chợ Đầm mua yến sào & hải sản - Tiễn sân bay.",
                    highlights="VinWonders Hòn Tre, Tắm khoáng nóng trị liệu, Hải sản tươi ngon",
                    image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
                ),
                models.Tour(
                    code="VN-DL08",
                    title="Đà Lạt Thành Phố Sương Mù - Đồi Chè Cầu Đất - Thác Datanla",
                    destination="Đà Lạt",
                    category="NGHIDUONG",
                    duration_days=3,
                    duration_nights=2,
                    base_price=2850000,
                    description="Thư giãn cùng khí hậu mát mẻ quanh năm của xứ sở sương mù, săn mây đón bình minh tại Đồi Chè Cầu Đất, trải nghiệm xe máng trượt xuyên rừng thác Datanla.",
                    itinerary_summary="Ngày 1: Đón bến xe/sân bay Liên Khương - Dinh Bảo Đại - Quảng trường Lâm Viên - Hồ Xuân Hương.\nNgày 2: Săn mây Cầu Đất Panorama - Vườn dâu tây công nghệ cao - Chùa Linh Phước - Trải nghiệm máng trượt thác Datanla.\nNgày 3: Thiền Viện Trúc Lâm - Chợ Đà Lạt mua atiso, mứt hoa quả - Kết thúc tour.",
                    highlights="Săn mây Cầu Đất, Hái dâu tại vườn, Xe trượt thác Datanla cảm giác mạnh",
                    image_url="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80"
                )
            ]
            db.add_all(tours_data)
            db.commit()
            print(f"[SEED] Da tao {len(tours_data)} tours mau.")

        # 4. Tạo Lịch khởi hành (Departures)
        if db.query(models.Departure).count() == 0:
            today = date.today()
            tours = db.query(models.Tour).all()
            guides = db.query(models.TourGuide).all()
            
            departures_data = [
                # Tour 1: Đà Nẵng (Còn 15 chỗ)
                models.Departure(
                    tour_id=tours[0].id,
                    departure_date=today + timedelta(days=3),
                    return_date=today + timedelta(days=5),
                    total_slots=25,
                    available_slots=15,
                    guide_id=guides[0].id if guides else None,
                    status="OPEN",
                    notes="Tour khởi hành cuối tuần, xe 29 chỗ đời mới."
                ),
                # Tour 1: Đợt 2 (Còn 4 chỗ - sắp hết)
                models.Departure(
                    tour_id=tours[0].id,
                    departure_date=today + timedelta(days=10),
                    return_date=today + timedelta(days=12),
                    total_slots=25,
                    available_slots=4,
                    guide_id=guides[1].id if len(guides) > 1 else None,
                    status="OPEN",
                    notes="Sắp kín chỗ, ưu tiên khách đặt sớm."
                ),
                # Tour 2: Phú Quốc (Còn 8 chỗ)
                models.Departure(
                    tour_id=tours[1].id,
                    departure_date=today + timedelta(days=5),
                    return_date=today + timedelta(days=8),
                    total_slots=20,
                    available_slots=8,
                    guide_id=guides[2].id if len(guides) > 2 else None,
                    status="OPEN",
                    notes="Bao gồm vé cáp treo Hòn Thơm khứ hồi."
                ),
                # Tour 3: Sa Pa (Còn 12 chỗ)
                models.Departure(
                    tour_id=tours[2].id,
                    departure_date=today + timedelta(days=4),
                    return_date=today + timedelta(days=6),
                    total_slots=20,
                    available_slots=12,
                    guide_id=guides[1].id if len(guides) > 1 else None,
                    status="OPEN",
                    notes="Khách sạn 4 sao trung tâm Sa Pa."
                ),
                # Tour 4: Hà Giang (FULL chỗ - để test chống overbooking)
                models.Departure(
                    tour_id=tours[3].id,
                    departure_date=today + timedelta(days=7),
                    return_date=today + timedelta(days=10),
                    total_slots=16,
                    available_slots=0,
                    guide_id=guides[0].id if guides else None,
                    status="FULL",
                    notes="Đã kín chỗ đợt này."
                ),
                # Tour 5: Miền Tây (Còn 18 chỗ)
                models.Departure(
                    tour_id=tours[4].id,
                    departure_date=today + timedelta(days=2),
                    return_date=today + timedelta(days=4),
                    total_slots=25,
                    available_slots=18,
                    guide_id=guides[2].id if len(guides) > 2 else None,
                    status="OPEN",
                    notes="Trọn gói ăn uống đặc sản miền sông nước."
                ),
                # Tour 6: Hạ Long (Còn 6 chỗ)
                models.Departure(
                    tour_id=tours[5].id,
                    departure_date=today + timedelta(days=6),
                    return_date=today + timedelta(days=7),
                    total_slots=15,
                    available_slots=6,
                    guide_id=guides[3].id if len(guides) > 3 else None,
                    status="OPEN",
                    notes="Du thuyền 5 sao đẳng cấp phòng ban công riêng."
                ),
                # Tour 7: Nha Trang (Còn 14 chỗ)
                models.Departure(
                    tour_id=tours[6].id if len(tours) > 6 else tours[0].id,
                    departure_date=today + timedelta(days=4),
                    return_date=today + timedelta(days=6),
                    total_slots=25,
                    available_slots=14,
                    guide_id=guides[1].id if len(guides) > 1 else None,
                    status="OPEN",
                    notes="Tour biển đảo Nha Trang kết hợp VinWonders."
                ),
                # Tour 8: Đà Lạt (Còn 10 chỗ)
                models.Departure(
                    tour_id=tours[7].id if len(tours) > 7 else tours[0].id,
                    departure_date=today + timedelta(days=8),
                    return_date=today + timedelta(days=10),
                    total_slots=20,
                    available_slots=10,
                    guide_id=guides[3].id if len(guides) > 3 else None,
                    status="OPEN",
                    notes="Thời tiết se lạnh lý tưởng."
                )
            ]
            db.add_all(departures_data)
            db.commit()



        # 5. Tạo Khách hàng & Booking mẫu
        if db.query(models.Customer).count() == 0:
            cust1 = models.Customer(
                full_name="Nguyễn Thành Nam",
                phone="0909123456",
                email="nam.nguyen@gmail.com",
                id_card="079095001234",
                address="Quận 1, TP. Hồ Chí Minh"
            )
            cust2 = models.Customer(
                full_name="Trần Thị Lan",
                phone="0908888999",
                email="lan.tran@yahoo.com",
                id_card="001092004567",
                address="Cầu Giấy, Hà Nội"
            )
            db.add_all([cust1, cust2])
            db.commit()
            
            dep1 = db.query(models.Departure).first()
            if dep1:
                b1 = models.Booking(
                    booking_code="BK-2026-VIP01",
                    departure_id=dep1.id,
                    customer_id=cust1.id,
                    num_people=2,
                    total_amount=dep1.tour.base_price * 2,
                    deposit_amount=(dep1.tour.base_price * 2) * 0.3,
                    paid_amount=dep1.tour.base_price * 2,
                    status="CONFIRMED",
                    special_requests="Phòng tầng cao không hút thuốc"
                )
                db.add(b1)
                db.commit()
                
                pay1 = models.Payment(
                    booking_id=b1.id,
                    payment_type="FULL",
                    amount=b1.total_amount,
                    payment_method="BANK_TRANSFER",
                    status="COMPLETED",
                    transaction_code="TXN-VCB-987654",
                    note="Thanh toán 100% qua Vietcombank",
                    created_by="Kế toán"
                )
                db.add(pay1)
                db.commit()

        # 6. Tạo Đánh giá & Phản hồi mẫu (Feedbacks)
        if db.query(models.Feedback).count() == 0:
            tours = db.query(models.Tour).all()
            sample_feedbacks = [
                models.Feedback(
                    tour_id=tours[0].id,
                    customer_name="Nguyễn Thành Nam",
                    rating=5,
                    comments="Chuyến đi Đà Nẵng tuyệt vời! Hướng dẫn viên anh Bảo rất nhiệt tình, chụp hình có tâm, đồ ăn hải sản rất tươi ngon và phong phú.",
                    guide_rating=5,
                    sentiment="POSITIVE"
                ),
                models.Feedback(
                    tour_id=tours[0].id,
                    customer_name="Lê Thu Trang",
                    rating=4,
                    comments="Cảnh Bà Nà và Hội An rất đẹp. Tuy nhiên ngày thứ 2 di chuyển hơi vội vàng một chút, hy vọng công ty tăng thêm thời gian tự do dạo phố cổ.",
                    guide_rating=5,
                    sentiment="POSITIVE"
                ),
                models.Feedback(
                    tour_id=tours[1].id,
                    customer_name="Hoàng Minh Đức",
                    rating=5,
                    comments="Phú Quốc biển quá đẹp, dịch vụ cano và cáp treo Hòn Thơm xịn xò. Các bạn tư vấn viên hỗ trợ book vé chu đáo.",
                    guide_rating=5,
                    sentiment="POSITIVE"
                ),
                models.Feedback(
                    tour_id=tours[2].id,
                    customer_name="Đỗ Mai Phương",
                    rating=3,
                    comments="Sa Pa lạnh và đẹp, khách sạn sạch sẽ. Điểm trừ là tài xế bấm còi hơi nhiều trên đường đèo khiến đoàn hơi mệt.",
                    guide_rating=4,
                    sentiment="NEUTRAL"
                ),
                models.Feedback(
                    tour_id=tours[4].id,
                    customer_name="Trần Văn Khang",
                    rating=5,
                    comments="Tour Miền Tây vui hết nấc, hướng dẫn viên hát đờn ca tài tử rất hay, ăn bánh xèo và cá tai tượng chiên xù bao no.",
                    guide_rating=5,
                    sentiment="POSITIVE"
                )
            ]
            db.add_all(sample_feedbacks)
            db.commit()
            print("[SEED] Da nap phan hoi va danh gia mau thanh cong.")

        # Luôn tự động kiểm tra và đảm bảo các lịch khởi hành có ngày tương lai và còn chỗ
        # Demo refresh must be invoked explicitly; never mutate existing schedules here.
    finally:
        if close_after:
            db.close()

if __name__ == "__main__":
    init_db()
