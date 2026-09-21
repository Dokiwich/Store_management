"""Employees module — Quản lý tài khoản nhân viên (tương ứng employee_tab.py)."""

from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container


@ui.page('/admin/employees')
@admin_layout('Quản Lý Nhân Viên', active_tab='employees')
def employees_page():
    container = get_container()
    
    # Phân quyền Admin
    if app.storage.user.get('role') != 'admin':
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm'):
            ui.icon('lock', size='54px').classes('text-red-400 mb-3')
            ui.label('Không Có Quyền Truy Cập').classes('text-xl font-bold text-gray-800')
            ui.label('Chức năng quản lý nhân viên chỉ dành riêng cho tài khoản Quản Trị Viên (Admin).').classes('text-sm text-gray-500 mt-1')
        return

    state = {'users': []}

    def load_users():
        if container.user_service:
            state['users'] = container.user_service.get_all_users() or []

    load_users()

    with ui.row().classes('w-full justify-between items-center mb-6'):
        with ui.column().classes('gap-1'):
            ui.label(f'Quản Lý Nhân Sự ({len(state["users"])})').classes('text-2xl font-bold text-gray-900')
            ui.label('Tạo mới tài khoản, phân quyền chức vụ và quản lý trạng thái hoạt động').classes('text-sm text-gray-500')

    with ui.row().classes('w-full grid grid-cols-1 lg:grid-cols-3 gap-6 items-start'):
        # ── Cột trái: Form Thêm Nhân Viên ──
        with ui.card().classes('p-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
            ui.label('Thêm Tài Khoản Mới').classes('text-sm font-bold text-blue-600 uppercase tracking-wider mb-4')
            emp_user = ui.input('Tên đăng nhập *').classes('w-full mb-2').props('outlined dense')
            emp_pass = ui.input('Mật khẩu (≥ 6 ký tự) *', password=True, password_toggle_button=True).classes('w-full mb-2').props('outlined dense')
            emp_name = ui.input('Họ và Tên *').classes('w-full mb-2').props('outlined dense')
            emp_role = ui.select(['staff', 'admin'], value='staff', label='Chức vụ / Vai trò').classes('w-full mb-4').props('outlined dense')

            def handle_add_emp():
                u = emp_user.value.strip() if emp_user.value else ''
                p = emp_pass.value.strip() if emp_pass.value else ''
                n = emp_name.value.strip() if emp_name.value else ''
                r = emp_role.value

                if not u or not p or not n:
                    ui.notify('Vui lòng điền đầy đủ các trường bắt buộc!', type='warning')
                    return

                if len(p) < 6:
                    ui.notify('Mật khẩu phải chứa ít nhất 6 ký tự!', type='warning')
                    return

                success, msg = container.user_service.add_user(u, p, n, r)
                if success:
                    ui.notify('Tạo tài khoản nhân viên thành công!', type='positive')
                    emp_user.value = ''
                    emp_pass.value = ''
                    emp_name.value = ''
                    load_users()
                    render_emp_table.refresh()
                else:
                    ui.notify(f'Lỗi: {msg}', type='negative')

            ui.button('Tạo Nhân Viên', icon='person_add', on_click=handle_add_emp).classes(
                'w-full bg-[#0071e3] text-white font-semibold h-11 rounded-xl shadow-sm hover:opacity-90'
            ).props('no-caps')

        # ── Cột phải: Bảng Danh Sách Nhân Viên ──
        with ui.column().classes('col-span-2 w-full gap-4'):
            @ui.refreshable
            def render_emp_table():
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                    {'name': 'username', 'label': 'TÀI KHOẢN', 'field': 'username', 'align': 'left'},
                    {'name': 'full_name', 'label': 'HỌ VÀ TÊN', 'field': 'full_name', 'align': 'left'},
                    {'name': 'role', 'label': 'CHỨC VỤ', 'field': 'role', 'align': 'center'},
                    {'name': 'status', 'label': 'TRẠNG THÁI', 'field': 'status', 'align': 'center'},
                    {'name': 'action', 'label': 'THAO TÁC', 'field': 'action', 'align': 'center'},
                ]
                rows = []
                for u in state['users']:
                    # u: id, username, full_name, role, is_active
                    role_str = "QUẢN TRỊ" if u[3] == 'admin' else ("NHÂN VIÊN" if u[3] == 'staff' else "KHÁCH HÀNG")
                    rows.append({
                        'id': f"#{u[0]}",
                        'raw_id': u[0],
                        'username': u[1],
                        'full_name': u[2],
                        'role': role_str,
                        'is_active': u[4] == 1,
                        'status': 'Hoạt động' if u[4] == 1 else 'Đã khóa',
                    })

                t = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full bg-white rounded-2xl shadow-sm border border-gray-100')
                t.add_slot('body-cell-status', '''
                    <q-td :props="props">
                        <span :class="props.row.is_active ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'" class="px-3 py-1 rounded-full text-xs font-semibold border">
                            {{ props.value }}
                        </span>
                    </q-td>
                ''')
                t.add_slot('body-cell-action', '''
                    <q-td :props="props">
                        <q-btn flat dense rounded :color="props.row.is_active ? 'negative' : 'positive'" 
                               :label="props.row.is_active ? 'Khóa' : 'Mở khóa'"
                               @click="() => $parent.$emit('toggle_status', props.row.raw_id)" />
                    </q-td>
                ''')

                def toggle_user(e):
                    raw = e.args
                    uid = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
                    if uid and str(uid) == str(app.storage.user.get('id')):
                        ui.notify('Không thể tự khóa tài khoản của chính bạn đang đăng nhập!', type='warning')
                        return
                    # Khóa / Mở khóa tài khoản
                    success = container.user_service.toggle_user_status(uid)
                    if success:
                        ui.notify('Đã cập nhật trạng thái tài khoản', type='info')
                        load_users()
                        render_emp_table.refresh()
                    else:
                        ui.notify('Không thể cập nhật tài khoản này', type='negative')

                t.on('toggle_status', toggle_user)

            render_emp_table()
