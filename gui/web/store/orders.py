from nicegui import ui, app
from gui.web.store.layout import store_layout
from logic.service_container import get_container
from datetime import datetime


@ui.page('/orders')
@store_layout('Đơn Hàng Của Tôi', active_tab='orders')
def store_orders_page():
    user = app.storage.user
    if not user.get('authenticated'):
        ui.navigate.to('/login')
        return

    role = user.get('role')
    if role in ('admin', 'staff'):
        ui.navigate.to('/admin/orders')
        return

    user_id = user.get('id')
    container = get_container()

    # Top Header
    with ui.row().classes('w-full justify-between items-center mb-6 flex-wrap gap-4'):
        with ui.column().classes('gap-1'):
            ui.label('Đơn Hàng Của Tôi').classes('text-3xl font-extrabold text-gray-900 tracking-tight')
            ui.label('Theo dõi trạng thái và lịch sử các đơn hàng bạn đã mua sắm tại cửa hàng.').classes('text-sm text-gray-500')
        ui.button('Tra Cứu Bảo Hành Thiết Bị', icon='verified_user', on_click=lambda: ui.navigate.to('/warranty')).classes(
            'bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold px-5 h-10 rounded-xl'
        ).props('flat no-caps')

    orders_data = []
    order_items_map = {}

    if container.db_manager:
        conn = container.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                # 1. Lấy danh sách đơn hàng
                cursor.execute("""
                    SELECT o.id, o.total_amount, o.status, o.created_at, o.voucher_code,
                           (SELECT COUNT(*) FROM order_details WHERE order_id = o.id) as item_count
                    FROM orders o
                    WHERE o.user_id = %s
                    ORDER BY o.id DESC
                """, (user_id,))
                orders_data = cursor.fetchall()

                # 2. Lấy chi tiết sản phẩm
                if orders_data:
                    order_ids = [str(o['id']) for o in orders_data]
                    format_strings = ','.join(['%s'] * len(order_ids))
                    cursor.execute(f"""
                        SELECT od.order_id, od.quantity, od.price_at_sale, p.name as product_name,
                               p.warranty_time, p.spec_cpu as cpu, p.spec_ram as ram
                        FROM order_details od
                        JOIN products p ON od.product_id = p.id
                        WHERE od.order_id IN ({format_strings})
                    """, tuple(order_ids))
                    items = cursor.fetchall()
                    for it in items:
                        oid = it['order_id']
                        if oid not in order_items_map:
                            order_items_map[oid] = []
                        order_items_map[oid].append(it)
            except Exception as e:
                print(f"Error fetching orders: {e}")
            finally:
                if cursor:
                    cursor.close()
                conn.close()

    if not orders_data:
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-3xl border border-gray-100 shadow-sm'):
            ui.icon('receipt_long', size='64px').classes('text-gray-300 mb-4')
            ui.label('Chưa có đơn hàng nào').classes('text-xl font-bold text-gray-800')
            ui.label('Bạn chưa thực hiện bất kỳ giao dịch mua sắm laptop nào.').classes('text-sm text-gray-500 mt-2')
            ui.button('Mua Sắm Ngay', on_click=lambda: ui.navigate.to('/')).classes('mt-6 bg-[#0071e3] text-white rounded-full px-8 h-12 font-semibold shadow-md hover:bg-blue-600').props('no-caps')
        return

    # Display orders in cards
    with ui.column().classes('w-full gap-5'):
        for order in orders_data:
            oid = order['id']
            dt_obj = order['created_at']
            date_str = dt_obj.strftime('%d/%m/%Y %H:%M') if isinstance(dt_obj, datetime) else str(dt_obj)
            
            # Status badge styling
            status = str(order['status']).lower()
            badge_color = 'bg-gray-100 text-gray-600'
            status_text = order['status']
            if status == 'completed' or status == 'hoàn thành':
                badge_color = 'bg-emerald-50 text-emerald-700 border-emerald-200'
                status_text = 'Hoàn tất'
            elif status == 'đang giao':
                badge_color = 'bg-blue-50 text-blue-700 border-blue-200'
            elif status == 'chờ xử lý':
                badge_color = 'bg-amber-50 text-amber-700 border-amber-200'
            elif status == 'đã hủy':
                badge_color = 'bg-rose-50 text-rose-700 border-rose-200'

            with ui.card().classes('w-full p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow bg-white'):
                # Card Header
                with ui.row().classes('w-full justify-between items-start pb-4 border-b border-gray-100 flex-wrap gap-2'):
                    with ui.row().classes('items-center gap-3'):
                        ui.label(f"Đơn hàng #{oid}").classes('font-bold text-lg text-gray-900')
                        ui.label(date_str).classes('text-xs text-gray-400')
                        if order.get('voucher_code'):
                            ui.label(f"Voucher: {order['voucher_code']}").classes('text-[11px] font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-100')
                    
                    ui.label(status_text).classes(f'px-3 py-1 rounded-full text-xs font-semibold border {badge_color}')

                # Card Body: Product List
                items = order_items_map.get(oid, [])
                with ui.column().classes('w-full py-4 gap-2.5'):
                    for it in items:
                        with ui.row().classes('w-full justify-between items-center py-2 px-3 rounded-xl bg-gray-50/70 border border-gray-100/80'):
                            with ui.row().classes('items-center gap-3'):
                                ui.icon('laptop_mac', size='20px').classes('text-blue-600')
                                ui.label(it['product_name']).classes('font-semibold text-sm text-gray-900')
                            ui.label(f"SL: {it['quantity']} • {int(it['price_at_sale']):,} ₫".replace(",", ".")).classes('text-xs font-medium text-gray-600')

                # Card Footer: Total Amount & Action Buttons
                def show_order_detail(ord_data=order, ord_items=items):
                    with ui.dialog() as dlg, ui.card().classes('w-[650px] max-w-[96vw] rounded-[24px] p-6 bg-white shadow-2xl'):
                        with ui.row().classes('w-full justify-between items-center pb-4 border-b border-gray-100'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('receipt_long', size='24px').classes('text-blue-600')
                                ui.label(f"Chi Tiết Đơn Hàng #{ord_data['id']}").classes('text-lg font-bold text-gray-900')
                            ui.button(icon='close', on_click=dlg.close).props('flat round dense')

                        with ui.column().classes('w-full py-4 gap-3'):
                            with ui.row().classes('w-full justify-between text-xs text-gray-500'):
                                ui.label(f"Thời gian: {date_str}")
                                ui.label(f"Trạng thái: {status_text}").classes('font-semibold text-emerald-600')

                            ui.separator().classes('my-1 opacity-50')
                            ui.label('DANH SÁCH THIẾT BỊ MUA SẮM').classes('text-[11px] font-bold text-gray-400 uppercase tracking-wider')

                            for p in ord_items:
                                w_time = p.get('warranty_time', 12) or 12
                                with ui.card().classes('w-full p-4 rounded-xl bg-gray-50/80 border border-gray-100 shadow-none'):
                                    with ui.row().classes('w-full justify-between items-start'):
                                        with ui.column().classes('gap-1'):
                                            ui.label(p['product_name']).classes('font-bold text-sm text-gray-900')
                                            specs_snippet = [s for s in (p.get('cpu'), p.get('ram')) if s]
                                            if specs_snippet:
                                                ui.label(' • '.join(specs_snippet)).classes('text-xs text-gray-500')
                                            ui.label(f"Bảo hành chính hãng: {w_time} tháng").classes('text-xs font-semibold text-blue-600')
                                        ui.label(f"{int(p['price_at_sale']):,} ₫ × {p['quantity']}").classes('font-bold text-sm text-gray-800')

                            if ord_data.get('voucher_code'):
                                with ui.row().classes('w-full justify-between items-center px-2 py-1 bg-purple-50 rounded-lg text-xs text-purple-800'):
                                    ui.label('Mã khuyến mãi áp dụng:')
                                    ui.label(ord_data['voucher_code']).classes('font-bold')

                            with ui.row().classes('w-full justify-between items-center pt-3 border-t border-gray-100'):
                                ui.label('Tổng cộng thanh toán:').classes('font-bold text-base text-gray-900')
                                ui.label(f"{int(ord_data['total_amount'] or 0):,} ₫".replace(",", ".")).classes('text-2xl font-extrabold text-blue-600')

                        with ui.row().classes('w-full justify-between items-center pt-2'):
                            ui.button('Tra Cứu Hạn Bảo Hành', icon='verified_user', on_click=lambda: (dlg.close(), ui.navigate.to('/warranty'))).classes(
                                'bg-blue-50 text-blue-700 font-semibold px-4 h-10 rounded-xl text-xs hover:bg-blue-100'
                            ).props('flat no-caps')
                            ui.button('Đóng', on_click=dlg.close).classes('h-10 px-6 rounded-xl text-xs font-medium text-gray-600').props('flat no-caps')

                    dlg.open()

                with ui.row().classes('w-full justify-between items-center pt-4 border-t border-gray-100 flex-wrap gap-3'):
                    with ui.row().classes('items-center gap-2'):
                        ui.button('Xem chi tiết', icon='visibility', on_click=show_order_detail).classes(
                            'text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-xl'
                        ).props('flat dense no-caps')
                        ui.button('Tra cứu bảo hành', icon='verified_user', on_click=lambda: ui.navigate.to('/warranty')).classes(
                            'text-xs font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-xl'
                        ).props('flat dense no-caps')

                    with ui.row().classes('items-baseline gap-2'):
                        ui.label('Tổng thanh toán:').classes('text-xs text-gray-500')
                        ui.label(f"{int(order['total_amount'] or 0):,} ₫".replace(",", ".")).classes('text-xl font-extrabold text-blue-600')
