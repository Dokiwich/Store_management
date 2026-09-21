"""Warranty module — Tab riêng biệt chuyên biệt cho Quản Lý & Tra Cứu Bảo Hành (tương ứng warranty_tab.py)."""

from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container
from datetime import datetime


@ui.page('/admin/warranty')
@admin_layout('Bảo Hành', active_tab='warranty')
def warranty_page():
    container = get_container()
    state = {'results': [], 'filter_status': 'all'}

    def fetch_warranties(kw=''):
        conn = container.db_manager.get_connection() if container.db_manager else None
        if not conn:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            kw_clean = kw.strip()
            if kw_clean:
                sql = """
                    SELECT o.id, c.full_name, c.phone, p.name, od.price_at_sale, o.created_at, p.warranty_time
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    JOIN order_details od ON o.id = od.order_id
                    JOIN products p ON od.product_id = p.id
                    WHERE (c.phone LIKE %s OR o.id LIKE %s OR p.name LIKE %s)
                    ORDER BY o.created_at DESC LIMIT 60
                """
                param = f"%{kw_clean}%"
                cursor.execute(sql, (param, param, param))
            else:
                sql = """
                    SELECT o.id, c.full_name, c.phone, p.name, od.price_at_sale, o.created_at, p.warranty_time
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    JOIN order_details od ON o.id = od.order_id
                    JOIN products p ON od.product_id = p.id
                    ORDER BY o.created_at DESC LIMIT 50
                """
                cursor.execute(sql)
            return cursor.fetchall()
        except Exception as ex:
            print(f"Error fetching warranties: {ex}")
            return []
        finally:
            if cursor: cursor.close()
            conn.close()

    # Tải dữ liệu ban đầu
    state['results'] = fetch_warranties()

    # ── Page Header ──
    with ui.row().classes('w-full justify-between items-center mb-6'):
        with ui.column().classes('gap-1'):
            ui.label('Quản Lý Bảo Hành').classes('text-2xl font-bold text-gray-900')
            ui.label('Tra cứu thời hạn bảo hành, tiếp nhận thiết bị bảo hành và kiểm tra điều kiện bảo hành sản phẩm').classes('text-sm text-gray-500')

    # ── Quick Stats Row ──
    def calc_stats():
        total = len(state['results'])
        valid = 0
        expired = 0
        now = datetime.now()
        for r in state['results']:
            created_at = r[5]
            w_raw = r[6]
            months = 12
            if w_raw:
                try:
                    nums = [int(s) for s in str(w_raw).split() if s.isdigit()]
                    months = nums[0] if nums else int(w_raw)
                except:
                    months = 12
            if hasattr(created_at, 'year'):
                diff = now - created_at
                if (months * 30) - diff.days > 0:
                    valid += 1
                else:
                    expired += 1
            else:
                valid += 1
        return total, valid, expired

    total_cnt, valid_cnt, expired_cnt = calc_stats()

    with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-3 gap-4 mb-6'):
        with ui.card().classes('p-4 rounded-2xl bg-white border border-gray-100 shadow-xs flex-row items-center gap-4'):
            with ui.element('div').classes('w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center'):
                ui.icon('verified_user', size='26px')
            with ui.column().classes('gap-0'):
                ui.label(f'{total_cnt} máy').classes('text-xl font-bold text-gray-900')
                ui.label('Tổng thiết bị đã bán').classes('text-xs text-gray-500')

        with ui.card().classes('p-4 rounded-2xl bg-white border border-gray-100 shadow-xs flex-row items-center gap-4'):
            with ui.element('div').classes('w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center'):
                ui.icon('check_circle', size='26px')
            with ui.column().classes('gap-0'):
                ui.label(f'{valid_cnt} máy').classes('text-xl font-bold text-emerald-600')
                ui.label('Thiết bị đang còn hạn bảo hành').classes('text-xs text-gray-500')

        with ui.card().classes('p-4 rounded-2xl bg-white border border-gray-100 shadow-xs flex-row items-center gap-4'):
            with ui.element('div').classes('w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center'):
                ui.icon('schedule', size='26px')
            with ui.column().classes('gap-0'):
                ui.label(f'{expired_cnt} máy').classes('text-xl font-bold text-rose-500')
                ui.label('Thiết bị đã hết hạn bảo hành').classes('text-xs text-gray-500')

    # ── Search & Filter Bar ──
    with ui.card().classes('w-full p-4 mb-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
        with ui.row().classes('w-full gap-4 items-center justify-between flex-wrap'):
            with ui.row().classes('flex-1 gap-3 items-center min-w-[300px]'):
                search_inp = ui.input(
                    placeholder='Nhập Số điện thoại khách hàng, Mã đơn (#ID) hoặc Tên máy laptop...'
                ).classes('flex-1').props('outlined dense clearable')

                def do_search():
                    state['results'] = fetch_warranties(search_inp.value or '')
                    render_table.refresh()

                ui.button('Tra Cứu', icon='search', on_click=do_search).classes(
                    'bg-[#0071e3] text-white px-6 h-10 rounded-xl font-semibold shadow-sm hover:bg-blue-600'
                ).props('no-caps')

                search_inp.on('keydown.enter', do_search)

            # Filter chips: Tất cả, Còn hạn, Hết hạn
            with ui.row().classes('gap-2'):
                def set_filter(f_val):
                    state['filter_status'] = f_val
                    render_table.refresh()

                ui.button('Tất cả', on_click=lambda: set_filter('all')).props('outline dense rounded no-caps size=sm')
                ui.button('Còn hạn', on_click=lambda: set_filter('valid')).props('outline dense rounded no-caps size=sm color=positive')
                ui.button('Hết hạn', on_click=lambda: set_filter('expired')).props('outline dense rounded no-caps size=sm color=negative')

    # ── Data Table ──
    @ui.refreshable
    def render_table():
        columns = [
            {'name': 'order', 'label': 'MÃ ĐƠN', 'field': 'order', 'align': 'left'},
            {'name': 'cust', 'label': 'KHÁCH HÀNG', 'field': 'cust', 'align': 'left'},
            {'name': 'phone', 'label': 'SỐ ĐIỆN THOẠI', 'field': 'phone', 'align': 'center'},
            {'name': 'prod', 'label': 'LAPTOP MUA', 'field': 'prod', 'align': 'left'},
            {'name': 'price', 'label': 'GIÁ MUA', 'field': 'price', 'align': 'right'},
            {'name': 'date', 'label': 'NGÀY MUA', 'field': 'date', 'align': 'center'},
            {'name': 'period', 'label': 'GÓI BẢO HÀNH', 'field': 'period', 'align': 'center'},
            {'name': 'status', 'label': 'TÌNH TRẠNG', 'field': 'status', 'align': 'center'},
        ]

        rows = []
        now = datetime.now()
        f_mode = state.get('filter_status', 'all')

        for row in state['results']:
            order_id = f"#{row[0]}"
            cust_name = row[1] if row[1] else "Khách vãng lai"
            phone = row[2] if row[2] else "—"
            prod_name = row[3]
            price = f"{int(row[4]):,} ₫".replace(",", ".") if row[4] else "—"
            created_at = row[5]
            date_str = created_at.strftime("%d/%m/%Y") if hasattr(created_at, 'strftime') else str(created_at)[:10]

            w_raw = row[6]
            months = 12
            warranty_period = "12 Tháng"
            if w_raw:
                try:
                    nums = [int(s) for s in str(w_raw).split() if s.isdigit()]
                    if nums:
                        months = nums[0]
                        warranty_period = f"{months} Tháng"
                    else:
                        months = int(w_raw)
                        warranty_period = f"{months} Tháng"
                except:
                    warranty_period = str(w_raw)

            is_valid = True
            days_left = 0
            if hasattr(created_at, 'year'):
                diff = now - created_at
                days_left = (months * 30) - diff.days
                is_valid = days_left > 0

            # Áp dụng bộ lọc
            if f_mode == 'valid' and not is_valid:
                continue
            if f_mode == 'expired' and is_valid:
                continue

            status_text = f"Còn hạn ({days_left} ngày)" if is_valid else "Hết hạn bảo hành"

            rows.append({
                'order': order_id,
                'cust': cust_name,
                'phone': phone,
                'prod': prod_name,
                'price': price,
                'date': date_str,
                'period': warranty_period,
                'status': status_text,
                'is_valid': is_valid,
            })

        table = ui.table(columns=columns, rows=rows, row_key='order').classes('w-full bg-white rounded-2xl shadow-sm border border-gray-100')
        table.add_slot('body-cell-status', '''
            <q-td :props="props">
                <span :class="props.row.is_valid ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'" class="px-3 py-1 rounded-full text-xs font-semibold border">
                    {{ props.value }}
                </span>
            </q-td>
        ''')

    render_table()

    # ── Hướng Dẫn & Quy Trình Tiếp Nhận Bảo Hành ──
    with ui.card().classes('w-full mt-6 p-6 rounded-2xl bg-blue-50/60 border border-blue-100 shadow-xs'):
        with ui.row().classes('items-start gap-4'):
            with ui.element('div').classes('w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5'):
                ui.icon('info', size='22px')
            with ui.column().classes('flex-1 gap-1.5'):
                ui.label('QUY TRÌNH TIẾP NHẬN BẢO HÀNH CHÍNH HÃNG').classes('text-sm font-bold text-blue-900 uppercase tracking-wider')
                ui.label(
                    '1. Kiểm tra đối chiếu số điện thoại khách hàng hoặc mã đơn hàng trên hóa đơn mua hàng điện tử.'
                ).classes('text-xs text-blue-800')
                ui.label(
                    '2. Xác định tình trạng máy còn nguyên tem bảo hành của Laptop Store và nhà phân phối, không có dấu hiệu cấn móp nặng, rơi vỡ hoặc ngập nước.'
                ).classes('text-xs text-blue-800')
                ui.label(
                    '3. Lập biên nhận tiếp nhận máy và chuyển tới trung tâm bảo hành hãng (Thời gian xử lý: 3 - 7 ngày làm việc).'
                ).classes('text-xs text-blue-800')
