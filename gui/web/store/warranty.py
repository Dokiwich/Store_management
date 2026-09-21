from nicegui import ui, app
from gui.web.store.layout import store_layout
from logic.service_container import get_container
from datetime import datetime, timedelta


@ui.page('/warranty')
@store_layout('Tra Cứu Bảo Hành', active_tab='warranty')
def store_warranty_page():
    user = app.storage.user
    role = user.get('role')
    if role in ('admin', 'staff'):
        ui.navigate.to('/admin/warranty')
        return

    container = get_container()
    authenticated = user.get('authenticated', False)
    user_id = user.get('id')
    user_fullname = user.get('full_name', user.get('username', 'Khách hàng'))

    state = {'results': [], 'initial_loaded': False, 'cust_phone': ''}

    # Fetch customer phone if logged in (customers doesn't have user_id; join via orders)
    if authenticated and user_id and container.db_manager:
        conn = container.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT c.phone FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE o.user_id = %s AND c.phone IS NOT NULL AND c.phone != ''
                    ORDER BY o.id DESC LIMIT 1
                """, (user_id,))
                cust_row = cursor.fetchone()
                if cust_row and cust_row.get('phone'):
                    state['cust_phone'] = cust_row['phone']
            except Exception as e:
                print(f"Error fetching customer phone: {e}")
            finally:
                if cursor:
                    cursor.close()
                conn.close()

    def fetch_warranties(kw=None):
        conn = container.db_manager.get_connection() if container.db_manager else None
        if not conn:
            return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            if kw and len(kw.strip()) > 0:
                kw_clean = kw.strip()
                sql = """
                    SELECT o.id as order_id, p.id as product_id, p.name as product_name, 
                           od.price_at_sale, o.created_at, p.warranty_time,
                           p.spec_cpu as cpu, p.spec_ram as ram, p.spec_hard_drive as hard_drive,
                           COALESCE(c.phone, '') as phone, COALESCE(c.full_name, 'Khách hàng') as customer_name
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    JOIN order_details od ON o.id = od.order_id
                    JOIN products p ON od.product_id = p.id
                    WHERE c.phone LIKE %s OR o.id = %s OR p.name LIKE %s
                    ORDER BY o.created_at DESC
                """
                cursor.execute(sql, (f"%{kw_clean}%", kw_clean, f"%{kw_clean}%"))
            elif authenticated and user_id:
                sql = """
                    SELECT o.id as order_id, p.id as product_id, p.name as product_name, 
                           od.price_at_sale, o.created_at, p.warranty_time,
                           p.spec_cpu as cpu, p.spec_ram as ram, p.spec_hard_drive as hard_drive,
                           COALESCE(c.phone, '') as phone, COALESCE(c.full_name, 'Khách hàng') as customer_name
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    JOIN order_details od ON o.id = od.order_id
                    JOIN products p ON od.product_id = p.id
                    WHERE o.user_id = %s OR (c.phone = %s AND %s != '')
                    ORDER BY o.created_at DESC
                """
                cursor.execute(sql, (user_id, state['cust_phone'], state['cust_phone']))
            else:
                return []
            return cursor.fetchall()
        except Exception as ex:
            print(f"Error fetching warranty: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            conn.close()

    # Load initial results if logged in
    if authenticated:
        state['results'] = fetch_warranties()
        state['initial_loaded'] = True

    # ── Page Header ──
    with ui.column().classes('gap-1 mb-6'):
        ui.label('Tra Cứu Thông Tin Bảo Hành').classes('text-3xl font-extrabold text-gray-900 tracking-tight')
        ui.label('Kiểm tra thời hạn bảo hành chính hãng và chính sách hậu mãi của các thiết bị laptop đã mua.').classes('text-sm text-gray-500')

    # ── Search Card ──
    with ui.card().classes('w-full p-6 mb-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
        with ui.row().classes('w-full gap-4 items-end flex-wrap'):
            with ui.column().classes('flex-1 gap-1 min-w-[280px]'):
                ui.label('Tra cứu theo Số điện thoại, Mã đơn hàng (#ID) hoặc Tên laptop:').classes('font-medium text-gray-700 text-xs')
                default_kw = state['cust_phone'] if not state['results'] and state['cust_phone'] else ''
                search_input = ui.input(value=default_kw, placeholder='Ví dụ: 0912345678, mã #45 hoặc tên máy...').classes('w-full').props('outlined dense clearable')

            def handle_search():
                kw = search_input.value
                if not kw or len(kw.strip()) < 2:
                    if authenticated:
                        state['results'] = fetch_warranties()
                    else:
                        ui.notify('Vui lòng nhập số điện thoại hoặc mã đơn hàng để tra cứu!', type='warning')
                        state['results'] = []
                else:
                    state['results'] = fetch_warranties(kw)
                render_results.refresh()

            ui.button('Tra Cứu', icon='search', on_click=handle_search).classes(
                'bg-[#0071e3] text-white px-8 h-10 rounded-xl font-semibold shadow-sm hover:bg-blue-600'
            ).props('no-caps')

            search_input.on('keydown.enter', handle_search)

    # ── Detail Dialog Function ──
    def open_warranty_detail_modal(item, status_info):
        buy_date = item['created_at']
        buy_date_str = buy_date.strftime('%d/%m/%Y') if hasattr(buy_date, 'strftime') else str(buy_date)[:10]
        warr_months = int(item['warranty_time']) if item['warranty_time'] else 12

        with ui.dialog() as dlg, ui.card().classes('w-[620px] max-w-[96vw] rounded-[24px] p-6 bg-white shadow-2xl'):
            with ui.row().classes('w-full justify-between items-center pb-4 border-b border-gray-100'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('verified', size='24px').classes('text-blue-600')
                    ui.label('Thông Tin Chi Tiết Bảo Hành').classes('text-lg font-bold text-gray-900')
                ui.button(icon='close', on_click=dlg.close).props('flat round dense')

            with ui.column().classes('w-full py-3 gap-3 text-sm'):
                # Product Header
                with ui.row().classes('w-full justify-between items-start bg-gray-50 p-4 rounded-xl border border-gray-100'):
                    with ui.column().classes('gap-0.5'):
                        ui.label(item['product_name']).classes('font-bold text-base text-gray-900')
                        specs = [s for s in (item.get('cpu'), item.get('ram'), item.get('hard_drive')) if s]
                        if specs:
                            ui.label(' • '.join(specs)).classes('text-xs text-gray-500')
                        ui.label(f"Mã đơn hàng: #{item['order_id']}").classes('text-xs text-blue-600 font-semibold mt-1')
                    
                    ui.label(status_info['label']).classes(f"px-3 py-1 rounded-full text-xs font-bold {status_info['badge_class']}")

                # Warranty Dates Grid
                with ui.row().classes('w-full grid grid-cols-3 gap-2 py-2 text-center'):
                    with ui.column().classes('p-2 bg-blue-50/50 rounded-xl border border-blue-100/60'):
                        ui.label('NGÀY MUA').classes('text-[10px] font-bold text-gray-400')
                        ui.label(buy_date_str).classes('font-bold text-gray-800 text-sm')
                    with ui.column().classes('p-2 bg-blue-50/50 rounded-xl border border-blue-100/60'):
                        ui.label('THỜI HẠN').classes('text-[10px] font-bold text-gray-400')
                        ui.label(f"{warr_months} Tháng").classes('font-bold text-blue-600 text-sm')
                    with ui.column().classes('p-2 bg-blue-50/50 rounded-xl border border-blue-100/60'):
                        ui.label('HẾT HẠN').classes('text-[10px] font-bold text-gray-400')
                        ui.label(status_info['exp_str']).classes('font-bold text-gray-800 text-sm')

                # Policy details
                ui.separator().classes('my-1 opacity-50')
                ui.label('CHÍNH SÁCH BẢO HÀNH CHÍNH HÃNG').classes('text-[11px] font-bold text-gray-400 uppercase tracking-wider')

                with ui.column().classes('gap-2 text-xs text-gray-600 bg-gray-50/60 p-3 rounded-xl border border-gray-100'):
                    ui.label('• 1 Đổi 1 trong 30 ngày đầu tiên nếu máy phát sinh lỗi phần cứng từ nhà sản xuất.')
                    ui.label('• Bảo hành sửa chữa thay thế linh kiện chính hãng miễn phí trong suốt thời hạn bảo hành.')
                    ui.label('• Điều kiện: Máy còn nguyên vẹn tem bảo hành, không có dấu hiệu cấn móp nặng, rơi vỡ, chập cháy hoặc ngấm nước.')

                with ui.row().classes('w-full justify-between items-center text-xs text-gray-500 pt-1'):
                    ui.label('Hotline hỗ trợ CSKH: 1800 1234 (Miễn phí)').classes('font-semibold text-blue-700')
                    ui.label('Địa chỉ: 123 Đường Công Nghệ, Q.1, TP. HCM')

            with ui.row().classes('w-full justify-end pt-3 border-t border-gray-100'):
                ui.button('Đóng', on_click=dlg.close).classes('h-10 px-6 rounded-xl font-medium text-xs text-gray-700').props('flat no-caps')

        dlg.open()

    # ── Results Render ──
    @ui.refreshable
    def render_results():
        if not state['results']:
            with ui.column().classes('w-full items-center justify-center py-16 text-center bg-white rounded-2xl border border-gray-100 shadow-sm'):
                ui.icon('verified_user', size='56px').classes('text-gray-300 mb-3')
                ui.label('Không tìm thấy thông tin bảo hành').classes('text-lg font-bold text-gray-800')
                if authenticated:
                    ui.label('Bạn chưa có thiết bị nào đang áp dụng bảo hành hoặc vui lòng nhập số điện thoại để tra cứu.').classes('text-xs text-gray-500 mt-1 max-w-md')
                else:
                    ui.label('Vui lòng nhập Số điện thoại hoặc Mã đơn hàng vào ô tra cứu bên trên.').classes('text-xs text-gray-500 mt-1 max-w-md')
            return

        with ui.column().classes('w-full gap-4'):
            if authenticated:
                with ui.row().classes('w-full items-center gap-2 px-1 text-xs text-gray-500'):
                    ui.icon('check_circle', size='16px').classes('text-emerald-600')
                    ui.label(f'Tìm thấy {len(state["results"])} thiết bị bảo hành gắn liền với tài khoản của bạn:').classes('font-medium')

            for item in state['results']:
                warr_months = int(item['warranty_time']) if item['warranty_time'] else 12
                buy_date = item['created_at']
                buy_date_str = buy_date.strftime('%d/%m/%Y') if hasattr(buy_date, 'strftime') else str(buy_date)[:10]

                exp_date_str = 'Không bảo hành'
                status = 'Hết Hạn'
                status_color = 'bg-rose-50 text-rose-700 border-rose-200'
                days_left = 0

                if warr_months > 0 and hasattr(buy_date, 'year'):
                    exp_date = buy_date + timedelta(days=warr_months * 30)
                    exp_date_str = exp_date.strftime('%d/%m/%Y')
                    diff = exp_date - datetime.now()
                    days_left = diff.days
                    if days_left > 0:
                        status = f'Còn Hạn ({days_left} ngày)'
                        status_color = 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    else:
                        status = 'Hết Hạn Bảo Hành'
                        status_color = 'bg-gray-100 text-gray-600 border-gray-200'

                status_info = {
                    'label': status,
                    'badge_class': status_color,
                    'exp_str': exp_date_str,
                    'days_left': days_left,
                }

                with ui.card().classes('w-full p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow bg-white'):
                    with ui.row().classes('w-full justify-between items-start mb-3 flex-wrap gap-2'):
                        with ui.column().classes('gap-0.5'):
                            ui.label(item['product_name']).classes('font-bold text-lg text-gray-900')
                            with ui.row().classes('items-center gap-2'):
                                ui.label(f"Mã Đơn Hàng: #{item['order_id']}").classes('text-xs text-gray-500')
                                specs = [s for s in (item.get('cpu'), item.get('ram'), item.get('hard_drive')) if s]
                                if specs:
                                    ui.label('• ' + ' - '.join(specs)).classes('text-xs text-gray-400')

                        ui.label(status).classes(f'px-3.5 py-1 rounded-full text-xs font-semibold border {status_color}')

                    ui.separator().classes('my-2 opacity-50')

                    with ui.row().classes('w-full justify-between items-center flex-wrap gap-4 pt-1'):
                        with ui.row().classes('gap-6 items-center flex-wrap'):
                            with ui.column().classes('gap-0.5'):
                                ui.label('Ngày Mua').classes('text-[10px] font-bold text-gray-400 uppercase tracking-wider')
                                ui.label(buy_date_str).classes('font-semibold text-xs text-gray-800')

                            with ui.column().classes('gap-0.5'):
                                ui.label('Thời Gian BH').classes('text-[10px] font-bold text-gray-400 uppercase tracking-wider')
                                ui.label(f"{warr_months} tháng").classes('font-semibold text-xs text-gray-800')

                            with ui.column().classes('gap-0.5'):
                                ui.label('Ngày Hết Hạn').classes('text-[10px] font-bold text-gray-400 uppercase tracking-wider')
                                ui.label(exp_date_str).classes('font-bold text-xs ' + ('text-emerald-700' if days_left > 0 else 'text-gray-600'))

                        ui.button('Xem chi tiết', icon='visibility', on_click=lambda it=item, si=status_info: open_warranty_detail_modal(it, si)).classes(
                            'bg-blue-50 text-blue-600 hover:bg-blue-100 text-xs font-semibold px-4 h-9 rounded-xl shadow-none'
                        ).props('flat dense no-caps')

    render_results()
