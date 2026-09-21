"""Enterprise Cart Dialog — Quản lý giỏ hàng, áp dụng Voucher (FR-03), liên kết Khách hàng (FR-07) và Xuất PDF (FR-04)."""

import os
from datetime import datetime
from nicegui import ui, app
from logic.service_container import get_container


def open_cart_dialog(container=None, on_cart_changed=None):
    if not container:
        container = get_container()

    cart = app.storage.user.get('cart', [])
    applied_voucher = {'code': '', 'discount': 0}

    with ui.dialog() as dlg, ui.card().classes(
        'w-[680px] max-w-[96vw] rounded-[24px] p-0 overflow-hidden bg-white shadow-2xl flex-col flex'
    ):
        # ── Header ──
        with ui.row().classes('w-full justify-between items-center px-6 py-4 border-b border-gray-100 bg-gray-50/80'):
            with ui.row().classes('items-center gap-2.5'):
                ui.icon('shopping_bag', size='22px').classes('text-blue-600')
                ui.label('Giỏ Hàng Mua Sắm').classes('text-lg font-bold text-gray-900')
                total_qty = sum(i.get('qty', 1) for i in cart)
                ui.label(f'{total_qty} sản phẩm').classes('text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100')
            ui.button(icon='close', on_click=dlg.close).classes('text-gray-400 hover:text-gray-700').props('flat round dense')

        # ── Main Body (Scrollable) ──
        with ui.element('div').classes('p-6 overflow-y-auto flex-1 custom-scrollbar').style('max-height: 60vh;'):
            if not cart:
                with ui.column().classes('items-center justify-center py-12 w-full'):
                    ui.icon('remove_shopping_cart', size='54px').classes('text-gray-300 mb-3')
                    ui.label('Giỏ hàng của bạn đang trống').classes('text-base font-bold text-gray-800')
                    ui.label('Hãy chọn các sản phẩm laptop ưng ý để tiếp tục thanh toán.').classes('text-xs text-gray-500 mt-1')
                    ui.button('Khám Phá Sản Phẩm Ngay', on_click=lambda: (dlg.close(), ui.navigate.to('/'))).classes(
                        'mt-5 bg-[#0071e3] text-white rounded-xl text-xs px-5 py-2 font-medium shadow-xs'
                    ).props('no-caps')
            else:
                # ── Danh sách sản phẩm ──
                ui.label('DANH SÁCH SẢN PHẨM').classes('text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3')
                
                @ui.refreshable
                def render_items():
                    nonlocal cart
                    cart = app.storage.user.get('cart', [])
                    if not cart:
                        dlg.close()
                        open_cart_dialog(container, on_cart_changed)
                        return

                    for idx, item in enumerate(cart):
                        p_id = item['id']
                        name = item['name']
                        price = float(item['price'])
                        qty = int(item.get('qty', 1))
                        item_total = price * qty

                        is_gaming = any(k in name for k in ('Gaming', 'ROG', 'TUF', 'Nitro', 'Legion'))
                        img_src = '/static/assets/laptop_gaming.jpg' if is_gaming else '/static/assets/laptop_silver.jpg'

                        with ui.row().classes('w-full items-center justify-between py-3 border-b border-gray-100 last:border-0 gap-3'):
                            # Thumbnail + Info
                            with ui.row().classes('items-center gap-3 flex-1 min-w-[200px]'):
                                ui.image(img_src).classes('w-12 h-12 rounded-lg object-contain bg-gray-50 border border-gray-200 p-1 flex-shrink-0')
                                with ui.column().classes('gap-0.5 flex-1'):
                                    ui.label(name).classes('text-xs font-semibold text-gray-900 line-clamp-1 leading-snug')
                                    ui.label(f'{price:,.0f} ₫').classes('text-[11px] text-gray-500 font-medium')

                            # Quantity Controls [-] qty [+]
                            with ui.row().classes('items-center border border-gray-200 rounded-lg overflow-hidden bg-gray-50'):
                                def dec_qty(index=idx):
                                    c = app.storage.user.get('cart', [])
                                    if index < len(c):
                                        if c[index]['qty'] > 1:
                                            c[index]['qty'] -= 1
                                            c[index]['total'] = c[index]['qty'] * c[index]['price']
                                        else:
                                            c.pop(index)
                                        app.storage.user['cart'] = c
                                        render_items.refresh()
                                        render_summary.refresh()
                                        if on_cart_changed:
                                            on_cart_changed()

                                def inc_qty(index=idx, pid=p_id):
                                    c = app.storage.user.get('cart', [])
                                    if index < len(c):
                                        prod_svc = getattr(container, 'product_service', None)
                                        prod = prod_svc.get_product_by_id(pid) if prod_svc else None
                                        stock = int(prod[7]) if prod and prod[7] else 0
                                        if c[index]['qty'] < stock:
                                            c[index]['qty'] += 1
                                            c[index]['total'] = c[index]['qty'] * c[index]['price']
                                            app.storage.user['cart'] = c
                                            render_items.refresh()
                                            render_summary.refresh()
                                            if on_cart_changed:
                                                on_cart_changed()
                                        else:
                                            ui.notify(f'Sản phẩm chỉ còn {stock} máy trong kho!', type='warning')

                                def remove_item(index=idx):
                                    c = app.storage.user.get('cart', [])
                                    if index < len(c):
                                        del c[index]
                                        app.storage.user['cart'] = c
                                        render_items.refresh()
                                        render_summary.refresh()
                                        if on_cart_changed:
                                            on_cart_changed()

                                ui.button('-', on_click=dec_qty).classes('w-7 h-7 text-xs font-bold text-gray-600').props('flat dense')
                                ui.label(str(qty)).classes('w-7 text-center font-bold text-xs text-gray-900')
                                ui.button('+', on_click=inc_qty).classes('w-7 h-7 text-xs font-bold text-gray-600').props('flat dense')

                            # Item Total & Delete
                            with ui.row().classes('items-center gap-3 justify-end'):
                                ui.label(f'{item_total:,.0f} ₫').classes('text-xs font-bold text-gray-900 min-w-[80px] text-right')
                                ui.button(icon='delete_outline', on_click=remove_item).classes('text-gray-400 hover:text-red-600').props('flat round dense size=sm')

                render_items()

                # ── Mã Voucher (FR-03, TC-08, TC-09) ──
                with ui.column().classes('w-full mt-6 pt-4 border-t border-gray-100 gap-2'):
                    ui.label('MÃ KHUYẾN MÃI (VOUCHER)').classes('text-[11px] font-bold text-gray-400 uppercase tracking-wider')
                    with ui.row().classes('w-full items-center gap-2'):
                        voucher_input = ui.input(placeholder='Nhập mã (VD: SALE500K, HELLO...)').classes('flex-1 bg-gray-50').props('outlined dense')
                        voucher_msg = ui.label('').classes('text-xs font-medium w-full hidden')

                        def apply_voucher():
                            code = (voucher_input.value or '').strip().upper()
                            if not code:
                                voucher_msg.text = 'Vui lòng nhập mã khuyến mãi'
                                voucher_msg.classes('text-red-500', remove='text-green-600 hidden')
                                return

                            curr_cart = app.storage.user.get('cart', [])
                            cart_total = sum(i['price'] * i['qty'] for i in curr_cart)

                            prom_svc = getattr(container, 'promotion_service', None)
                            if not prom_svc:
                                voucher_msg.text = 'Dịch vụ khuyến mãi chưa sẵn sàng!'
                                voucher_msg.classes('text-red-500', remove='text-green-600 hidden')
                                return

                            is_valid, res = prom_svc.check_promotion(code, cart_total)
                            if is_valid:
                                applied_voucher['code'] = code
                                applied_voucher['discount'] = float(res)
                                voucher_msg.text = f'Áp dụng thành công voucher {code}! Giảm {float(res):,.0f} ₫'
                                voucher_msg.classes('text-green-600', remove='text-red-500 hidden')
                                render_summary.refresh()
                            else:
                                applied_voucher['code'] = ''
                                applied_voucher['discount'] = 0
                                voucher_msg.text = f'{res}'
                                voucher_msg.classes('text-red-500', remove='text-green-600 hidden')
                                render_summary.refresh()

                        ui.button('Áp Dụng', on_click=apply_voucher).classes('bg-blue-600 text-white font-medium px-4 h-10 rounded-xl text-xs').props('no-caps')

                # ── Thông tin khách hàng đặt hàng (FR-07, FR-08, TC-10, TC-12) ──
                with ui.column().classes('w-full mt-4 pt-4 border-t border-gray-100 gap-3'):
                    ui.label('THÔNG TIN GIAO HÀNG & BẢO HÀNH').classes('text-[11px] font-bold text-gray-400 uppercase tracking-wider')
                    user_info = app.storage.user
                    cust_name_input = ui.input('Họ và Tên người nhận *', value=user_info.get('full_name', '')).classes('w-full').props('outlined dense')
                    cust_phone_input = ui.input('Số điện thoại (10 chữ số) *', placeholder='VD: 0941241213').classes('w-full').props('outlined dense')
                    cust_addr_input = ui.input('Địa chỉ nhận hàng (Tùy chọn)').classes('w-full').props('outlined dense')

        # ── Footer / Checkout Summary ──
        if cart:
            with ui.column().classes('w-full p-6 bg-gray-50 border-t border-gray-200 gap-3'):
                @ui.refreshable
                def render_summary():
                    curr_cart = app.storage.user.get('cart', [])
                    subtotal = sum(i['price'] * i['qty'] for i in curr_cart)
                    discount = applied_voucher['discount']
                    final_pay = max(0.0, subtotal - discount)

                    with ui.column().classes('w-full gap-1'):
                        with ui.row().classes('w-full justify-between items-center text-xs text-gray-500'):
                            ui.label('Tạm tính:')
                            ui.label(f'{subtotal:,.0f} ₫').classes('font-semibold text-gray-700')
                        
                        if discount > 0:
                            with ui.row().classes('w-full justify-between items-center text-xs text-emerald-600'):
                                ui.label(f'Khuyến mãi ({applied_voucher["code"]}):')
                                ui.label(f'-{discount:,.0f} ₫').classes('font-bold')

                        with ui.row().classes('w-full justify-between items-center pt-2 border-t border-gray-200 mt-1'):
                            ui.label('TỔNG THANH TOÁN:').classes('text-sm font-bold text-gray-800')
                            ui.label(f'{final_pay:,.0f} ₫').classes('text-2xl font-extrabold text-red-600')

                render_summary()

                # Action Buttons
                with ui.row().classes('w-full justify-between items-center gap-3 mt-2'):
                    ui.button('Xóa Tất Cả', on_click=lambda: [
                        app.storage.user.update({'cart': []}),
                        dlg.close(),
                        ui.notify('Đã xóa toàn bộ sản phẩm trong giỏ', type='info'),
                        on_cart_changed() if on_cart_changed else None,
                    ]).classes('rounded-xl h-11 px-4 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100').props('flat no-caps')

                    def handle_checkout():
                        if not app.storage.user.get('authenticated'):
                            ui.notify('Vui lòng đăng nhập tài khoản trước khi thanh toán đơn hàng!', type='warning')
                            dlg.close()
                            ui.navigate.to('/login')
                            return

                        curr_cart = app.storage.user.get('cart', [])
                        if not curr_cart:
                            ui.notify('Giỏ hàng trống!', type='warning')
                            return

                        c_name = (cust_name_input.value or '').strip()
                        c_phone = (cust_phone_input.value or '').strip()
                        c_addr = (cust_addr_input.value or '').strip()

                        if not c_name or not c_phone:
                            ui.notify('Vui lòng nhập Họ tên và Số điện thoại nhận hàng!', type='warning')
                            return

                        if len(c_phone) != 10 or not c_phone.isdigit() or not c_phone.startswith('0'):
                            ui.notify('Số điện thoại phải gồm 10 chữ số và bắt đầu bằng số 0!', type='warning')
                            return

                        # 1. Tìm hoặc tạo Customer trong CSDL để gán customer_id (FR-07)
                        cust_id = None
                        cust_svc = getattr(container, 'customer_service', None)
                        cust_dao = getattr(container, 'customer_dao', None)
                        if cust_svc:
                            cust_id = cust_svc.get_or_create_customer_by_phone(c_phone, c_name, c_addr)
                        elif cust_dao:
                            cust_row = cust_dao.get_customer_by_phone(c_phone)
                            if cust_row:
                                cust_id = cust_row[0]
                            else:
                                ok_add, _ = cust_dao.add_customer(c_name, c_phone, '', c_addr)
                                if ok_add:
                                    n_cust = cust_dao.get_customer_by_phone(c_phone)
                                    if n_cust:
                                        cust_id = n_cust[0]

                        # 2. Tính tiền và thực thi transaction
                        subtotal = sum(i['price'] * i['qty'] for i in curr_cart)
                        discount = applied_voucher['discount']
                        final_pay = max(0.0, subtotal - discount)
                        voucher_code = applied_voucher['code']

                        # Chuyển đổi định dạng cart_items phù hợp cho OrderDAO và Exporter
                        items_payload = []
                        for i in curr_cart:
                            items_payload.append({
                                'id': i['id'],
                                'name': i['name'],
                                'price': float(i['price']),
                                'qty': int(i['qty']),
                                'quantity': int(i['qty']),
                                'total': float(i['price']) * int(i['qty']),
                            })

                        user_id = app.storage.user.get('id')
                        order_svc = getattr(container, 'order_service', None)
                        if not order_svc:
                            ui.notify('Dịch vụ đơn hàng chưa sẵn sàng!', type='negative')
                            return

                        ok, msg = order_svc.create_order(
                            user_id, voucher_code, final_pay, items_payload, cust_id
                        )

                        if ok:
                            # Trích xuất mã đơn hàng từ message "Thanh toán thành công! Mã đơn: 33"
                            order_id = "NEW"
                            if "Mã đơn: " in msg:
                                order_id = msg.split("Mã đơn: ")[-1].strip()

                            # Hiển thị thông báo Toast thành công tức thời
                            ui.notify(
                                f'Đặt hàng thành công! Mã đơn: #{order_id} • Tổng tiền: {final_pay:,.0f} ₫',
                                type='positive',
                                position='top',
                                timeout=6000,
                                close_button='Đóng'
                            )

                            # 3. Xuất hóa đơn PDF tự động (FR-04)
                            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                            export_dir = os.path.join(base_dir, 'exports')
                            os.makedirs(export_dir, exist_ok=True)
                            pdf_filename = f"hoadon_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            pdf_path = os.path.join(export_dir, pdf_filename)
                            
                            pdf_ok = False
                            exporter = getattr(container, 'exporter', None)
                            if exporter:
                                pdf_ok, _ = exporter.print_invoice_pdf(
                                    order_id, c_name, items_payload, final_pay, pdf_path
                                )

                            # Dọn sạch giỏ
                            app.storage.user['cart'] = []
                            dlg.close()
                            if on_cart_changed:
                                on_cart_changed()

                            # 4. Hiển thị Dialog thông báo thành công
                            _show_success_dialog(order_id, c_name, c_phone, final_pay, pdf_path if pdf_ok else None)
                        else:
                            ui.notify(f'Lỗi đặt hàng: {msg}', type='negative')

                    ui.button('Xác Nhận Đặt Hàng', on_click=handle_checkout).classes(
                        'flex-1 bg-[#111827] text-white font-bold h-12 rounded-xl text-sm hover:opacity-95 shadow-md transition-transform hover:scale-[1.01]'
                    ).props('no-caps icon=check_circle')

    dlg.open()


