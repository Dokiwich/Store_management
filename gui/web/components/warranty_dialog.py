"""Warranty Quick Lookup Dialog — Tra cứu bảo hành nổi tại chỗ mọi lúc không chuyển trang."""

from datetime import datetime
from nicegui import ui
from logic.service_container import get_container


def open_warranty_dialog(prefill_kw: str = ''):
    container = get_container()
    state = {'results': [], 'searched': bool(prefill_kw)}

    def fetch_data(kw: str):
        if not kw or not kw.strip():
            state['results'] = []
            state['searched'] = False
            render_results.refresh()
            return

        kw_clean = kw.strip()
        conn = container.db_manager.get_connection() if container.db_manager else None
        if not conn:
            ui.notify('Không thể kết nối cơ sở dữ liệu', type='negative')
            return

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT o.id as order_id, COALESCE(c.full_name, 'Khách vãng lai') as customer_name,
                       c.phone, p.name as product_name, od.price_at_sale, o.created_at, p.warranty_time
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                JOIN order_details od ON o.id = od.order_id
                JOIN products p ON od.product_id = p.id
                WHERE c.phone LIKE %s OR o.id LIKE %s OR p.name LIKE %s
                ORDER BY o.created_at DESC LIMIT 30
            """
            param = f"%{kw_clean}%"
            cursor.execute(sql, (param, param, param))
            state['results'] = cursor.fetchall()
            state['searched'] = True
            render_results.refresh()
        except Exception as e:
            print(f"Error fetching warranty in dialog: {e}")
            ui.notify(f'Lỗi tra cứu: {e}', type='negative')
        finally:
            if cursor:
                cursor.close()
            conn.close()

    with ui.dialog() as dlg, ui.card().classes(
        'w-[760px] max-w-[96vw] rounded-[24px] p-0 overflow-hidden bg-white shadow-2xl flex flex-col'
    ):
        # ── Header ──
        with ui.row().classes('w-full justify-between items-center px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-blue-50/70 to-indigo-50/70'):
            with ui.row().classes('items-center gap-3'):
                with ui.element('div').classes('w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20'):
                    ui.icon('verified_user', size='22px')
                with ui.column().classes('gap-0'):
                    ui.label('Tra Cứu Bảo Hành Thiết Bị').classes('text-lg font-bold text-gray-900 leading-tight')
                    ui.label('Kiểm tra nhanh thời hạn và chính sách bảo hành chính hãng').classes('text-xs text-gray-500')
            ui.button(icon='close', on_click=dlg.close).props('flat round dense color=grey-7').classes('hover:bg-gray-100')

        # ── Search Bar Section ──
        with ui.column().classes('w-full px-6 pt-5 pb-3 gap-2 bg-gray-50/40 border-b border-gray-100'):
            with ui.row().classes('w-full gap-3 items-center'):
                search_input = ui.input(
                    placeholder='Nhập Số điện thoại, Mã đơn hàng (#ID) hoặc Tên laptop...',
                    value=prefill_kw
                ).classes('flex-1 bg-white rounded-xl text-sm').props('outlined dense clearable')
                
                search_btn = ui.button(
                    'Tra Cứu',
                    icon='search',
                    on_click=lambda: fetch_data(search_input.value)
                ).classes('bg-[#0071e3] text-white px-6 h-10 rounded-xl font-semibold shadow-sm hover:bg-blue-600').props('no-caps')

                search_input.on('keydown.enter', lambda: fetch_data(search_input.value))

            with ui.row().classes('items-center gap-2 text-xs text-gray-400'):
                ui.icon('lightbulb', size='15px').classes('text-amber-500')
                ui.label('Gợi ý: Bạn có thể nhập SĐT đặt hàng hoặc mã hóa đơn in trên phiếu mua hàng.')

        # ── Results Body (Scrollable) ──
        with ui.element('div').classes('p-6 overflow-y-auto flex-1 custom-scrollbar').style('max-height: 55vh; min-height: 220px;'):
            @ui.refreshable
            def render_results():
                if not state['searched']:
                    with ui.column().classes('w-full items-center justify-center py-12 text-center'):
                        ui.icon('manage_search', size='56px').classes('text-gray-300 mb-2')
                        ui.label('Sẵn sàng tra cứu').classes('font-bold text-base text-gray-700')
                        ui.label('Nhập thông tin bên trên để kiểm tra tình trạng bảo hành máy của bạn.').classes('text-xs text-gray-400 max-w-sm')
                    return

                results = state['results']
                if not results:
                    with ui.column().classes('w-full items-center justify-center py-12 text-center'):
                        ui.icon('sentiment_dissatisfied', size='52px').classes('text-amber-400 mb-2')
                        ui.label('Không tìm thấy thông tin').classes('font-bold text-base text-gray-800')
                        ui.label('Vui lòng kiểm tra lại Số điện thoại hoặc Mã đơn hàng vừa nhập.').classes('text-xs text-gray-500')
                    return

                with ui.column().classes('w-full gap-3.5'):
                    ui.label(f'Tìm thấy {len(results)} kết quả:').classes('text-xs font-bold text-gray-500 uppercase tracking-wider')

                    for r in results:
                        created_at = r['created_at']
                        date_str = created_at.strftime('%d/%m/%Y') if hasattr(created_at, 'strftime') else str(created_at)[:10]

                        # Warranty calculation
                        w_raw = r['warranty_time']
                        months = 12
                        if w_raw:
                            try:
                                nums = [int(s) for s in str(w_raw).split() if s.isdigit()]
                                if nums:
                                    months = nums[0]
                                else:
                                    months = int(w_raw)
                            except:
                                months = 12

                        is_valid = True
                        days_left = 0
                        if hasattr(created_at, 'year'):
                            diff = datetime.now() - created_at
                            days_left = (months * 30) - diff.days
                            is_valid = days_left > 0

                        status_bg = 'bg-emerald-50 text-emerald-700 border-emerald-200' if is_valid else 'bg-gray-100 text-gray-500 border-gray-200'
                        status_label = f"Còn hạn ({days_left} ngày)" if is_valid else "Đã hết hạn bảo hành"

                        with ui.card().classes('w-full p-4 rounded-2xl border border-gray-100 shadow-xs hover:border-blue-200 transition-all bg-white'):
                            with ui.row().classes('w-full justify-between items-start'):
                                with ui.column().classes('gap-1 flex-1'):
                                    with ui.row().classes('items-center gap-2'):
                                        ui.label(r['product_name']).classes('font-bold text-base text-gray-900')
                                        ui.label(f"#{r['order_id']}").classes('text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md')
                                    
                                    with ui.row().classes('items-center gap-4 text-xs text-gray-500 mt-1 flex-wrap'):
                                        with ui.row().classes('items-center gap-1'):
                                            ui.icon('person', size='15px').classes('text-gray-400')
                                            ui.label(f"{r['customer_name']} ({r['phone'] or '—'})")
                                        with ui.row().classes('items-center gap-1'):
                                            ui.icon('event', size='15px').classes('text-gray-400')
                                            ui.label(f"Ngày mua: {date_str}")
                                        with ui.row().classes('items-center gap-1'):
                                            ui.icon('timer', size='15px').classes('text-gray-400')
                                            ui.label(f"Gói BH: {months} Tháng")

                                with ui.column().classes('items-end gap-1'):
                                    ui.label(status_label).classes(f'px-3 py-1 rounded-full text-xs font-semibold border {status_bg}')
                                    price = r.get('price_at_sale')
                                    if price:
                                        ui.label(f"{int(price):,} ₫".replace(",", ".")).classes('text-xs font-bold text-gray-700 mt-1')

            render_results()

        # ── Footer ──
        with ui.row().classes('w-full justify-between items-center px-6 py-3 border-t border-gray-100 bg-gray-50/50'):
            with ui.row().classes('items-center gap-1.5 text-xs text-gray-500'):
                ui.icon('support_agent', size='16px').classes('text-blue-600')
                ui.label('Hotline hỗ trợ kỹ thuật: 1800 1234')
            ui.button('Đóng', on_click=dlg.close).props('flat dense no-caps color=grey-8').classes('font-medium text-xs px-4')

    if prefill_kw:
        fetch_data(prefill_kw)
    dlg.open()
