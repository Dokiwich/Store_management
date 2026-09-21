from nicegui import ui, app
from functools import wraps
from typing import Optional, Callable, Any
from gui.web.cart_dialog import open_cart_dialog
from gui.web.components.onboarding import show_web_tour, restart_web_tour

def _inject_master_styles():
    ui.add_head_html('''
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            html, body, .q-page { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; background-color: #f9fafb !important; margin: 0; }
            .q-page-container { background-color: #f9fafb !important; }
            .q-drawer--left, .q-header { transition: none !important; }
            .nicegui-reconnect-badge, .q-loading-bar { display: none !important; }
            .sidebar-nav-btn { transition: all 0.15s ease; }
            .sidebar-nav-btn:hover { background-color: #f3f4f6 !important; }
            .custom-scrollbar::-webkit-scrollbar { width: 6px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
        </style>
    ''')

def admin_layout(title: str = '', active_tab: Optional[str] = None, *args: Any, **kwargs: Any) -> Callable:
    """Unified master layout for all pages: Home, POS, Inventory, Dashboard, etc."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not app.storage.user.get('authenticated'):
                ui.navigate.to('/login')
                return
            
            _inject_master_styles()

            user = app.storage.user
            role = user.get('role', 'staff')
            if role == 'customer':
                ui.navigate.to('/')
                return

            full_name = user.get('full_name', user.get('username', 'Quản Trị Viên'))
            role_display = "Quản Trị Viên" if role == 'admin' else "Nhân Viên"

            # ── Unified Header ──
            with ui.header().classes(
                'items-center px-6 h-16 border-b border-gray-200 z-30'
            ).style('background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);'):
                with ui.row().classes('w-full items-center justify-between max-w-[1800px] mx-auto'):
                    # Left: Hamburger + Logo + Breadcrumb
                    with ui.row().classes('items-center gap-3'):
                        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat round dense color=dark').classes('lg:hidden')
                        ui.image('/static/assets/logo.svg').classes('w-9 h-9 rounded-xl shadow-xs cursor-pointer').on('click', lambda: ui.navigate.to('/'))
                        ui.label('Laptop Store').classes('text-base font-bold text-gray-900 cursor-pointer').on('click', lambda: ui.navigate.to('/'))
                        ui.label('›').classes('text-gray-300 font-semibold')
                        ui.label(title).classes('text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100')

                    # Right: Cart + User info + Logout
                    with ui.row().classes('items-center gap-3'):
                        # Cart quick button (Luôn khả dụng tại mọi trang)
                        @ui.refreshable
                        def render_header_cart():
                            curr_cart = app.storage.user.get('cart', [])
                            c_count = sum(i.get('qty', 1) for i in curr_cart)
                            with ui.button(
                                on_click=lambda: open_cart_dialog(on_cart_changed=render_header_cart.refresh)
                            ).classes('rounded-full px-3 h-9 ' + ('bg-blue-50 text-blue-600' if c_count > 0 else 'bg-gray-100 text-gray-600')).props('flat no-caps id="header-cart"'):
                                ui.icon('shopping_bag', size='18px')
                                ui.label(f'{c_count}').classes('ml-1 font-bold text-xs')
                        
                        render_header_cart()

                        with ui.row().classes('items-center gap-2 pl-2 border-l border-gray-200').props('id="user-profile"'):
                            ui.avatar(icon='person', color='blue-6', text_color='white', size='32px').classes('shadow-sm')
                            with ui.column().classes('gap-0 hidden md:flex'):
                                ui.label(full_name).classes('font-semibold text-xs text-gray-900 leading-tight')
                                ui.label(role_display).classes('text-[10px] text-gray-500 font-medium')
                        
                        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat round dense color=grey-7 size=sm').classes('hover:text-red-600 hover:bg-red-50')

            # ── Unified Sidebar (Left Drawer) ──
            with ui.left_drawer(value=True, bordered=True).classes(
                'bg-white w-64 px-4 pt-4 border-r border-gray-200 z-20 flex-col flex justify-between'
            ).props('id="sidebar-menu"') as left_drawer:
                with ui.column().classes('w-full gap-0'):
                    def nav_item(icon, label, target_url, tab_key):
                        is_active = (active_tab == tab_key) if active_tab else False
                        btn_classes = 'w-full justify-start rounded-xl h-11 text-sm font-medium sidebar-nav-btn mb-1 '
                        if is_active:
                            btn_classes += 'bg-blue-50 text-blue-600 font-semibold shadow-xs'
                        else:
                            btn_classes += 'text-gray-600 hover:text-gray-900'

                        with ui.button(on_click=lambda url=target_url: ui.navigate.to(url)).classes(btn_classes).props(f'flat no-caps align=left id="menu-{tab_key}"'):
                            ui.icon(icon, size='18px').classes('mr-3 ' + ('text-blue-600' if is_active else 'text-gray-400'))
                            ui.label(label)

                    # MENU CHÍNH (Áp dụng cho tất cả vai trò)
                    ui.label('MENU CHÍNH').classes('text-[11px] font-bold text-gray-400 mt-2 mb-2 ml-2 tracking-wider')
                    nav_item('storefront', 'Trang Chủ & Cửa Hàng', '/', 'home')
                    nav_item('support_agent', 'Dịch Vụ & CSKH', '/services', 'services')

                    # QUẢN LÝ (Admin & Staff)
                    ui.label('QUẢN LÝ').classes('text-[11px] font-bold text-gray-400 mt-5 mb-2 ml-2 tracking-wider')
                    nav_item('inventory_2', 'Kho Hàng Laptop', '/admin/inventory', 'inventory')
                    nav_item('people', 'Khách Hàng CRM', '/admin/customers', 'customers')
                    nav_item('receipt_long', 'Lịch Sử Hoạt Động', '/admin/orders', 'orders')
                    nav_item('verified_user', 'Bảo Hành', '/admin/warranty', 'warranty')
                    if role == 'staff':
                        nav_item('settings', 'Cài Đặt Của Tôi', '/admin/settings', 'settings')

                    # HỆ THỐNG (Admin only)
                    if role == 'admin':
                        ui.label('HỆ THỐNG').classes('text-[11px] font-bold text-gray-400 mt-5 mb-2 ml-2 tracking-wider')
                        nav_item('bar_chart', 'Thống Kê Doanh Thu', '/admin', 'dashboard')
                        nav_item('badge', 'Quản Lý Nhân Viên', '/admin/employees', 'employees')
                        nav_item('settings', 'Cài Đặt Hệ Thống', '/admin/settings', 'settings')

                    # TRỢ GIÚP
                    ui.label('TRỢ GIÚP').classes('text-[11px] font-bold text-gray-400 mt-5 mb-2 ml-2 tracking-wider')
                    with ui.button(on_click=lambda: restart_web_tour(role, 'admin')).classes('w-full justify-start rounded-xl h-11 text-sm font-medium sidebar-nav-btn mb-1 text-gray-600 hover:text-gray-900').props('flat no-caps align=left id="menu-tour"'):
                        ui.icon('help_outline', size='18px').classes('mr-3 text-gray-400')
                        ui.label('Hướng Dẫn Sử Dụng')

            # ── Main Page Content Wrapper ──
            with ui.column().classes('w-full max-w-[1800px] mx-auto p-4 md:p-8 flex-1'):
                func(*args, **kwargs)

                # ── FOOTER HỆ THỐNG ──
                with ui.element('footer').classes('w-full mt-16 pt-10 border-t border-gray-200 text-gray-600'):
                    with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-3 gap-8 mb-8'):
                        # Cột 1: Giới thiệu hệ thống
                        with ui.column().classes('gap-2'):
                            with ui.row().classes('items-center gap-2'):
                                ui.image('/static/assets/logo.svg').classes('w-8 h-8 rounded-lg')
                                ui.label('Laptop Store').classes('font-extrabold text-base text-gray-900')
                            ui.label('Hệ thống quản lý cửa hàng kinh doanh laptop và thiết bị tin học.').classes('text-xs text-gray-500 leading-relaxed')
                            ui.label('Phần mềm phục vụ quản trị bán hàng, tồn kho, bảo hành và chăm sóc khách hàng.').classes('text-xs text-gray-400')

                        # Cột 2: Dịch vụ & Tra cứu
                        with ui.column().classes('gap-2'):
                            ui.label('DỊCH VỤ & CHÍNH SÁCH').classes('font-bold text-xs text-gray-900 tracking-wider')
                            ui.link('Chính sách 1 Đổi 1 trong 30 ngày', '/services').classes('text-xs text-gray-500 hover:text-blue-600 no-underline')
                            ui.link('Bảo hành chính hãng 12 - 24 tháng', '/services').classes('text-xs text-gray-500 hover:text-blue-600 no-underline')
                            ui.link('Tra cứu bảo hành theo SĐT', '/admin/warranty').classes('text-xs text-gray-500 hover:text-blue-600 no-underline')

                        # Cột 3: Hỗ trợ tại cửa hàng
                        with ui.column().classes('gap-2'):
                            ui.label('HỖ TRỢ TẠI CỬA HÀNG').classes('font-bold text-xs text-gray-900 tracking-wider')
                            ui.label('Địa điểm: Cửa hàng Laptop Store').classes('text-xs text-gray-600')
                            ui.label('Thời gian: 08:30 - 18:00 (Thứ 2 - Thứ 7)').classes('text-xs text-gray-600')
                            ui.label('Hỗ trợ kỹ thuật và tiếp nhận bảo hành trực tiếp tại cửa hàng.').classes('text-xs text-gray-500')

                    with ui.row().classes('w-full justify-between items-center py-4 border-t border-gray-100 text-xs text-gray-400 flex-wrap gap-2'):
                        ui.label('© 2026 Laptop Store Management System • Báo cáo học phần Nhập Môn Công Nghệ Phần Mềm.')
                        ui.label('Đại Học Công Nghệ Miền Đông (MUT) - Nhóm Inter Zero Salary')
            
            show_web_tour(role, context='admin')

        return wrapper
    return decorator