def _show_success_dialog(order_id, cust_name, cust_phone, total_amount, pdf_filepath=None):
    with ui.dialog() as dlg, ui.card().classes('w-[520px] max-w-[95vw] rounded-3xl p-8 bg-white shadow-2xl items-center text-center flex-col gap-4'):
        with ui.element('div').classes('w-16 h-16 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mb-1'):
            ui.icon('verified', size='36px')

        ui.label('ĐẶT HÀNG THÀNH CÔNG!').classes('text-2xl font-extrabold text-gray-900 tracking-tight')
        ui.label(f'Mã hóa đơn: #{order_id}').classes('text-sm font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full')
        
        ui.label(
            f'Cảm ơn Quý khách {cust_name}! Đơn hàng đã được lưu vào hệ thống CSDL, '
            f'trừ số lượng tồn kho tự động và tích lũy điểm thưởng thành viên theo số điện thoại {cust_phone}.'
        ).classes('text-xs text-gray-600 leading-relaxed max-w-md')

        with ui.column().classes('w-full p-4 rounded-2xl bg-gray-50 border border-gray-100 text-left gap-1 my-2'):
            with ui.row().classes('w-full justify-between text-xs'):
                ui.label('Tổng thanh toán:').classes('text-gray-500')
                ui.label(f'{total_amount:,.0f} ₫').classes('font-bold text-red-600')
            with ui.row().classes('w-full justify-between text-xs'):
                ui.label('Chính sách áp dụng:').classes('text-gray-500')
                ui.label('1 Đổi 1 trong 30 ngày').classes('font-medium text-emerald-700')
            with ui.row().classes('w-full justify-between text-xs'):
                ui.label('Tra cứu bảo hành:').classes('text-gray-500')
                ui.label(f'Bằng SĐT: {cust_phone}').classes('font-semibold text-blue-600')

        with ui.column().classes('w-full gap-2 mt-2'):
            if pdf_filepath and os.path.exists(pdf_filepath):
                filename = os.path.basename(pdf_filepath)
                ui.button(
                    'Tải Hóa Đơn PDF (A4)',
                    on_click=lambda fp=pdf_filepath, fn=filename: (
                        ui.download(fp, fn),
                        ui.notify(f'Đang tải hóa đơn {fn}...', type='positive')
                    )
                ).classes(
                    'w-full bg-[#0071e3] text-white font-semibold h-11 rounded-xl shadow-xs'
                ).props('no-caps icon=download')

            ui.button('Xem Lịch Sử Đơn Hàng', on_click=lambda: (dlg.close(), ui.navigate.to('/admin/orders'))).classes(
                'w-full bg-gray-100 text-gray-800 font-medium h-11 rounded-xl hover:bg-gray-200'
            ).props('flat no-caps')

            ui.button('Tiếp Tục Mua Sắm', on_click=lambda: (dlg.close(), ui.navigate.to('/'))).classes(
                'w-full text-gray-500 hover:text-gray-900 text-xs'
            ).props('flat no-caps')

    dlg.open()
