"""Customer Profile & Settings — Hồ sơ cá nhân, Địa chỉ giao hàng và Cài đặt bảo mật cho Khách hàng."""

from nicegui import ui, app
from gui.web.store.layout import store_layout
from logic.service_container import get_container


@ui.page('/profile')
@ui.page('/settings')
@store_layout('Hồ Sơ & Cài Đặt Cá Nhân', active_tab='profile')
def profile_page():
    user = app.storage.user
    if not user.get('authenticated'):
        ui.navigate.to('/login')
        return

    role = user.get('role')
    if role in ('admin', 'staff'):
        ui.navigate.to('/admin/settings')
        return

    container = get_container()
    user_id = user.get('id')
    
    if not user_id:
        ui.label('Không tìm thấy thông tin tài khoản.').classes('text-red-500')
        return

    # Lấy thông tin user và customer tương ứng
    current_user_data = None
    customer_data = None

    if container.db_manager:
        conn = container.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                current_user_data = cursor.fetchone()

                # Tìm customer theo full_name hoặc liên kết qua đơn hàng gần nhất
                if current_user_data:
                    u_name = current_user_data.get('full_name') or current_user_data.get('username')
                    cursor.execute("SELECT * FROM customers WHERE full_name = %s ORDER BY id DESC LIMIT 1", (u_name,))
                    customer_data = cursor.fetchone()

                if not customer_data and user_id:
                    cursor.execute("""
                        SELECT c.* FROM orders o
                        JOIN customers c ON o.customer_id = c.id
                        WHERE o.user_id = %s
                        ORDER BY o.id DESC LIMIT 1
                    """, (user_id,))
                    customer_data = cursor.fetchone()
            except Exception as e:
                print(f"Error loading profile: {e}")
            finally:
                if cursor: cursor.close()
                conn.close()

    if not current_user_data:
        ui.label('Lỗi tải dữ liệu người dùng.').classes('text-red-500')
        return

    # Header trang
    with ui.row().classes('w-full justify-between items-center mb-6 flex-wrap gap-4'):
        with ui.column().classes('gap-1'):
            ui.label('Hồ Sơ & Cài Đặt Cá Nhân').classes('text-3xl font-extrabold text-gray-900 tracking-tight')
            ui.label('Quản lý thông tin liên hệ, địa chỉ nhận hàng mặc định và bảo mật tài khoản').classes('text-sm text-gray-500')

        # Thẻ điểm thưởng thành viên
        points = customer_data.get('loyalty_points', 0) if customer_data else 0
        with ui.card().classes('px-5 py-3 rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-200 shadow-xs flex-row items-center gap-3'):
            with ui.element('div').classes('w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold'):
                ui.icon('military_tech', size='22px')
            with ui.column().classes('gap-0'):
                ui.label(f'{points} Điểm').classes('font-bold text-base text-amber-900')
                ui.label('Điểm thành viên tích lũy').classes('text-[11px] text-amber-700 font-medium')

    with ui.column().classes('w-full max-w-3xl mx-auto gap-6'):
        # 1. THÔNG TIN CÁ NHÂN & GIAO HÀNG
        with ui.card().classes('w-full p-6 rounded-2xl shadow-xs border border-gray-100 bg-white'):
            with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                ui.icon('person_pin', size='22px').classes('text-blue-600')
                ui.label('Thông Tin Giao Hàng & Liên Hệ').classes('font-bold text-base text-gray-900')

            with ui.column().classes('w-full gap-4'):
                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                    inp_username = ui.input('Tên đăng nhập', value=current_user_data.get('username')).props('outlined dense readonly')
                    inp_fullname = ui.input('Họ và Tên', value=current_user_data.get('full_name', '')).props('outlined dense')

                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                    init_phone = customer_data.get('phone', '') if customer_data else user.get('phone', '')
                    inp_phone = ui.input('Số điện thoại nhận hàng', value=init_phone).props('outlined dense placeholder="Ví dụ: 0912345678"')
                    init_email = customer_data.get('email', '') if customer_data else ''
                    inp_email = ui.input('Email liên hệ', value=init_email).props('outlined dense placeholder="email@domain.com"')

                init_addr = customer_data.get('address', '') if customer_data else user.get('address', '')
                inp_address = ui.input('Địa chỉ nhận hàng mặc định', value=init_addr).classes('w-full').props('outlined dense placeholder="Số nhà, tên đường, phường/xã, quận/huyện, tỉnh/thành..."')

        # 2. BẢO MẬT & ĐỔI MẬT KHẨU
        with ui.card().classes('w-full p-6 rounded-2xl shadow-xs border border-gray-100 bg-white'):
            with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                ui.icon('lock', size='22px').classes('text-blue-600')
                ui.label('Đổi Mật Khẩu Đăng Nhập').classes('font-bold text-base text-gray-900')

            with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 gap-4'):
                new_password = ui.input('Mật khẩu mới (Để trống nếu không đổi)', password=True, password_toggle_button=True).props('outlined dense')
                confirm_password = ui.input('Xác nhận mật khẩu mới', password=True, password_toggle_button=True).props('outlined dense')

        # 3. TÙY CHỌN THÔNG BÁO
        with ui.card().classes('w-full p-6 rounded-2xl shadow-xs border border-gray-100 bg-white'):
            with ui.row().classes('items-center gap-2 mb-4 pb-3 border-b border-gray-100'):
                ui.icon('notifications', size='22px').classes('text-blue-600')
                ui.label('Tùy Chọn Thông Báo').classes('font-bold text-base text-gray-900')

            with ui.column().classes('gap-2'):
                ui.checkbox('Nhận thông báo ưu đãi và Voucher giảm giá độc quyền', value=True).classes('text-sm text-gray-700')
                ui.checkbox('Nhận email cập nhật tình trạng giao hàng và bảo hành thiết bị', value=True).classes('text-sm text-gray-700')

        def save_customer_profile():
            # 1. Kiểm tra mật khẩu
            p1 = new_password.value
            p2 = confirm_password.value
            if p1 or p2:
                if len(p1) < 6:
                    ui.notify('Mật khẩu mới phải có ít nhất 6 ký tự!', type='warning')
                    return
                if p1 != p2:
                    ui.notify('Mật khẩu xác nhận không khớp!', type='negative')
                    return
                # Mã hóa bằng Bcrypt chuẩn qua UserService
                if container.user_service:
                    container.user_service.update_password_hash(user_id, p1)

            # 2. Cập nhật thông tin người dùng trong DB
            conn = container.db_manager.get_connection() if container.db_manager else None
            if conn:
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET full_name = %s WHERE id = %s", (inp_fullname.value, user_id))

                    # Cập nhật hoặc thêm khách hàng
                    ph = (inp_phone.value or '').strip()
                    em = (inp_email.value or '').strip()
                    addr = (inp_address.value or '').strip()
                    fn = inp_fullname.value or ''

                    if ph:
                        if len(ph) != 10 or not ph.isdigit() or not ph.startswith('0'):
                            ui.notify('Số điện thoại phải gồm 10 chữ số và bắt đầu bằng số 0!', type='warning')
                            return
                        cursor.execute("""
                            INSERT INTO customers (full_name, phone, email, address)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), email = VALUES(email), address = VALUES(address)
                        """, (fn, ph, em, addr))
                    
                    conn.commit()
                except Exception as e:
                    print(f"Error saving customer profile: {e}")
                finally:
                    if cursor: cursor.close()
                    conn.close()

            app.storage.user['full_name'] = inp_fullname.value
            app.storage.user['phone'] = inp_phone.value
            app.storage.user['address'] = inp_address.value

            ui.notify('Cập nhật hồ sơ và cài đặt thành công!', type='positive')
            new_password.value = ''
            confirm_password.value = ''

        with ui.row().classes('w-full justify-end mt-2 mb-8'):
            ui.button('Lưu Thay Đổi', icon='save', on_click=save_customer_profile).classes(
                'bg-[#0071e3] text-white px-8 h-12 rounded-xl font-semibold shadow-md hover:bg-blue-600'
            ).props('no-caps')
