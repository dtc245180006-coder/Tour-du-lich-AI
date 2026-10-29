from email.utils import formatdate, make_msgid
import smtplib
import threading
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)

def _send_smtp_worker(to_email: str, subject: str, html_body: str):
    """Hàm gửi email qua SMTP chạy ngầm trong background thread, không chặn luồng chính"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP chưa được cấu hình SMTP_USER hoặc SMTP_PASSWORD. Bỏ qua việc gửi email.")
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg['To'] = to_email
        msg['Reply-To'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain='ictu.edu.vn')

        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL or settings.SMTP_USER, [to_email], msg.as_string())
        server.quit()
        logger.info(f"Đã gửi email thành công tới: {to_email} với tiêu đề '{subject}'")
    except Exception as e:
        logger.error(f"Lỗi khi gửi email SMTP tới {to_email}: {e}")

def send_email_async(to_email: str, subject: str, html_body: str):
    """Gửi email không đồng bộ (fire and forget)"""
    if not to_email or '@' not in to_email:
        return
    thread = threading.Thread(target=_send_smtp_worker, args=(to_email.strip(), subject, html_body), daemon=True)
    thread.start()

# ==========================================
# CÁC MẪU EMAIL NGHIỆP VỤ (TRANSACTIONAL TEMPLATES)
# ==========================================

def send_booking_confirmation_email(booking, customer, departure, tour):
    """Gửi email tiếp nhận đặt tour kèm hướng dẫn chuyển khoản VietQR và Magic Link tra cứu"""
    if not customer or not customer.email:
        return

    track_url = f"{settings.APP_BASE_URL}/home?track_code={booking.booking_code}&token={booking.access_token}"
    vietqr_url = (
        f"https://img.vietqr.io/image/MB-0333388888-compact2.png"
        f"?amount={int(booking.deposit_amount or (booking.total_amount * 0.3))}"
        f"&addInfo=VJ+{booking.booking_code}"
        f"&accountName=CONG+TY+DU+LICH+VIETJOURNEY"
    )

    dep_date_str = departure.departure_date.strftime("%d/%m/%Y") if departure and departure.departure_date else "Chưa định"
    ret_date_str = departure.return_date.strftime("%d/%m/%Y") if departure and departure.return_date else "Theo lịch trình"
    tour_title = tour.title if tour else "Tour du lịch VietJourney"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 30px 25px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; }}
            .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
            .content {{ padding: 25px; }}
            .badge-code {{ display: inline-block; background: #f1f5f9; color: #0284c7; font-weight: 800; padding: 6px 14px; border-radius: 8px; font-size: 15px; border: 1px dashed #cbd5e1; margin-bottom: 15px; font-family: monospace; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 20px; }}
            .table-info {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            .table-info td {{ padding: 8px 4px; vertical-align: top; }}
            .table-info td.label {{ color: #64748b; width: 40%; font-weight: 500; }}
            .table-info td.val {{ color: #0f172a; font-weight: 700; }}
            .qr-box {{ text-align: center; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
            .qr-box h3 {{ margin: 0 0 10px; color: #166534; font-size: 16px; font-weight: 800; }}
            .qr-box p {{ margin: 0 0 15px; font-size: 12px; color: #15803d; }}
            .btn-cta {{ display: block; width: fit-content; margin: 25px auto 10px; background: #0284c7; color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 700; font-size: 14px; text-align: center; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3); }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px; text-align: center; font-size: 11px; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VIETJOURNEY TOUR</h1>
                <p>Hệ Thống Quản Lý & Vận Hành Tour Du Lịch Thông Minh</p>
            </div>
            <div class="content">
                <p>Kính gửi Quý khách <strong>{customer.full_name}</strong>,</p>
                <p>Cảm ơn Quý khách đã đăng ký tour du lịch tại <strong>VietJourney</strong>. Hệ thống đã tiếp nhận yêu cầu đặt chỗ của Quý khách với thông tin chi tiết dưới đây:</p>
                
                <div style="text-align: center;">
                    <span class="badge-code">MÃ ĐƠN: {booking.booking_code}</span>
                </div>

                <div class="card">
                    <table class="table-info">
                        <tr>
                            <td class="label">Tuyến tour:</td>
                            <td class="val">{tour_title}</td>
                        </tr>
                        <tr>
                            <td class="label">Ngày khởi hành:</td>
                            <td class="val">{dep_date_str} - {ret_date_str}</td>
                        </tr>
                        <tr>
                            <td class="label">Số lượng khách:</td>
                            <td class="val">{booking.num_people} người</td>
                        </tr>
                        <tr>
                            <td class="label">Tổng giá trị tour:</td>
                            <td class="val" style="color: #0284c7;">{booking.total_amount:,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td class="label">Số tiền cọc tối thiểu (30%):</td>
                            <td class="val" style="color: #ea580c; font-size: 15px;">{booking.deposit_amount:,.0f} VNĐ</td>
                        </tr>
                    </table>
                </div>

                <div class="qr-box">
                    <h3>THANH TOÁN ĐẶT CỌC BẰNG CHUYỂN KHOẢN VIETQR</h3>
                    <p>Quý khách mở Ứng dụng Ngân hàng bất kỳ để quét mã QR thanh toán nhanh chính xác 100%:</p>
                    <img src="{vietqr_url}" alt="Mã VietQR Chuyển Khoản" width="220" style="display: block; margin: 0 auto; border-radius: 8px; border: 1px solid #e2e8f0;"/>
                    <div style="margin-top: 15px; font-size: 12px; line-height: 1.6; color: #334155; text-align: left; background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;">
                        <strong>Ngân hàng thụ hưởng:</strong> MB Bank (Ngân hàng Quân Đội)<br>
                        <strong>Số tài khoản:</strong> 0333388888<br>
                        <strong>Chủ tài khoản:</strong> CONG TY DU LICH VIETJOURNEY<br>
                        <strong>Số tiền:</strong> {booking.deposit_amount:,.0f} VNĐ<br>
                        <strong>Nội dung chuyển khoản (bắt buộc):</strong> <span style="color: #ea580c; font-weight: 800; font-family: monospace;">VJ {booking.booking_code}</span>
                    </div>
                </div>

                <div style="text-align: center; margin: 25px 0;">
                    <a href="{track_url}" class="btn-cta" target="_blank">Theo Dõi Tiến Độ Đơn Hàng & Biên Lai Trực Tuyến</a>
                    <p style="font-size: 11px; color: #64748b; margin-top: 8px;">(Quý khách nhấp vào nút trên để xem trực tiếp hóa đơn và số tiền còn lại mà không cần đăng nhập)</p>
                </div>

                <p style="font-size: 12px; color: #64748b; line-height: 1.6;">
                    Sau khi nhận được tiền cọc, Bộ phận Kế toán của VietJourney sẽ tiến hành kiểm tra và tự động gửi biên lai xác nhận đến email này trong vòng 5-15 phút.
                </p>
            </div>
            <div class="footer">
                <p><strong>CÔNG TY LỮ HÀNH VIETJOURNEY</strong></p>
                <p>Hotline hỗ trợ 24/7: 1900 6868 | Email: {settings.SMTP_USER}</p>
                <p>Đây là email thông báo tự động, Quý khách vui lòng không trả lời trực tiếp email này.</p>
            </div>
        </div>
    </body>
    </html>
    """
    subject = f"[VietJourney] Xác nhận đặt tour #{booking.booking_code} - Hướng dẫn thanh toán cọc"
    send_email_async(customer.email, subject, html_content)


