from nicegui import ui, app
import json

def _inject_driver_js():
    """Injects Driver.js library into the page with a clean, professional modern theme."""
    ui.add_head_html('''
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.css"/>
        <script src="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.js.iife.js"></script>
        <style>
            .driver-popover {
                background: #ffffff !important;
                color: #0f172a !important;
                border-radius: 16px !important;
                padding: 20px !important;
                box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05) !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                max-width: 380px !important;
                border: 1px solid #e2e8f0 !important;
            }
            .driver-popover-arrow {
                border-color: #ffffff !important;
            }
            .driver-popover-title {
                font-weight: 700 !important;
                color: #0f172a !important;
                font-size: 15px !important;
                letter-spacing: -0.01em !important;
                margin-bottom: 6px !important;
            }
            .driver-popover-description {
                font-size: 13px !important;
                color: #475569 !important;
                line-height: 1.6 !important;
                margin-bottom: 16px !important;
            }
            .driver-popover-footer {
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                margin-top: 14px !important;
                padding-top: 12px !important;
                border-top: 1px solid #f1f5f9 !important;
            }
            .driver-popover-progress-text {
                font-size: 12px !important;
                color: #64748b !important;
                font-weight: 600 !important;
            }
            .driver-popover-navigation-btns {
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }
            .driver-popover-prev-btn, .driver-popover-next-btn {
                font-size: 12px !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                padding: 7px 14px !important;
                cursor: pointer !important;
                transition: all 0.15s ease !important;
                text-shadow: none !important;
            }
            .driver-popover-prev-btn {
                background-color: #f8fafc !important;
                color: #475569 !important;
                border: 1px solid #cbd5e1 !important;
            }
            .driver-popover-prev-btn:hover {
                background-color: #f1f5f9 !important;
                color: #0f172a !important;
            }
            .driver-popover-next-btn {
                background-color: #0071e3 !important;
                color: #ffffff !important;
                border: 1px solid transparent !important;
            }
            .driver-popover-next-btn:hover {
                background-color: #005bb5 !important;
            }
            .driver-popover-close-btn {
                color: #94a3b8 !important;
                font-size: 18px !important;
                top: 14px !important;
                right: 14px !important;
                transition: color 0.15s ease !important;
            }
            .driver-popover-close-btn:hover {
                color: #334155 !important;
            }
        </style>
    ''')

