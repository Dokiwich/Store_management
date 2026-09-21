from nicegui import ui, app
from functools import wraps
from typing import Optional, Callable, Any
from gui.web.cart_dialog import open_cart_dialog
from gui.web.components.onboarding import show_web_tour, restart_web_tour

def _inject_store_styles():
    ui.add_head_html('''
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            html, body, .q-page { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; background-color: #f9fafb !important; margin: 0; }
            .q-page-container { background-color: #f9fafb !important; }
            .nicegui-reconnect-badge, .q-loading-bar { display: none !important; }
            .store-nav-link { font-weight: 600; font-size: 0.875rem; color: #4b5563; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.2s; cursor: pointer; text-decoration: none; }
            .store-nav-link:hover { background-color: #f3f4f6; color: #111827; }
            .store-nav-link.active { color: #0071e3; }
        </style>
    ''')

def store_layout(title: str = '', active_tab: Optional[str] = None, *args: Any, **kwargs: Any) -> Callable:
    """Unified layout for E-Commerce Front-End (Customer facing)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _inject_store_styles()

            user = app.storage.user
            authenticated = user.get('authenticated', False)
            role = user.get('role', 'guest')
            full_name = user.get('full_name', user.get('username', 'Tài khoản'))

            # ── STORE HEADER ──
            with ui.header().classes('items-center px-4 md:px-8 h-16 border-b border-gray-200 z-30 bg-white/95 backdrop-blur-md'):
                with ui.row().classes('w-full max-w-[1200px] mx-auto items-center justify-between h-full flex-nowrap'):
                    # 1. Logo & Nav
                    with ui.row().classes('items-center gap-6'):
                        with ui.row().classes('items-center gap-2 cursor-pointer').on('click', lambda: ui.navigate.to('/')):
                            ui.image('/static/assets/logo.svg').classes('w-9 h-9 rounded-xl shadow-xs')
                            ui.label('Laptop Store').classes('text-lg font-extrabold text-gray-900 hidden sm:block tracking-tight')
                        
                        # Navigation Menu (Role-tailored)
                        with ui.row().classes('flex items-center gap-1').props('id="store-nav"'):
                            ui.label('Trang Chủ').classes('store-nav-link ' + ('active' if active_tab == 'home' else '')).on('click', lambda: ui.navigate.to('/'))
                            if role == 'admin':
                                ui.label('Trang Quản Trị').classes('store-nav-link text-blue-600 font-bold hover:bg-blue-50').on('click', lambda: ui.navigate.to('/admin'))
                            elif role == 'staff':
                                ui.label('Quản Lý Bán Hàng').classes('store-nav-link text-blue-600 font-bold hover:bg-blue-50').on('click', lambda: ui.navigate.to('/admin/orders'))
                            else:
                                ui.label('Bảo Hành').classes('store-nav-link ' + ('active' if active_tab == 'warranty' else '')).on('click', lambda: ui.navigate.to('/warranty'))
                                ui.label('Dịch Vụ').classes('store-nav-link ' + ('active' if active_tab == 'services' else '')).on('click', lambda: ui.navigate.to('/services'))

                    # 2. Right Actions (Cart, Login/Profile)
                    with ui.row().classes('items-center gap-3'):
                        # Cart quick button
                        @ui.refreshable
                        def render_store_cart():
                            curr_cart = app.storage.user.get('cart', [])
                            c_count = sum(i.get('qty', 1) for i in curr_cart)
                            with ui.button(
                                on_click=lambda: open_cart_dialog(on_cart_changed=render_store_cart.refresh)
                            ).classes('rounded-full px-3 h-9 ' + ('bg-blue-50 text-blue-600' if c_count > 0 else 'bg-gray-100 text-gray-600')).props('flat no-caps id="header-cart"'):
                                ui.icon('shopping_cart', size='18px')
                                ui.label(f'{c_count}').classes('ml-1 font-bold text-xs')
                        
                        render_store_cart()

                        if authenticated:
                            # User Profile Dropdown (Phân tách tuyệt đối giữa Admin, Staff và Customer)
                            with ui.button(full_name, icon='person').classes('bg-gray-100 text-gray-700 rounded-full h-9 px-4 font-semibold text-xs').props('flat no-caps id="user-profile"'):
                                with ui.menu().classes('min-w-[180px] rounded-xl overflow-hidden shadow-lg border border-gray-100'):
                                    if role == 'admin':
                                        ui.menu_item('Vào Quản Trị', on_click=lambda: ui.navigate.to('/admin')).classes('text-sm font-bold text-blue-600 hover:bg-blue-50')
                                        ui.menu_item('Cài Đặt Hệ Thống', on_click=lambda: ui.navigate.to('/admin/settings')).classes('text-sm font-medium hover:bg-blue-50 hover:text-blue-600')
                                    elif role == 'staff':
                                        ui.menu_item('Vào Quản Trị Bán Hàng', on_click=lambda: ui.navigate.to('/admin/orders')).classes('text-sm font-bold text-blue-600 hover:bg-blue-50')
                                        ui.menu_item('Cài Đặt Của Tôi', on_click=lambda: ui.navigate.to('/admin/settings')).classes('text-sm font-medium hover:bg-blue-50 hover:text-blue-600')
                                    else:
                                        ui.menu_item('Hồ sơ & Cài đặt', on_click=lambda: ui.navigate.to('/profile')).classes('text-sm font-medium hover:bg-blue-50 hover:text-blue-600')
                                        ui.menu_item('Đơn mua', on_click=lambda: ui.navigate.to('/orders')).classes('text-sm font-medium hover:bg-blue-50 hover:text-blue-600')
                                        ui.menu_item('Tra cứu bảo hành', on_click=lambda: ui.navigate.to('/warranty')).classes('text-sm font-medium text-blue-600 hover:bg-blue-50 font-semibold')
                                    ui.menu_item('Hướng dẫn sử dụng', on_click=lambda: restart_web_tour(role, 'store')).classes('text-sm font-medium hover:bg-blue-50 hover:text-blue-600')
                                    ui.separator()
                                    ui.menu_item('Đăng xuất', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).classes('text-sm font-medium text-red-600 hover:bg-red-50')
                        else:
                            ui.button('Đăng Nhập', on_click=lambda: ui.navigate.to('/login')).classes('bg-[#0071e3] text-white rounded-full h-9 px-6 font-semibold text-xs').props('flat no-caps id="user-profile"')
            
            # ── STORE CONTENT ──
            with ui.column().classes('w-full max-w-[1200px] mx-auto min-h-[80vh] px-4 md:px-8 py-6 gap-6'):
                func(*args, **kwargs)
                
            # ── STORE FOOTER ──
            with ui.element('footer').classes('w-full bg-white border-t border-gray-200 mt-12 py-12'):
                with ui.row().classes('w-full max-w-[1200px] mx-auto px-4 md:px-8 grid grid-cols-1 md:grid-cols-4 gap-8'):
                    with ui.column().classes('gap-3'):
                        with ui.row().classes('items-center gap-2 mb-2'):
                            ui.image('/static/assets/logo.svg').classes('w-8 h-8 rounded-lg grayscale')
                            ui.label('Laptop Store').classes('text-base font-extrabold text-gray-800')
                        ui.label('Mang đến những sản phẩm công nghệ chất lượng nhất với dịch vụ chuẩn mực.').classes('text-xs text-gray-500 leading-relaxed')
                    with ui.column().classes('gap-2'):
                        ui.label('Dịch Vụ Khách Hàng').classes('font-bold text-gray-900 mb-2')
                        ui.link('Chính sách bảo hành', '/warranty').classes('text-sm text-gray-500 hover:text-blue-600 no-underline')
                        ui.link('Chính sách đổi trả', '/services').classes('text-sm text-gray-500 hover:text-blue-600 no-underline')
                    with ui.column().classes('gap-2'):
                        ui.label('Hỗ Trợ').classes('font-bold text-gray-900 mb-2')
                        ui.label('Tổng đài: 1800 1234').classes('text-sm text-gray-500')
                        ui.label('Email: cskh@laptopstore.vn').classes('text-sm text-gray-500')
                    with ui.column().classes('gap-2'):
                        ui.label('Địa Chỉ').classes('font-bold text-gray-900 mb-2')
                        ui.label('123 Đường Công Nghệ, Quận 1, TP. HCM').classes('text-sm text-gray-500')
            
            # Onboarding tour check
            if not app.storage.user.get('web_tour_done'):
                show_web_tour(role, context='store')

        return wrapper
    return decorator
