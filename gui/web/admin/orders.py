"""Orders module — Lịch sử bán hàng và nhập hàng (tương ứng history_tab.py)."""

from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container
import os


@ui.page('/admin/orders')
@admin_layout('Lịch Sử Hoạt Động', active_tab='orders')
def orders_page():
    container = get_container()

    with ui.row().classes('w-full justify-between items-center mb-6'):
        with ui.column().classes('gap-1'):
            ui.label("Lịch Sử Hoạt Động").classes('text-2xl font-bold text-gray-900')
            ui.label('Theo dõi toàn bộ đơn hàng bán ra và các đợt nhập kho linh kiện laptop').classes('text-sm text-gray-500')

    # Tab Container: Bán hàng vs Nhập hàng (chuẩn history_tab.py)
    with ui.tabs().classes('w-full border-b border-gray-200 mb-6') as tabs:
        tab_sales = ui.tab('sales', label='Lịch Sử Bán Hàng', icon='receipt_long')
        tab_imports = ui.tab('imports', label='Lịch Sử Nhập Hàng', icon='local_shipping')

    with ui.tab_panels(tabs, value='sales').classes('w-full bg-transparent p-0'):
        # ══════════════════════════════════════════════════════
        #  PANEL 1: LỊCH SỬ BÁN HÀNG
        # ══════════════════════════════════════════════════════
        with ui.tab_panel('sales').classes('p-0'):
            sales_data = []
            if container.db_manager:
                conn = container.db_manager.get_connection()
                if conn:
                    cursor = None
                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT o.id, COALESCE(u.full_name, u.username, 'Admin'), 
                                   COALESCE(c.full_name, 'Khách lẻ'), o.voucher_code, o.total_amount, o.status, o.created_at
                            FROM orders o
                            LEFT JOIN users u ON o.user_id = u.id
                            LEFT JOIN customers c ON o.customer_id = c.id
                            ORDER BY o.id DESC LIMIT 50
                        """)
                        sales_data = cursor.fetchall()
                    except Exception as e:
                        print(f"Error fetching sales: {e}")
                    finally:
                        if cursor: cursor.close()
                        conn.close()

            columns_sales = [
                {'name': 'id', 'label': 'MÃ ĐƠN', 'field': 'id', 'align': 'left'},
                {'name': 'staff', 'label': 'NHÂN VIÊN', 'field': 'staff', 'align': 'left'},
                {'name': 'cust', 'label': 'KHÁCH HÀNG', 'field': 'cust', 'align': 'left'},
                {'name': 'voucher', 'label': 'VOUCHER', 'field': 'voucher', 'align': 'center'},
                {'name': 'total', 'label': 'TỔNG TIỀN', 'field': 'total', 'align': 'right'},
                {'name': 'date', 'label': 'NGÀY TẠO', 'field': 'date', 'align': 'center'},
                {'name': 'action', 'label': 'THAO TÁC', 'field': 'action', 'align': 'center'},
            ]
            rows_sales = []
            for s in sales_data:
                rows_sales.append({
                    'id': f"#{s[0]}",
                    'raw_id': s[0],
                    'staff': s[1],
                    'cust': s[2],
                    'voucher': s[3] or '—',
                    'total': f"{int(s[4] or 0):,} ₫".replace(",", "."),
                    'date': str(s[6])[:19] if s[6] else '—',
                })

            sales_table = ui.table(columns=columns_sales, rows=rows_sales, row_key='id').classes('w-full bg-white rounded-2xl shadow-sm border border-gray-100')
            sales_table.add_slot('body-cell-action', '''
                <q-td :props="props">
                    <q-btn flat dense rounded color="primary" icon="visibility" label="Chi tiết" 
                           @click="() => $parent.$emit('view_detail', props.row.raw_id)" />
                </q-td>
            ''')

            def show_detail_dialog(e):
                raw = e.args
                order_id = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
                conn = container.db_manager.get_connection() if container.db_manager else None
                if not conn:
                    return
                details = []
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT p.name, od.quantity, od.price_at_sale, (od.quantity * od.price_at_sale) as subtotal
                        FROM order_details od
                        JOIN products p ON od.product_id = p.id
                        WHERE od.order_id = %s
                    """, (order_id,))
                    details = cursor.fetchall()
                except Exception as ex:
                    print(f"Error fetching details: {ex}")
                finally:
                    if cursor: cursor.close()
                    conn.close()

                with ui.dialog() as dlg, ui.card().classes('w-[600px] max-w-[95vw] rounded-2xl p-6 bg-white shadow-2xl'):
                    with ui.row().classes('w-full justify-between items-center border-b pb-3 mb-4'):
                        ui.label(f'Chi tiết đơn hàng #{order_id}').classes('text-lg font-bold text-gray-900')
                        ui.button(icon='close', on_click=dlg.close).props('flat round dense')

                    if details:
                        for d in details:
                            with ui.row().classes('w-full justify-between items-center py-2.5 border-b border-gray-50'):
                                with ui.column().classes('gap-0.5'):
                                    ui.label(d[0]).classes('font-semibold text-sm text-gray-900')
                                    ui.label(f'{int(d[2]):,} ₫ × {d[1]} máy').classes('text-xs text-gray-500')
                                ui.label(f'{int(d[3]):,} ₫').classes('font-bold text-sm text-blue-600')

                        def export_pdf_again():
                            export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'exports')
                            os.makedirs(export_dir, exist_ok=True)
                            pdf_path = os.path.join(export_dir, f"hoadon_{order_id}.pdf")
                            
                            items_payload = [{'name': d[0], 'quantity': d[1], 'price': float(d[2])} for d in details]
                            total_amt = sum(d[3] for d in details)
                            
                            if container.exporter:
                                ok, _ = container.exporter.print_invoice_pdf(str(order_id), "Khách Hàng", items_payload, total_amt, pdf_path)
                                if ok:
                                    ui.notify(f'Xuất hóa đơn PDF thành công! Lưu tại: exports/hoadon_{order_id}.pdf', type='positive')
                                else:
                                    ui.notify('Lỗi xuất hóa đơn PDF', type='negative')

                        with ui.row().classes('w-full justify-end mt-4'):
                            ui.button('In Hóa Đơn PDF (A4)', on_click=export_pdf_again).classes(
                                'bg-[#0071e3] text-white font-medium px-4 py-2 rounded-xl text-xs shadow-xs'
                            ).props('no-caps icon=print')
                    else:
                        ui.label('Không có thông tin chi tiết sản phẩm').classes('text-gray-400 italic py-4')

                dlg.open()

            sales_table.on('view_detail', show_detail_dialog)

        # ══════════════════════════════════════════════════════
        #  PANEL 2: LỊCH SỬ NHẬP HÀNG (Dành cho Staff & Admin)
        # ══════════════════════════════════════════════════════
        with ui.tab_panel('imports').classes('p-0'):
            import_logs = []
            if container.history_service:
                import_logs = container.history_service.get_import_history(limit=50) or []

            columns_imports = [
                {'name': 'id', 'label': 'MÃ NHẬP', 'field': 'id', 'align': 'left'},
                {'name': 'prod', 'label': 'SẢN PHẨM LAPTOP', 'field': 'prod', 'align': 'left'},
                {'name': 'qty', 'label': 'SL NHẬP', 'field': 'qty', 'align': 'center'},
                {'name': 'price', 'label': 'GIÁ NHẬP', 'field': 'price', 'align': 'right'},
                {'name': 'total', 'label': 'TỔNG CHI PHÍ', 'field': 'total', 'align': 'right'},
                {'name': 'date', 'label': 'NGÀY NHẬP', 'field': 'date', 'align': 'center'},
            ]
            rows_imports = []
            for row in import_logs:
                date_str = row[5].strftime("%d/%m/%Y %H:%M") if hasattr(row[5], 'strftime') else str(row[5])[:16]
                rows_imports.append({
                    'id': f"#{row[0]}",
                    'prod': row[1],
                    'qty': f"{row[2]} máy",
                    'price': f"{int(row[3]):,} ₫".replace(",", "."),
                    'total': f"{int(row[4]):,} ₫".replace(",", "."),
                    'date': date_str,
                })

            ui.table(columns=columns_imports, rows=rows_imports, row_key='id').classes('w-full bg-white rounded-2xl shadow-sm border border-gray-100')