def show_web_tour(role: str, context: str = 'auto', force: bool = False):
    """
    Shows a streamlined onboarding tour tailored to the current view (store or admin).
    Checks `app.storage.user['web_tour_done']` unless `force=True`.
    """
    if not force and app.storage.user.get('web_tour_done', False):
        return

    _inject_driver_js()

    # Determine steps based on context
    is_admin_layout = (context == 'admin')

    if not is_admin_layout and context == 'auto':
        # Default store layout steps for customers & guests
        steps = [
            {
                'element': '#store-nav',
                'popover': {
                    'title': 'Menu Điều Hướng',
                    'description': 'Chuyển đổi nhanh chóng giữa Trang chủ sản phẩm, Dịch vụ chăm sóc khách hàng và Tra cứu hạn bảo hành.',
                    'side': 'bottom',
                    'align': 'start'
                }
            },
            {
                'element': '#search-filter-bar',
                'popover': {
                    'title': 'Tìm Kiếm & Bộ Lọc',
                    'description': 'Dễ dàng tra cứu theo tên sản phẩm, phân loại theo danh mục thương hiệu hoặc khoảng giá ngân sách.',
                    'side': 'bottom',
                    'align': 'center'
                }
            },
            {
                'element': '#header-cart',
                'popover': {
                    'title': 'Giỏ Hàng & Mua Sắm',
                    'description': 'Xem danh sách sản phẩm đã chọn, áp dụng mã khuyến mãi Voucher và tiến hành hoàn tất đơn hàng.',
                    'side': 'bottom',
                    'align': 'center'
                }
            },
            {
                'element': '#user-profile',
                'popover': {
                    'title': 'Tài Khoản & Cá Nhân',
                    'description': 'Quản lý thông tin cá nhân, tra cứu lịch sử mua hàng hoặc đăng nhập để hưởng ưu đãi thành viên.',
                    'side': 'bottom',
                    'align': 'end'
                }
            }
        ]
    else:
        # Admin / Staff control panel steps
        steps = [
            {
                'element': '#sidebar-menu',
                'popover': {
                    'title': 'Bảng Điều Khiển Quản Trị',
                    'description': 'Thanh menu bên trái giúp truy cập nhanh vào toàn bộ các phân hệ quản lý của hệ thống.',
                    'side': 'right',
                    'align': 'start'
                }
            },
            {
                'element': '#menu-inventory',
                'popover': {
                    'title': 'Quản Lý Kho Hàng',
                    'description': 'Kiểm tra số lượng tồn, cập nhật thông số kỹ thuật laptop và xuất báo cáo dữ liệu Excel.',
                    'side': 'right',
                    'align': 'start'
                }
            },
            {
                'element': '#menu-orders',
                'popover': {
                    'title': 'Lịch Sử Hoạt Động',
                    'description': 'Theo dõi toàn bộ hóa đơn bán ra và lịch sử các đợt nhập hàng theo thời gian thực.',
                    'side': 'right',
                    'align': 'start'
                }
            }
        ]

        if role == 'admin':
            steps.append({
                'element': '#menu-dashboard',
                'popover': {
                    'title': 'Báo Cáo & Thống Kê',
                    'description': 'Theo dõi biểu đồ doanh thu theo tháng/năm, sản phẩm bán chạy nhất và cảnh báo hàng sắp hết.',
                    'side': 'right',
                    'align': 'start'
                }
            })

        steps.extend([
            {
                'element': '#header-cart',
                'popover': {
                    'title': 'Bán Hàng Nhanh (POS)',
                    'description': 'Truy cập giỏ hàng bán hàng trực tiếp và in hóa đơn thanh toán PDF tiêu chuẩn cho khách.',
                    'side': 'bottom',
                    'align': 'center'
                }
            },
            {
                'element': '#user-profile',
                'popover': {
                    'title': 'Tài Khoản Đang Đăng Nhập',
                    'description': f'Thông tin tài khoản {role.capitalize()} và trạng thái phân quyền trong phiên làm việc.',
                    'side': 'bottom',
                    'align': 'end'
                }
            }
        ])

    steps_json = json.dumps(steps)

    js_code = f"""
        setTimeout(() => {{
            const driverFn = window.driver?.js?.driver || window.driver?.driver || (typeof window.driver === 'function' ? window.driver : null);
            if (!driverFn) {{
                console.warn("Driver.js not loaded or driver function missing.");
                return;
            }}
            try {{
                const allSteps = {steps_json};
                // Auto-filter steps to ensure elements exist in current page DOM
                const validSteps = allSteps.filter(s => {{
                    if (!s.element) return true;
                    const el = document.querySelector(s.element);
                    return el !== null && el.offsetParent !== null; // Element is visible
                }});

                if (validSteps.length === 0) return;

                const driverObj = driverFn({{
                    showProgress: true,
                    animate: true,
                    doneBtnText: 'Hoàn tất',
                    closeBtnText: 'Bỏ qua',
                    nextBtnText: 'Tiếp theo',
                    prevBtnText: 'Quay lại',
                    progressText: 'Bước {{{{current}}}} / {{{{total}}}}',
                    steps: validSteps,
                    onDestroyStarted: () => {{
                        driverObj.destroy();
                    }}
                }});
                setTimeout(() => {{ driverObj.drive(); }}, 400);
            }} catch (e) {{
                console.error("Error launching driver tour:", e);
            }}
        }}, 500);
    """

    ui.run_javascript(js_code)
    app.storage.user['web_tour_done'] = True

def restart_web_tour(role: str, context: str = 'auto'):
    """Force restarts the onboarding tour."""
    app.storage.user['web_tour_done'] = False
    show_web_tour(role, context=context, force=True)

