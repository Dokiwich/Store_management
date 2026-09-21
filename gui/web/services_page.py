"""Services & Customer Care page — Dịch vụ CSKH, Chính sách Đổi mới 1-đổi-1 và Hướng dẫn bảo hành."""

from nicegui import ui
from gui.web.store.layout import store_layout


@ui.page('/services')
@store_layout('Dịch Vụ & CSKH', active_tab='services')
def services_page():
    with ui.column().classes('w-full gap-8 max-w-[1200px] mx-auto'):

        # ── Hero Banner Dịch Vụ ──
        with ui.element('div').classes(
            'w-full rounded-3xl overflow-hidden relative p-8 md:p-10'
        ).style(
            'background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0284c7 100%);'
        ):
            with ui.column().classes('max-w-2xl gap-3 z-10 relative'):
                ui.label('DỊCH VỤ & HẬU MÃI').classes(
                    'text-xs font-bold text-sky-400 uppercase tracking-widest'
                )
                ui.label('Chính Sách Bảo Hành & Đổi Trả Laptop').classes(
                    'text-2xl sm:text-3xl font-extrabold text-white leading-tight'
                )
                ui.label(
                    'Laptop Store cam kết chính sách đổi mới 1-đổi-1 trong 30 ngày đầu với lỗi phần cứng, '
                    'bảo hành chính hãng 12 - 24 tháng và hỗ trợ kỹ thuật tận tâm.'
                ).classes('text-sm text-gray-200 mt-1 leading-relaxed')
                
                with ui.row().classes('gap-3 mt-4 items-center'):
                    ui.button(
                        'Tra Cứu Bảo Hành Ngay',
                        on_click=lambda: ui.navigate.to('/warranty')
                    ).props('color=white text-color=dark no-caps icon=verified_user').classes(
                        'font-bold px-6 py-2.5 rounded-xl shadow-md text-sm'
                    )

        # ── 3 Khối Chính Sách Cốt Lõi ──
        with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-3 gap-6'):
            # Khối 1: Đổi mới 30 ngày
            with ui.card().classes('p-6 rounded-2xl bg-white border border-gray-100 shadow-sm flex-col gap-3 h-full'):
                with ui.element('div').classes('w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 mb-1'):
                    ui.icon('published_with_changes', size='28px')
                ui.label('1 ĐỔI 1 TRONG 30 NGÀY').classes('font-bold text-base text-gray-900')
                ui.label(
                    'Áp dụng cho mọi dòng laptop phát sinh lỗi phần cứng từ nhà sản xuất trong vòng 30 ngày kể từ ngày mua. '
                    'Đổi máy mới cùng model hoặc nâng cấp tương đương.'
                ).classes('text-xs text-gray-600 leading-relaxed')

            # Khối 2: Bảo hành chính hãng
            with ui.card().classes('p-6 rounded-2xl bg-white border border-gray-100 shadow-sm flex-col gap-3 h-full'):
                with ui.element('div').classes('w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 mb-1'):
                    ui.icon('verified', size='28px')
                ui.label('BẢO HÀNH 12 – 24 THÁNG').classes('font-bold text-base text-gray-900')
                ui.label(
                    'Sản phẩm phân phối đầy đủ thông tin bảo hành chính hãng từ 12 đến 24 tháng. '
                    'Hỗ trợ tiếp nhận kiểm tra và gửi bảo hành nhanh chóng.'
                ).classes('text-xs text-gray-600 leading-relaxed')

            # Khối 3: Bảo dưỡng máy
            with ui.card().classes('p-6 rounded-2xl bg-white border border-gray-100 shadow-sm flex-col gap-3 h-full'):
                with ui.element('div').classes('w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 mb-1'):
                    ui.icon('build_circle', size='28px')
                ui.label('HỖ TRỢ KỸ THUẬT & VỆ SINH').classes('font-bold text-base text-gray-900')
                ui.label(
                    'Hỗ trợ vệ sinh laptop, tra keo tản nhiệt định kỳ và cài đặt phần mềm cơ bản '
                    'cho khách hàng đã mua laptop tại cửa hàng.'
                ).classes('text-xs text-gray-600 leading-relaxed')

        # ── Quy Trình Tiếp Nhận Bảo Hành ──
        with ui.card().classes('w-full p-6 sm:p-8 rounded-2xl bg-white border border-gray-100 shadow-sm'):
            ui.label('QUY TRÌNH TIẾP NHẬN BẢO HÀNH').classes('text-xs font-bold text-blue-600 uppercase tracking-wider mb-5')
            
            with ui.row().classes('w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'):
                def step_item(step_no, title, desc, icon):
                    with ui.column().classes('gap-2 p-4 rounded-xl bg-gray-50 border border-gray-100 h-full w-full'):
                        with ui.row().classes('items-center justify-between w-full'):
                            ui.label(f'BƯỚC {step_no}').classes('text-[11px] font-extrabold text-blue-600 uppercase tracking-widest')
                            ui.icon(icon, size='20px').classes('text-gray-400')
                        ui.label(title).classes('font-bold text-sm text-gray-900 mt-1')
                        ui.label(desc).classes('text-xs text-gray-500 leading-relaxed')

                step_item('1', 'Tiếp Nhận Máy', 'Khách mang máy đến cửa hàng, cung cấp Số điện thoại hoặc Mã đơn hàng.', 'contact_support')
                step_item('2', 'Kiểm Tra Kỹ Thuật', 'Kỹ thuật viên kiểm tra phần cứng và xác định lỗi thiết bị.', 'precision_manufacturing')
                step_item('3', 'Xử Lý Bảo Hành', 'Đổi mới (nếu trong 30 ngày) hoặc gửi bảo hành sửa chữa chính hãng.', 'rule')
                step_item('4', 'Bàn Giao Thiết Bị', 'Bàn giao máy hoàn thiện cho khách hàng và cập nhật phiếu bảo hành.', 'task_alt')

        # ── Thông Tin Cửa Hàng & Tiếp Nhận ──
        with ui.card().classes('w-full p-6 sm:p-8 rounded-2xl bg-gray-50 border border-gray-200/80 shadow-xs'):
            with ui.row().classes('items-start gap-4'):
                ui.icon('storefront', size='32px').classes('text-blue-600 mt-1 flex-shrink-0')
                with ui.column().classes('gap-2 flex-1'):
                    ui.label('THÔNG TIN TIẾP NHẬN BẢO HÀNH TẠI CỬA HÀNG').classes('font-bold text-sm text-gray-900 uppercase tracking-wider')
                    ui.label('Quý khách vui lòng mang thiết bị trực tiếp đến Cửa hàng Laptop Store để nhân viên kỹ thuật hỗ trợ kiểm tra và tiếp nhận.').classes('text-xs text-gray-600 leading-relaxed')
                    with ui.row().classes('gap-6 mt-2 flex-wrap text-xs text-gray-700'):
                        with ui.row().classes('items-center gap-1.5'):
                            ui.icon('schedule', size='16px').classes('text-gray-500')
                            ui.label('Thời gian làm việc: 08:30 – 18:00 (Thứ Hai – Thứ Bảy)')
                        with ui.row().classes('items-center gap-1.5'):
                            ui.icon('verified_user', size='16px').classes('text-gray-500')
                            ui.label('Tra cứu trực tuyến: Nhập Số điện thoại mua hàng tại trang Tra Cứu Bảo Hành')