def send_payment_received_email(payment, booking, customer):
    """Gửi email biên nhận khi Kế toán hoặc Hệ thống ghi nhận thanh toán tiền cọc / toàn bộ"""
    if not customer or not customer.email:
        return

    track_url = f"{settings.APP_BASE_URL}/home?track_code={booking.booking_code}&token={booking.access_token}"
    remaining = max(0, booking.total_amount - booking.paid_amount)
    status_label = "ĐÃ ĐẶT CỌC" if booking.status == "DEPOSITED" else ("ĐÃ THANH TOÁN ĐỦ" if booking.status == "CONFIRMED" else booking.status)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); padding: 30px 25px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; }}
            .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
            .content {{ padding: 25px; }}
            .badge-success {{ display: inline-block; background: #ecfdf5; color: #059669; font-weight: 800; padding: 6px 14px; border-radius: 8px; font-size: 14px; border: 1px solid #a7f3d0; margin-bottom: 15px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 20px; }}
            .table-info {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            .table-info td {{ padding: 8px 4px; vertical-align: top; }}
            .table-info td.label {{ color: #64748b; width: 45%; font-weight: 500; }}
            .table-info td.val {{ color: #0f172a; font-weight: 700; }}
            .btn-cta {{ display: block; width: fit-content; margin: 25px auto 10px; background: #059669; color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 700; font-size: 14px; text-align: center; }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px; text-align: center; font-size: 11px; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>BIÊN LAI XÁC NHẬN THANH TOÁN</h1>
                <p>VietJourney xác nhận đã nhận thanh toán thành công</p>
            </div>
            <div class="content">
                <p>Kính gửi Quý khách <strong>{customer.full_name}</strong>,</p>
                <p>VietJourney trân trọng thông báo chúng tôi đã nhận được khoản thanh toán cho đơn đặt tour <strong>#{booking.booking_code}</strong>:</p>

                <div style="text-align: center;">
                    <span class="badge-success">TRẠNG THÁI: {status_label}</span>
                </div>

                <div class="card">
                    <table class="table-info">
                        <tr>
                            <td class="label">Mã giao dịch:</td>
                            <td class="val" style="font-family: monospace;">{payment.transaction_code or 'PAY-ONLINE'}</td>
                        </tr>
                        <tr>
                            <td class="label">Số tiền vừa thanh toán:</td>
                            <td class="val" style="color: #059669; font-size: 16px;">+{payment.amount:,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td class="label">Hình thức:</td>
                            <td class="val">{payment.payment_method or 'Chuyển khoản Ngân hàng'}</td>
                        </tr>
                        <tr>
                            <td class="label">Tổng tiền đã thanh toán:</td>
                            <td class="val">{booking.paid_amount:,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td class="label">Tổng giá trị đơn tour:</td>
                            <td class="val">{booking.total_amount:,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td class="label">Số tiền còn lại cần nộp:</td>
                            <td class="val" style="color: {'#dc2626' if remaining > 0 else '#059669'};">{remaining:,.0f} VNĐ</td>
                        </tr>
                    </table>
                </div>

                <div style="text-align: center; margin: 25px 0;">
                    <a href="{track_url}" class="btn-cta" target="_blank">Xem Biên Lai Điện Tử & Lịch Trình Chi Tiết</a>
                    <p style="font-size: 11px; color: #64748b; margin-top: 8px;">(Quý khách có thể xem trực tuyến bất kỳ lúc nào mà không cần đăng nhập)</p>
                </div>
            </div>
            <div class="footer">
                <p><strong>CÔNG TY LỮ HÀNH VIETJOURNEY</strong></p>
                <p>Hotline: 1900 6868 | Email: {settings.SMTP_USER}</p>
            </div>
        </div>
    </body>
    </html>
    """
    subject = f"[VietJourney] Biên lai xác nhận thanh toán {payment.amount:,.0f} VNĐ - Đơn #{booking.booking_code}"
    send_email_async(customer.email, subject, html_content)


def send_cancellation_email(booking, customer):
    """Gửi email xác nhận hủy tour và số tiền hoàn trả"""
    if not customer or not customer.email:
        return

    track_url = f"{settings.APP_BASE_URL}/home?track_code={booking.booking_code}&token={booking.access_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: #475569; padding: 25px; text-align: center; color: #ffffff; }}
            .content {{ padding: 25px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 20px; }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px; text-align: center; font-size: 11px; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">XÁC NHẬN HỦY ĐẶT CHỖ</h2>
                <p style="margin: 5px 0 0; font-size: 13px;">Đơn hàng #{booking.booking_code}</p>
            </div>
            <div class="content">
                <p>Kính gửi Quý khách <strong>{customer.full_name}</strong>,</p>
                <p>Yêu cầu hủy đặt chỗ cho đơn hàng <strong>#{booking.booking_code}</strong> đã được ghi nhận thành công.</p>
                <div class="card">
                    <p><strong>Lý do hủy:</strong> {booking.cancellation_reason or 'Theo yêu cầu của khách hàng'}</p>
                    <p><strong>Số tiền khách đã đóng:</strong> {booking.paid_amount:,.0f} VNĐ</p>
                    <p><strong>Số tiền hoàn lại theo chính sách:</strong> <span style="color: #059669; font-weight: bold; font-size: 16px;">{booking.refund_amount:,.0f} VNĐ</span></p>
                </div>
                <p style="font-size: 12px; color: #64748b;">Bộ phận kế toán sẽ liên hệ xác nhận thông tin tài khoản và hoàn tiền trong vòng 1-3 ngày làm việc.</p>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{track_url}" style="background: #64748b; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 13px; font-weight: bold;">Xem Chi Tiết Đơn Hàng</a>
                </div>
            </div>
            <div class="footer">
                <p>VietJourney | Hotline: 1900 6868</p>
            </div>
        </div>
    </body>
    </html>
    """
    subject = f"[VietJourney] Xác nhận hủy đặt chỗ #{booking.booking_code}"
    send_email_async(customer.email, subject, html_content)

def send_recovery_email(customer_email: str, customer_name: str, bookings_data: list):
    """Gửi email tổng hợp toàn bộ các đơn đặt tour kèm liên kết tra cứu một chạm khi khách quên mã"""
    if not customer_email or '@' not in customer_email:
        return

    items_html = ""
    for b in bookings_data:
        track_url = f"{settings.APP_BASE_URL}/home?track_code={b['booking_code']}&token={b['access_token']}"
        status_label = b['status']
        if b['status'] == 'WAITING_CONFIRM':
            status_label = 'CHỜ XÁC NHẬN'
        elif b['status'] == 'PENDING':
            status_label = 'CHỜ THANH TOÁN CỌC'
        elif b['status'] == 'DEPOSITED':
            status_label = 'ĐÃ ĐẶT CỌC (GIỮ CHỖ)'
        elif b['status'] == 'CONFIRMED':
            status_label = 'ĐÃ THANH TOÁN ĐỦ'
        elif b['status'] == 'COMPLETED':
            status_label = 'HOÀN THÀNH'
        elif b['status'] == 'CANCELLED':
            status_label = 'ĐÃ HỦY'

        remaining = max(0, b['total_amount'] - b['paid_amount'])

        items_html += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 10px;">
                <span style="font-family: monospace; font-weight: 800; font-size: 14px; color: #0284c7;">#{b['booking_code']}</span>
                <span style="font-size: 11px; font-weight: 800; background: #f1f5f9; padding: 4px 10px; border-radius: 6px; color: #334155;">{status_label}</span>
            </div>
            <p style="margin: 0 0 6px; font-weight: 700; font-size: 14px; color: #0f172a;">{b['tour_title']}</p>
            <p style="margin: 0 0 8px; font-size: 12px; color: #64748b;">Khởi hành: <strong>{b['departure_date']}</strong> • {b['num_people']} khách</p>
            <div style="font-size: 12px; margin-bottom: 12px; background: #f8fafc; padding: 8px 12px; border-radius: 8px;">
                Tổng tiền: <strong>{b['total_amount']:,.0f} đ</strong> | Đã nộp: <strong style="color: #059669;">{b['paid_amount']:,.0f} đ</strong> | Còn lại: <strong style="color: {'#dc2626' if remaining > 0 else '#059669'};">{remaining:,.0f} đ</strong>
            </div>
            <a href="{track_url}" target="_blank" style="display: block; text-align: center; background: #0284c7; color: #ffffff !important; text-decoration: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; font-size: 12px;">Xem Tiến Độ & Thanh Toán Đơn Này</a>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 25px; text-align: center; color: #ffffff; }}
            .content {{ padding: 25px; }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px; text-align: center; font-size: 11px; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0; font-size: 20px;">DANH SÁCH ĐƠN ĐẶT TOUR CỦA BẠN</h2>
                <p style="margin: 5px 0 0; font-size: 12px; opacity: 0.9;">Hệ thống lữ hành VietJourney</p>
            </div>
            <div class="content">
                <p>Kính gửi Quý khách <strong>{customer_name or 'Quý khách'}</strong>,</p>
                <p style="font-size: 13px; line-height: 1.6; color: #475569;">
                    VietJourney nhận được yêu cầu tìm lại mã đặt chỗ từ địa chỉ email này. Dưới đây là danh sách các đơn đặt tour gần đây của Quý khách:
                </p>

                <div style="margin: 20px 0;">
                    {items_html}
                </div>

                <p style="font-size: 11px; color: #94a3b8; line-height: 1.5;">
                    Quý khách có thể nhấp trực tiếp vào nút ở từng đơn bên trên để xem tiến trình đặt cọc, biên lai điện tử và mã chuyển khoản VietQR mà không cần phải nhớ mã đặt chỗ hay mật khẩu.
                </p>
            </div>
            <div class="footer">
                <p><strong>CÔNG TY LỮ HÀNH VIETJOURNEY</strong></p>
                <p>Hotline hỗ trợ 24/7: 1900 6868 | Email: {settings.SMTP_USER}</p>
            </div>
        </div>
    </body>
    </html>
    """
    subject = f"[VietJourney] Danh sách đơn đặt tour & Liên kết tra cứu của Quý khách"
    send_email_async(customer_email, subject, html_content)
