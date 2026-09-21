import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Đăng ký font Times New Roman hỗ trợ tiếng Việt
try:
    pdfmetrics.registerFont(TTFont('TNR', r'C:\Windows\Fonts\times.ttf'))
    pdfmetrics.registerFont(TTFont('TNR-Bold', r'C:\Windows\Fonts\timesbd.ttf'))
except Exception:
    # Fallback nếu không tìm thấy font
    pdfmetrics.registerFont(TTFont('TNR', r'C:\Windows\Fonts\arial.ttf'))
    pdfmetrics.registerFont(TTFont('TNR-Bold', r'C:\Windows\Fonts\arialbd.ttf'))

# Thông tin cửa hàng
STORE_NAME = "LAPTOP STORE"
STORE_ADDRESS = "Cửa Hàng Laptop Store"
STORE_TAX_ID = "Hệ thống Quản lý Bán hàng Laptop"
STORE_HOTLINE = "Hỗ trợ kỹ thuật & bảo hành tại cửa hàng"



class Exporter:
    def __init__(self):
        pass

    def print_invoice_pdf(self, order_id, customer_name, cart_items, total_amount, filepath):
        """Xuất hóa đơn PDF chuẩn với font tiếng Việt và phân trang tự động."""
        try:
            doc = SimpleDocTemplate(
                filepath, pagesize=A4,
                topMargin=20*mm, bottomMargin=20*mm,
                leftMargin=20*mm, rightMargin=20*mm
            )
            elements = []
            width = A4[0] - 40*mm  # Chiều rộng nội dung

            # === STYLES ===
            style_store = ParagraphStyle('Store', fontName='TNR-Bold', fontSize=16,
                                         alignment=TA_CENTER, spaceAfter=2*mm)
            style_info = ParagraphStyle('Info', fontName='TNR', fontSize=10,
                                        alignment=TA_CENTER, spaceAfter=1*mm)
            style_title = ParagraphStyle('Title', fontName='TNR-Bold', fontSize=14,
                                          alignment=TA_CENTER, spaceBefore=5*mm, spaceAfter=5*mm)
            style_left = ParagraphStyle('Left', fontName='TNR', fontSize=11,
                                         alignment=TA_LEFT, spaceAfter=1*mm)
            style_right = ParagraphStyle('Right', fontName='TNR', fontSize=11,
                                          alignment=TA_RIGHT)
            style_footer = ParagraphStyle('Footer', fontName='TNR', fontSize=11,
                                           alignment=TA_CENTER, spaceBefore=10*mm)

            # === HEADER CỬA HÀNG ===
            # Thêm Logo nếu có, không có thì bỏ qua
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
            if os.path.exists(logo_path):
                im = Image(logo_path, width=40*mm, height=40*mm)
                im.hAlign = 'CENTER'
                elements.append(im)
            
            elements.append(Paragraph(STORE_NAME, style_store))
            elements.append(Paragraph(STORE_ADDRESS, style_info))
            elements.append(Paragraph(STORE_TAX_ID, style_info))
            elements.append(Paragraph(STORE_HOTLINE, style_info))

            # === TIÊU ĐỀ HÓA ĐƠN ===
            elements.append(Paragraph("HÓA ĐƠN BÁN HÀNG", style_title))

            # === THÔNG TIN ĐƠN HÀNG ===
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            elements.append(Paragraph(f"Mã đơn hàng: <b>{order_id}</b>", style_left))
            elements.append(Paragraph(f"Ngày: {now}", style_left))
            elements.append(Paragraph(f"Khách hàng: {customer_name}", style_left))
            elements.append(Spacer(1, 5*mm))

            # === BẢNG SẢN PHẨM ===
            header = ['STT', 'Tên sản phẩm', 'SL', 'Đơn giá (đ)', 'Thành tiền (đ)']
            table_data = [header]

            for idx, item in enumerate(cart_items, 1):
                name = item.get('name', 'N/A')
                qty = item.get('quantity', item.get('qty', 0))
                price = item.get('price', 0)
                subtotal = item.get('total', qty * price)
                table_data.append([
                    str(idx),
                    name,
                    str(qty),
                    f"{price:,.0f}",
                    f"{subtotal:,.0f}"
                ])

            # Dòng tổng cộng
            table_data.append(['', '', '', 'TỔNG CỘNG:', f"{total_amount:,.0f} đ"])

            col_widths = [30, width - 200, 35, 70, 75]  # Điều chỉnh cột
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'TNR-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Body
                ('FONTNAME', (0, 1), (-1, -1), 'TNR'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),   # STT center
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),   # SL center
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),   # Giá right
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),

                # Grid
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1d5db')),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),

                # Tổng cộng bold
                ('FONTNAME', (3, -1), (-1, -1), 'TNR-Bold'),
                ('FONTSIZE', (3, -1), (-1, -1), 11),

                # Alternate row colors
                *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f3f4f6'))
                  for i in range(2, len(table_data) - 1, 2)],
            ]))
            elements.append(table)

            # === FOOTER ===
            elements.append(Paragraph("Cảm ơn quý khách đã mua hàng!", style_footer))

            # Build PDF
            doc.build(elements)
            return True, f"Xuất hóa đơn thành công: {filepath}"

        except Exception as e:
            return False, f"Lỗi xuất PDF: {type(e).__name__}"

    def export_inventory_to_excel(self, products_data, filepath):
        """Xuất danh sách sản phẩm ra file Excel từ dữ liệu được cung cấp (Tôn trọng Encapsulation)."""
        try:
            if not products_data:
                return False, "Không có dữ liệu để xuất"
                
            # Đảm bảo columns khớp với thứ tự của list tuple truyền vào từ ProductService.get_all_products()
            # Giả sử tuple: (id, category, name, brand, supplier_id, import_price, price, stock, cpu, ram, screen, hard_drive, gpu, weight, os, description, is_active)
            df = pd.DataFrame(products_data)
            # Cột chuẩn từ get_all_products(): 0:id, 2:name, 3:category, 4:brand, 6:price, 7:stock, 8:cpu, 9:ram, 11:hdd, 10:screen
            df = df[[0, 2, 3, 4, 6, 7, 8, 9, 11, 10]]
            df.columns = ['ID', 'Tên SP', 'Loại', 'Hãng', 'Giá bán', 'Tồn kho', 'CPU', 'RAM', 'Ổ cứng', 'Màn hình']
            
            df.to_excel(filepath, index=False, engine='openpyxl')
            return True, f"Xuất Excel thành công: {filepath}"
        except Exception as e:
            return False, f"Lỗi xuất Excel: {type(e).__name__}"