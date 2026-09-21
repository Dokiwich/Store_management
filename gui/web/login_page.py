"""Login page — Professional Apple-style login."""

from nicegui import ui, app

def build_login_page(container):
    """Render the login page with a background image and professional aesthetic."""

    ui.add_head_html('''
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body, .q-page { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
            .login-input .q-field__control { border-radius: 12px !important; height: 48px !important; background: #f9fafb; }
            .login-input .q-field__marginal { height: 48px !important; }
            .bg-image {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                object-fit: cover;
                z-index: -2;
            }
            .bg-overlay {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                z-index: -1;
            }
        </style>
    ''')

    # Background elements
    ui.element('img').classes('bg-image').props('src="/static/resources/images.jfif"')
    ui.element('div').classes('bg-overlay')

    with ui.column().classes('w-full min-h-screen items-center justify-center p-4'):

        # ── Login Card ──
        with ui.card().classes('w-[420px] max-w-full rounded-[24px] p-10 border-0').style(
            'box-shadow: 0 20px 40px rgba(0,0,0,0.2); background: rgba(255, 255, 255, 0.95);'
        ):
            # Logo + Heading
            with ui.column().classes('items-center w-full mb-8'):
                ui.image('/static/assets/logo.svg').classes('w-16 h-16 rounded-2xl mb-4 shadow-sm')
                ui.label('Laptop Store').classes(
                    'text-2xl font-semibold text-gray-900 tracking-tight'
                )
                ui.label('Đăng nhập vào hệ thống').classes('text-sm text-gray-500 mt-1')

            # ── Form ──
            username = ui.input(
                label='Tên đăng nhập',
            ).classes('w-full login-input').props('outlined dense')

            password = ui.input(
                label='Mật khẩu',
                password=True,
                password_toggle_button=True,
            ).classes('w-full mt-4 login-input').props('outlined dense')

            # Error label
            error_label = ui.label('').classes('text-red-500 text-sm mt-2 text-center w-full font-medium')
            error_label.visible = False

            async def handle_login():
                u = username.value.strip()
                p = password.value
                if not u or not p:
                    error_label.text = 'Vui lòng nhập đầy đủ thông tin'
                    error_label.visible = True
                    return

                user_info = container.user_service.login(u, p)
                if user_info:
                    app.storage.user.update({
                        'authenticated': True,
                        'id': user_info['id'],
                        'username': user_info['username'],
                        'full_name': user_info['full_name'],
                        'role': user_info['role'],
                        'cart': [],
                    })
                    ui.navigate.to('/')
                else:
                    error_label.text = 'Tài khoản hoặc mật khẩu không đúng'
                    error_label.visible = True
                    password.value = ''

            # Submit on Enter
            username.on('keydown.enter', handle_login)
            password.on('keydown.enter', handle_login)

            # Login button
            ui.button('Đăng Nhập', on_click=handle_login).classes(
                'w-full mt-8 rounded-2xl h-12 text-base font-semibold transition-all hover:opacity-90'
            ).style(
                'background-color: #0071e3; color: white; text-transform: none; box-shadow: 0 4px 14px rgba(0,113,227,0.3);'
            )

            # Forgot password
            ui.button('Quên mật khẩu?', on_click=lambda: ui.notify('Vui lòng liên hệ Quản trị viên (Admin) để được cấp lại mật khẩu.', type='info')).classes(
                'w-full mt-4 h-10 text-sm font-medium'
            ).props('flat no-caps color=primary')

        # Footer
        ui.label('© 2024 Laptop Store. All rights reserved.').classes(
            'text-white/60 text-xs mt-8'
        )
