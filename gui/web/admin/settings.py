"""Settings module — Phân hệ Cài Đặt chia luồng chuyên biệt cho Admin và Staff."""

from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container


@ui.page('/admin/settings')
@admin_layout('Cài Đặt', active_tab='settings')
def settings_page():
    if not app.storage.user.get('authenticated'):
        ui.navigate.to('/login')
        return

    container = get_container()
    user = app.storage.user
    role = user.get('role', 'staff')
    user_id = user.get('id')

    # Nếu là customer thì chuyển về trang profile khách hàng
    if role == 'customer':
        ui.navigate.to('/profile')
        return

    settings_svc = container.settings_service
    current_settings = settings_svc.get_all() if settings_svc else {}

    # ══════════════════════════════════════════════════════════════════
    #  GIAO DIỆN DÀNH CHO QUẢN TRỊ VIÊN (ADMIN)
    # ══════════════════════════════════════════════════════════════════
    if role == 'admin':
        with ui.row().classes('w-full justify-between items-center mb-6'):
            with ui.column().classes('gap-1'):
                ui.label('Cài Đặt Hệ Thống').classes('text-2xl font-bold text-gray-900')
                ui.label('Quản lý thông tin doanh nghiệp, tham số vận hành cửa hàng và an toàn hệ thống').classes('text-sm text-gray-500')

        with ui.column().classes('w-full max-w-4xl gap-6'):
            # 1. THÔNG TIN CỬA HÀNG & LIÊN HỆ
            with ui.card().classes('w-full p-6 rounded-2xl bg-white border border-gray-100 shadow-xs'):
                with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                    ui.icon('storefront', size='22px').classes('text-blue-600')
                    ui.label('Thông Tin Doanh Nghiệp & Cửa Hàng').classes('font-bold text-base text-gray-900')

                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                    inp_store_name = ui.input('Tên cửa hàng', value=current_settings.get('store_name', 'Laptop Store Pro')).props('outlined dense')
                    inp_hotline = ui.input('Hotline CSKH', value=current_settings.get('store_hotline', '1800 1234')).props('outlined dense')
                    inp_email = ui.input('Email hỗ trợ', value=current_settings.get('store_email', 'cskh@laptopstore.vn')).props('outlined dense')
                    inp_address = ui.input('Địa chỉ cửa hàng', value=current_settings.get('store_address', '123 Đường Công Nghệ, Quận 1, TP. HCM')).props('outlined dense')

            # 2. THAM SỐ NGHIỆP VỤ BÁN HÀNG & KHO
            with ui.card().classes('w-full p-6 rounded-2xl bg-white border border-gray-100 shadow-xs'):
                with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                    ui.icon('tune', size='22px').classes('text-blue-600')
                    ui.label('Tham Số Nghiệp Vụ').classes('font-bold text-base text-gray-900')

                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                    inp_loyalty = ui.number('Tỷ lệ tích điểm thành viên (VNĐ = 1 điểm)', value=int(current_settings.get('loyalty_rate', '100000'))).props('outlined dense')
                    inp_min_stock = ui.number('Ngưỡng cảnh báo tồn kho thấp (Số máy)', value=int(current_settings.get('low_stock_threshold', '5'))).props('outlined dense')

            def save_admin_settings():
                if settings_svc:
                    payload = {
                        'store_name': inp_store_name.value or '',
                        'store_hotline': inp_hotline.value or '',
                        'store_email': inp_email.value or '',
                        'store_address': inp_address.value or '',
                        'loyalty_rate': str(int(inp_loyalty.value or 100000)),
                        'low_stock_threshold': str(int(inp_min_stock.value or 5)),
                    }
                    settings_svc.update_settings(payload)
                    ui.notify('Đã lưu cấu hình hệ thống thành công!', type='positive')

            with ui.row().classes('w-full justify-end'):
                ui.button('Lưu Cấu Hình Hệ Thống', icon='save', on_click=save_admin_settings).classes(
                    'bg-[#0071e3] text-white px-8 h-11 rounded-xl font-semibold shadow-sm hover:bg-blue-600'
                ).props('no-caps')

            # 3. BẢO MẬT & TÀI KHOẢN ADMIN
            with ui.card().classes('w-full p-6 rounded-2xl bg-white border border-gray-100 shadow-xs mt-2'):
                with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                    ui.icon('security', size='22px').classes('text-rose-600')
                    ui.label('Bảo Mật Tài Khoản Quản Trị Viên (Admin)').classes('font-bold text-base text-gray-900')

                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                    admin_new_pass = ui.input('Mật khẩu mới (≥ 6 ký tự)', password=True, password_toggle_button=True).props('outlined dense')
                    admin_confirm_pass = ui.input('Xác nhận mật khẩu mới', password=True, password_toggle_button=True).props('outlined dense')

                def change_admin_password():
                    p1 = admin_new_pass.value
                    p2 = admin_confirm_pass.value
                    if not p1 or not p2:
                        ui.notify('Vui lòng nhập mật khẩu mới!', type='warning')
                        return
                    if len(p1) < 6:
                        ui.notify('Mật khẩu phải chứa ít nhất 6 ký tự!', type='warning')
                        return
                    if p1 != p2:
                        ui.notify('Mật khẩu xác nhận không khớp!', type='negative')
                        return

                    if container.user_service:
                        container.user_service.update_password_hash(user_id, p1)
                        ui.notify('Đã cập nhật mật khẩu Admin (mã hóa Bcrypt)!', type='positive')
                        admin_new_pass.value = ''
                        admin_confirm_pass.value = ''

                ui.button('Cập Nhật Mật Khẩu Admin', on_click=change_admin_password).classes(
                    'bg-gray-900 text-white px-6 h-10 rounded-xl font-semibold text-xs mt-2 hover:bg-black'
                ).props('no-caps')

            # 4. TRẠNG THÁI CƠ SỞ DỮ LIỆU
            with ui.card().classes('w-full p-6 rounded-2xl bg-gray-50 border border-gray-200/80 shadow-xs'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('dns', size='22px').classes('text-emerald-600')
                    ui.label('Trạng Thái Hạ Tầng Cơ Sở Dữ Liệu').classes('font-bold text-sm text-gray-800')

                with ui.row().classes('w-full gap-6 text-xs text-gray-600'):
                    with ui.column().classes('gap-1'):
                        ui.label('Connection Pool:').classes('font-semibold text-gray-500')
                        ui.label('MySQL Connection Pool (Singleton)').classes('font-bold text-gray-800')
                    with ui.column().classes('gap-1'):
                        ui.label('Pool Size tối đa:').classes('font-semibold text-gray-500')
                        ui.label('15 kết nối đồng thời').classes('font-bold text-emerald-600')
                    with ui.column().classes('gap-1'):
                        ui.label('Bảo mật dữ liệu:').classes('font-semibold text-gray-500')
                        ui.label('Bcrypt Salted Hash (Chuẩn quốc tế)').classes('font-bold text-blue-600')

    # ══════════════════════════════════════════════════════════════════
    #  GIAO DIỆN DÀNH CHO NHÂN VIÊN (STAFF)
    # ══════════════════════════════════════════════════════════════════
    else:
        with ui.row().classes('w-full justify-between items-center mb-6'):
            with ui.column().classes('gap-1'):
                ui.label('Cài Đặt Của Tôi & Bán Hàng').classes('text-2xl font-bold text-gray-900')
                ui.label('Tùy chỉnh cấu hình in ấn hóa đơn thu ngân, âm thanh thông báo và tài khoản cá nhân').classes('text-sm text-gray-500')

        with ui.column().classes('w-full max-w-3xl gap-6'):
            # 1. CẤU HÌNH MÁY IN HÓA ĐƠN POS
            with ui.card().classes('w-full p-6 rounded-2xl bg-white border border-gray-100 shadow-xs'):
                with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                    ui.icon('print', size='22px').classes('text-blue-600')
                    ui.label('Cấu Hình In Hóa Đơn Bán Hàng').classes('font-bold text-base text-gray-900')

                with ui.column().classes('w-full gap-4'):
                    paper_choice = ui.select(
                        {'A4': 'Khổ A4 tiêu chuẩn (In văn phòng / PDF)', 'K80': 'Khổ K80 cuộn (In hóa đơn nhiệt siêu tốc)'},
                        value=current_settings.get('default_print_paper', 'A4'),
                        label='Khổ giấy in mặc định'
                    ).classes('w-full').props('outlined dense')

                    auto_print = ui.checkbox(
                        'Tự động mở hộp thoại in sau khi thanh toán đơn hàng thành công',
                        value=current_settings.get('auto_print_invoice', '0') == '1'
                    ).classes('text-sm text-gray-700')

                    def save_staff_printer():
                        if settings_svc:
                            settings_svc.update_settings({
                                'default_print_paper': paper_choice.value,
                                'auto_print_invoice': '1' if auto_print.value else '0'
                            })
                            ui.notify('Đã lưu cấu hình in ấn thành công!', type='positive')

                    with ui.row().classes('w-full justify-end mt-2'):
                        ui.button('Lưu Cấu Hình In', icon='save', on_click=save_staff_printer).classes(
                            'bg-[#0071e3] text-white px-6 h-10 rounded-xl font-semibold text-xs'
                        ).props('no-caps')

            # 2. HỒ SƠ & BẢO MẬT NHÂN VIÊN
            with ui.card().classes('w-full p-6 rounded-2xl bg-white border border-gray-100 shadow-xs'):
                with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                    ui.icon('person', size='22px').classes('text-blue-600')
                    ui.label('Hồ Sơ Nhân Viên & Đổi Mật Khẩu').classes('font-bold text-base text-gray-900')

                with ui.column().classes('w-full gap-4'):
                    with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                        staff_name = ui.input('Họ và Tên nhân viên', value=user.get('full_name', '')).props('outlined dense')
                        ui.input('Tên đăng nhập', value=user.get('username', '')).props('outlined dense readonly')

                    with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4 mt-2'):
                        staff_new_pass = ui.input('Mật khẩu mới (≥ 6 ký tự)', password=True, password_toggle_button=True).props('outlined dense')
                        staff_confirm_pass = ui.input('Xác nhận mật khẩu mới', password=True, password_toggle_button=True).props('outlined dense')

                    def save_staff_profile():
                        p1 = staff_new_pass.value
                        p2 = staff_confirm_pass.value
                        if p1 or p2:
                            if len(p1) < 6:
                                ui.notify('Mật khẩu mới phải có ít nhất 6 ký tự!', type='warning')
                                return
                            if p1 != p2:
                                ui.notify('Mật khẩu xác nhận không khớp!', type='negative')
                                return
                            if container.user_service:
                                container.user_service.update_password_hash(user_id, p1)

                        if staff_name.value:
                            app.storage.user['full_name'] = staff_name.value
                            # update name in DB
                            conn = container.db_manager.get_connection() if container.db_manager else None
                            if conn:
                                cursor = None
                                try:
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE users SET full_name = %s WHERE id = %s", (staff_name.value, user_id))
                                    conn.commit()
                                finally:
                                    if cursor: cursor.close()
                                    conn.close()

                        ui.notify('Cập nhật hồ sơ nhân viên thành công!', type='positive')
                        staff_new_pass.value = ''
                        staff_confirm_pass.value = ''

                    with ui.row().classes('w-full justify-end mt-2'):
                        ui.button('Lưu Thay Đổi', icon='save', on_click=save_staff_profile).classes(
                            'bg-[#0071e3] text-white px-6 h-10 rounded-xl font-semibold text-xs'
                        ).props('no-caps')
