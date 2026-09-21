from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container

def format_currency(amount):
    try:
        return f"{int(amount):,} ₫".replace(",", ".")
    except:
        return f"{amount} ₫"

@ui.page('/admin/inventory')
@admin_layout('Kho Hàng Laptop', active_tab='inventory')
def inventory_page():
    # RBAC Guard: Chỉ Admin và Staff mới có quyền truy cập Kho Hàng
    if app.storage.user.get('role') not in ('admin', 'staff'):
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm'):
            ui.icon('lock', size='54px').classes('text-red-400 mb-3')
            ui.label('Không Có Quyền Truy Cập Kho Hàng').classes('text-xl font-bold text-gray-800')
            ui.label('Chức năng quản trị và kiểm kê kho hàng chỉ dành riêng cho Quản trị viên và Nhân viên.').classes('text-sm text-gray-500 mt-1')
            ui.button('Về Trang Chủ', on_click=lambda: ui.navigate.to('/')).classes('mt-4 bg-[#0071e3] text-white rounded-xl').props('no-caps')
        return

    container = get_container()
    all_products = []
    if container.product_service:
        all_products = container.product_service.get_all_products() or []

    # Dynamic brands from data
    brands = sorted(list(set(str(p[4]) for p in all_products if len(p) > 4 and p[4])))
    brand_options = ['Tất cả Hãng'] + brands

    filter_state = {
        'search': '',
        'brand': 'Tất cả Hãng',
        'stock_filter': 'Tất cả',
    }

    def handle_export_excel():
        fetch_latest_data()
        import os
        from datetime import datetime
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        filename = f"danh_muc_kho_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(export_dir, filename)
        
        if container.exporter:
            success, msg = container.exporter.export_inventory_to_excel(all_products, filepath)
            if success:
                ui.notify(f'Xuất Excel thành công! Lưu tại: exports/{filename}', type='positive', position='top', timeout=6000)
            else:
                ui.notify(f'{msg}', type='negative')
        else:
            ui.notify('Lỗi: Tiện ích Exporter chưa sẵn sàng', type='negative')

    with ui.row().classes('w-full items-center justify-between mb-6 flex-wrap gap-4'):
        with ui.row().classes('items-center gap-4 flex-wrap'):
            search_input = ui.input(placeholder='Tìm theo tên / SKU / CPU...').classes('w-72 bg-white').props('outlined dense clearable')
            search_input.on('update:model-value', lambda e: update_search(e.args))

            brand_select = ui.select(brand_options, value='Tất cả Hãng').classes('w-44 bg-white').props('outlined dense')
            brand_select.on('update:model-value', lambda e: update_brand(e.args))

            stock_select = ui.select(['Tất cả', 'Còn hàng (>5)', 'Sắp hết (1-5)', 'Hết hàng (0)'], value='Tất cả').classes('w-44 bg-white').props('outlined dense')
            stock_select.on('update:model-value', lambda e: update_stock(e.args))

        with ui.row().classes('items-center gap-3'):
            total_badge = ui.label(f'Tổng: {len(all_products)} sản phẩm').classes('text-sm text-gray-500 font-medium')
            
            # Nút Xuất Excel (FR-10, TC-13)
            ui.button('Xuất Excel', on_click=handle_export_excel).classes(
                'bg-emerald-600 text-white font-semibold rounded-xl px-4 py-2 hover:bg-emerald-700 shadow-xs'
            ).props('no-caps icon=description')

            if app.storage.user.get('role') == 'admin':
                ui.button('+ Thêm Laptop', on_click=lambda: ui.navigate.to('/admin/product/new')).classes('bg-[#0071e3] text-white font-semibold rounded-xl px-4 py-2 hover:opacity-90 shadow-xs').props('no-caps')

    # Header row
    with ui.row().classes('w-full grid grid-cols-12 gap-4 px-4 py-2 border-b border-gray-200 text-xs font-bold text-gray-500 uppercase tracking-wider'):
        ui.label('SẢN PHẨM').classes('col-span-5')
        ui.label('CẤU HÌNH').classes('col-span-3')
        ui.label('GIÁ BÁN').classes('col-span-2 text-right')
        ui.label('TỒN KHO').classes('col-span-2 text-right')

    @ui.refreshable
    def render_product_list():
        filtered = []
        q = filter_state['search'].strip().lower()
        b = filter_state['brand']
        sf = filter_state['stock_filter']

        for p in all_products:
            p_id = p[0]
            name = str(p[2] or '').lower()
            brand = str(p[4] or '')
            stock = int(p[7] or 0)
            cpu = str(p[8] or '').lower()
            sku = str(p[17] if len(p) > 17 and p[17] else f"SKU-{p_id}").lower()

            # Search text filter
            if q and (q not in name and q not in sku and q not in cpu):
                continue

            # Brand filter
            if b != 'Tất cả Hãng' and brand != b:
                continue

            # Stock filter
            if sf == 'Còn hàng (>5)' and stock <= 5:
                continue
            elif sf == 'Sắp hết (1-5)' and (stock <= 0 or stock > 5):
                continue
            elif sf == 'Hết hàng (0)' and stock > 0:
                continue

            filtered.append(p)

        if not filtered:
            with ui.column().classes('w-full items-center justify-center py-16 bg-white rounded-xl border border-gray-100'):
                ui.icon('inventory_2', size='48px', color='grey-4')
                ui.label('Không tìm thấy sản phẩm phù hợp').classes('text-gray-500 font-medium mt-2')
            return

        with ui.column().classes('w-full gap-0 bg-white shadow-sm border border-gray-100 rounded-xl overflow-hidden'):
            for p in filtered:
                p_id = p[0]
                name = p[2] or 'Laptop chưa đặt tên'
                brand = p[4] or ''
                price = p[6] or 0
                stock = int(p[7] or 0)
                cpu = p[8] or "N/A"
                ram = p[9] or "N/A"
                ssd = p[11] or "N/A"
                gpu = p[12] or "N/A"
                sku = p[17] if len(p) > 17 and p[17] else f"SKU-{p_id}"
                
                with ui.row().classes('w-full grid grid-cols-12 gap-4 p-4 border-b border-gray-50 items-center hover:bg-gray-50/80 transition-colors'):
                    # Product Info (Thumbnail + Name + Brand + SKU)
                    is_gaming = any(k in (name or '') for k in ('Gaming', 'ROG', 'TUF', 'Nitro', 'Legion'))
                    img_src = '/static/assets/laptop_gaming.jpg' if is_gaming else '/static/assets/laptop_silver.jpg'
                    with ui.row().classes('col-span-5 items-center gap-4 flex-nowrap'):
                        ui.image(img_src).classes('w-14 h-14 rounded-lg object-contain bg-gray-50 flex-shrink-0 border border-gray-100 p-1')
                        with ui.column().classes('gap-0.5 overflow-hidden'):
                            ui.link(name, f'/admin/product/{p_id}').classes('font-semibold text-[#1d1d1f] hover:text-blue-600 text-sm line-clamp-1 no-underline')
                            with ui.row().classes('items-center gap-2'):
                                if brand:
                                    ui.label(brand).classes('text-[11px] font-bold text-gray-500 uppercase')
                                ui.label(f'SKU: {sku}').classes('text-[11px] text-gray-400')
                    
                    # Specs (CPU/GPU/RAM/SSD)
                    with ui.column().classes('col-span-3 gap-1 justify-center'):
                        with ui.row().classes('items-center gap-1.5'):
                            ui.icon('memory', size='16px').classes('text-gray-400')
                            ui.label(f"{cpu} • {gpu}").classes('text-xs text-gray-600 truncate max-w-[200px]')
                        with ui.row().classes('items-center gap-1.5'):
                            ui.icon('storage', size='16px').classes('text-gray-400')
                            ui.label(f"{ram} • {ssd}").classes('text-xs text-gray-600 truncate max-w-[200px]')

                    # Price
                    with ui.column().classes('col-span-2 items-end justify-center'):
                        ui.label(format_currency(price)).classes('font-bold text-[#1d1d1f] text-sm')

                    # Stock
                    with ui.row().classes('col-span-2 items-center justify-end gap-2'):
                        status_color = 'bg-emerald-500' if stock > 5 else ('bg-amber-500' if stock > 0 else 'bg-rose-500')
                        ui.element('div').classes(f'w-2 h-2 rounded-full {status_color}')
                        ui.label(str(stock)).classes('font-bold text-sm text-gray-800')
                        
                        # Quick action menu
                        with ui.button(icon='more_vert').props('flat round dense size=sm').classes('ml-2 text-gray-400 hover:text-gray-700'):
                            with ui.menu():
                                if app.storage.user.get('role') == 'admin':
                                    ui.menu_item('Chỉnh sửa', on_click=lambda pid=p_id: ui.navigate.to(f'/admin/product/{pid}'))
                                else:
                                    ui.menu_item('Xem thông số', on_click=lambda pid=p_id: ui.navigate.to(f'/admin/product/{pid}'))
                                ui.menu_item('Xem ngoài Shop', on_click=lambda pid=p_id: ui.navigate.to('/shop'))

    def update_search(val):
        filter_state['search'] = val or ''
        render_product_list.refresh()

    def update_brand(val):
        filter_state['brand'] = val or 'Tất cả Hãng'
        render_product_list.refresh()

    def update_stock(val):
        filter_state['stock_filter'] = val or 'Tất cả'
        render_product_list.refresh()

    def fetch_latest_data():
        nonlocal all_products
        if container.product_service:
            new_data = container.product_service.get_all_products() or []
            if new_data != all_products:
                all_products = new_data
                render_product_list.refresh()

    render_product_list()

