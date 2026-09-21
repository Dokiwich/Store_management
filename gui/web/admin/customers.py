from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container


@ui.page('/admin/customers')
@admin_layout('Khách Hàng', active_tab='customers')
def customers_page():
    # RBAC Guard: Chỉ Admin và Staff mới có quyền truy cập CRM
    if app.storage.user.get('role') not in ('admin', 'staff'):
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm'):
            ui.icon('lock', size='54px').classes('text-red-400 mb-3')
            ui.label('Không Có Quyền Truy Cập').classes('text-xl font-bold text-gray-800')
            ui.label('Chức năng quản lý thông tin khách hàng chỉ dành riêng cho Quản trị viên và Nhân viên.').classes('text-sm text-gray-500 mt-1')
            ui.button('Về Trang Chủ', on_click=lambda: ui.navigate.to('/')).classes('mt-4 bg-[#0071e3] text-white rounded-xl').props('no-caps')
        return

    container = get_container()
    state = {'customers': [], 'search_kw': ''}

    def load_customers():
        if container.customer_service:
            state['customers'] = container.customer_service.get_all_customers(limit=100) or []
        else:
            state['customers'] = []

    load_customers()

    with ui.row().classes('w-full justify-between items-center mb-6'):
        with ui.column().classes('gap-1'):
            ui.label(f'Quản Lý Khách Hàng CRM ({len(state["customers"])})').classes('text-2xl font-bold text-gray-900')
            ui.label('Lưu trữ hồ sơ khách hàng, số điện thoại định danh duy nhất và tích lũy điểm thưởng thành viên (FR-07)').classes('text-sm text-gray-500')
        
        # Search Box
        with ui.row().classes('items-center gap-2'):
            search_input = ui.input(placeholder='Tìm SĐT hoặc Tên khách...').classes('w-64 bg-white').props('outlined dense clearable')
            def on_search(e):
                state['search_kw'] = (search_input.value or '').strip().lower()
                render_cust_table.refresh()
            search_input.on('update:model-value', on_search)

    with ui.row().classes('w-full grid grid-cols-1 lg:grid-cols-3 gap-6 items-start'):
        # ── Cột trái: Form Thêm Khách Hàng ──
        with ui.card().classes('p-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
            ui.label('Thêm Khách Hàng Mới').classes('text-sm font-bold text-blue-600 uppercase tracking-wider mb-4')
            cust_name = ui.input('Họ và Tên *').classes('w-full mb-2').props('outlined dense')
            cust_phone = ui.input('Số điện thoại (10 chữ số) *').classes('w-full mb-2').props('outlined dense placeholder="VD: 0987654321"')
            cust_email = ui.input('Email').classes('w-full mb-2').props('outlined dense placeholder="VD: email@domain.com"')
            cust_address = ui.input('Địa chỉ').classes('w-full mb-4').props('outlined dense')

            def handle_add_customer():
                n = cust_name.value.strip() if cust_name.value else ''
                p = cust_phone.value.strip() if cust_phone.value else ''
                e = cust_email.value.strip() if cust_email.value else ''
                a = cust_address.value.strip() if cust_address.value else ''

                if not n or not p:
                    ui.notify('Vui lòng nhập họ tên và số điện thoại!', type='warning')
                    return

                success, msg = container.customer_service.add_customer(n, p, e, a)
                if success:
                    ui.notify('Lưu thông tin khách hàng thành công!', type='positive')
                    cust_name.value = ''
                    cust_phone.value = ''
                    cust_email.value = ''
                    cust_address.value = ''
                    load_customers()
                    render_cust_table.refresh()
                else:
                    ui.notify(f'Lỗi: {msg}', type='negative')

            def clear_form():
                cust_name.value = ''
                cust_phone.value = ''
                cust_email.value = ''
                cust_address.value = ''

            with ui.row().classes('w-full gap-2 mt-2'):
                ui.button('Lưu Khách Hàng', icon='person_add', on_click=handle_add_customer).classes(
                    'flex-1 bg-[#0071e3] text-white font-semibold h-11 rounded-xl shadow-sm hover:opacity-90'
                ).props('no-caps')
                ui.button('Làm Mới', icon='refresh', on_click=clear_form).classes(
                    'h-11 px-4 rounded-xl text-gray-600 bg-gray-100 hover:bg-gray-200'
                ).props('flat no-caps')

        # ── Cột phải: Bảng Danh Sách Khách Hàng ──
        with ui.column().classes('col-span-2 w-full gap-4'):
            @ui.refreshable
            def render_cust_table():
                if not state['customers']:
                    with ui.column().classes('w-full items-center justify-center py-16 bg-white rounded-2xl border border-gray-100 shadow-sm'):
                        ui.icon('people_outline', size='48px').classes('text-gray-300 mb-2')
                        ui.label('Chưa có dữ liệu khách hàng').classes('text-gray-500 font-medium')
                    return

                columns = [
                    {'name': 'id', 'label': 'MÃ KH', 'field': 'id', 'align': 'left'},
                    {'name': 'name', 'label': 'HỌ VÀ TÊN', 'field': 'name', 'align': 'left'},
                    {'name': 'phone', 'label': 'SỐ ĐIỆN THOẠI', 'field': 'phone', 'align': 'left'},
                    {'name': 'email', 'label': 'EMAIL', 'field': 'email', 'align': 'left'},
                    {'name': 'points', 'label': 'ĐIỂM TÍCH LŨY', 'field': 'points', 'align': 'center'},
                    {'name': 'rank', 'label': 'HẠNG', 'field': 'rank', 'align': 'center'},
                ]
                rows = []
                kw = state.get('search_kw', '')
                for c in state['customers']:
                    name = str(c[1] or '')
                    phone = str(c[2] or '')
                    email = str(c[3] or '')
                    if kw and (kw not in name.lower() and kw not in phone.lower() and kw not in email.lower()):
                        continue

                    points = int(c[5] or 0)
                    rank = 'Vàng' if points >= 500 else ('Bạc' if points >= 200 else 'Đồng')
                    rows.append({
                        'id': f"#{c[0]}",
                        'name': name or 'Khách vãng lai',
                        'phone': phone or '—',
                        'email': email or '—',
                        'points': f"{points:,} pts",
                        'rank': rank,
                    })

                t = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full bg-white rounded-2xl shadow-sm border border-gray-100')
                t.add_slot('body-cell-rank', '''
                    <q-td :props="props">
                        <span :class="props.value === 'Vàng' ? 'bg-amber-50 text-amber-700 border-amber-200' : (props.value === 'Bạc' ? 'bg-slate-100 text-slate-700 border-slate-200' : 'bg-orange-50 text-orange-700 border-orange-200')" class="px-2.5 py-0.5 rounded-full text-xs font-bold border">
                            {{ props.value }}
                        </span>
                    </q-td>
                ''')

            render_cust_table()
