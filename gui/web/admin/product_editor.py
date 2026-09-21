from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container

@ui.page('/admin/product/{product_id}')
@admin_layout('Chi Tiết Sản Phẩm Laptop', active_tab='inventory')
def product_editor_page(product_id: str):
    # RBAC Guard: Chỉ Admin và Staff mới có quyền vào xem/sửa chi tiết quản trị
    if app.storage.user.get('role') not in ('admin', 'staff'):
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm'):
            ui.icon('lock', size='54px').classes('text-red-400 mb-3')
            ui.label('Không Có Quyền Truy Cập').classes('text-xl font-bold text-gray-800')
            ui.label('Trang quản trị thông số chi tiết chỉ dành riêng cho Quản trị viên và Nhân viên.').classes('text-sm text-gray-500 mt-1')
            ui.button('Về Trang Chủ', on_click=lambda: ui.navigate.to('/')).classes('mt-4 bg-[#0071e3] text-white rounded-xl').props('no-caps')
        return

    container = get_container()
    
    is_new = product_id == 'new'
    product = None
    if not is_new and container.product_service:
        try:
            product = container.product_service.get_product_by_id(int(product_id))
        except Exception:
            product = None

    # Base cols: 0:id, 1:sup, 2:name, 3:cat, 4:brand, 5:iprice, 6:price, 7:stock, 8:cpu, 9:ram, 10:scr, 11:hdd, 12:gpu, 13:wgt, 14:os, 15:desc, 16:act
    # New cols: 17:sku, 18:maxram, 19:panel, 20:bright, 21:batt, 22:color, 23:warr, 24:cond, 25:short, 26:high, 27:minstk
    data = {}
    if product:
        data = {
            'name': product[2] or '',
            'category': product[3] or 'Laptop',
            'brand': product[4] or 'Asus',
            'supplier_id': product[1] or 1,
            'sku': product[17] if len(product) > 17 and product[17] else f"SKU-{product_id}",
            'price': float(product[6] or 0),
            'import_price': float(product[5] or 0),
            'stock': int(product[7] or 0),
            'cpu': product[8] or '',
            'gpu': product[12] or '',
            'ram': product[9] or '',
            'ssd': product[11] or '',
            'screen': product[10] or '',
            'max_ram': product[18] if len(product) > 18 and product[18] else '',
            'panel': product[19] if len(product) > 19 and product[19] else '',
            'brightness': product[20] if len(product) > 20 and product[20] else '',
            'battery': product[21] if len(product) > 21 and product[21] else '',
            'color': product[22] if len(product) > 22 and product[22] else '',
            'weight': product[13] or '',
            'os': product[14] or '',
            'warranty': product[23] if len(product) > 23 and product[23] else '24 tháng',
            'condition': product[24] if len(product) > 24 and product[24] else 'New',
            'short_desc': product[25] if len(product) > 25 and product[25] else '',
            'highlights': product[26] if len(product) > 26 and product[26] else '',
            'full_desc': product[15] or '',
            'min_stock': int(product[27]) if len(product) > 27 and product[27] is not None else 5,
        }
    else:
        data = {
            'name': '', 'category': '', 'brand': '', 'supplier_id': 1,
            'sku': '', 'price': 0, 'import_price': 0, 'stock': 0,
            'cpu': '', 'gpu': '', 'ram': '', 'ssd': '', 'screen': '',
            'max_ram': '', 'panel': '', 'brightness': '', 'battery': '', 'color': '',
            'weight': '', 'os': '', 'warranty': '12 tháng', 'condition': 'New',
            'short_desc': '', 'highlights': '', 'full_desc': '', 'min_stock': 5
        }

    # Header / Hero Section
    with ui.row().classes('w-full justify-between items-start mb-6'):
        with ui.row().classes('gap-6 items-start'):
            # Image Box
            is_gaming = any(k in (data.get('name', '') or '') for k in ('Gaming', 'ROG', 'TUF', 'Nitro', 'Legion'))
            img_src = '/static/assets/laptop_gaming.jpg' if is_gaming else '/static/assets/laptop_silver.jpg'
            with ui.card().classes('w-44 h-44 justify-center items-center bg-gray-50 border border-gray-200 shadow-none p-3 overflow-hidden rounded-2xl'):
                ui.image(img_src).classes('w-full h-full object-contain')
            
            # Quick Info Form
            with ui.column().classes('gap-2'):
                name_input = ui.input('Tên sản phẩm', value=data.get('name', '')).classes('text-xl font-bold w-96').props('outlined dense')
                with ui.row().classes('gap-3 items-center'):
                    sku_input = ui.input('Mã SKU', value=data.get('sku', '')).classes('w-48').props('outlined dense')
                    condition_select = ui.select(['New', 'Like New 99%', 'Refurbished', 'Cũ'], value=data.get('condition', 'New')).classes('w-44').props('outlined dense')
                
                with ui.row().classes('gap-3 mt-1'):
                    price_input = ui.number('Giá bán (₫)', value=data.get('price', 0)).classes('w-36').props('outlined dense')
                    iprice_input = ui.number('Giá nhập (₫)', value=data.get('import_price', 0)).classes('w-36').props('outlined dense')
                    stock_input = ui.number('Tồn kho', value=data.get('stock', 0)).classes('w-28').props('outlined dense')
        
        # Action Buttons
        with ui.row().classes('gap-2 items-center'):
            ui.button('Quay lại', on_click=lambda: ui.navigate.to('/admin/inventory')).props('flat no-caps').classes('text-gray-600')
            if app.storage.user.get('role') == 'admin':
                save_btn = ui.button('Lưu vào CSDL', on_click=lambda: handle_save()).classes('bg-[#0071e3] text-white font-semibold px-6 py-2 rounded-xl shadow-md').props('no-caps')
            else:
                ui.label('Chế độ chỉ xem (Chỉ Admin mới có quyền lưu CSDL)').classes('text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded-xl font-medium border border-amber-200')

    # Tabs Section
    with ui.card().classes('w-full p-0 shadow-sm border border-gray-100 rounded-2xl overflow-hidden bg-white'):
        with ui.tabs().classes('w-full text-[#1d1d1f] border-b border-gray-100 bg-gray-50/50') as tabs:
            tab_overview = ui.tab('Tổng quan')
            tab_specs = ui.tab('Thông số kỹ thuật')
            tab_desc = ui.tab('Mô tả sản phẩm')
            tab_inventory = ui.tab('Kho & Bảo hành')
        
        with ui.tab_panels(tabs, value=tab_specs).classes('w-full p-6 bg-white'):
            
            with ui.tab_panel(tab_overview):
                ui.label('Phân loại & Thương hiệu').classes('text-sm font-bold text-gray-400 uppercase tracking-wider mb-4')
                with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-3 gap-4'):
                    brand_input = ui.input('Hãng sản xuất', value=data.get('brand', '')).props('outlined dense')
                    category_input = ui.input('Danh mục', value=data.get('category', '')).props('outlined dense')
                    supplier_id_input = ui.number('ID Nhà cung cấp', value=data.get('supplier_id', 1)).props('outlined dense')
                
            with ui.tab_panel(tab_specs):
                ui.label('THÔNG SỐ KỸ THUẬT (LAPTOP)').classes('text-sm font-bold text-gray-400 uppercase tracking-wider mb-6')
                with ui.row().classes('w-full grid grid-cols-2 md:grid-cols-3 gap-4'):
                    cpu_input = ui.input('CPU', value=data.get('cpu', '')).props('outlined dense')
                    gpu_input = ui.input('Card đồ họa (GPU)', value=data.get('gpu', '')).props('outlined dense')
                    ram_input = ui.input('Dung lượng RAM', value=data.get('ram', '')).props('outlined dense')
                    max_ram_input = ui.input('RAM tối đa hỗ trợ', value=data.get('max_ram', '')).props('outlined dense')
                    ssd_input = ui.input('Ổ cứng (SSD/HDD)', value=data.get('ssd', '')).props('outlined dense')
                    screen_input = ui.input('Kích thước & Độ phân giải', value=data.get('screen', '')).props('outlined dense')
                    panel_input = ui.input('Tấm nền (IPS/OLED/TN)', value=data.get('panel', '')).props('outlined dense')
                    bright_input = ui.input('Độ sáng màn hình', value=data.get('brightness', '')).props('outlined dense')
                    batt_input = ui.input('Dung lượng Pin', value=data.get('battery', '')).props('outlined dense')
                    color_input = ui.input('Màu sắc', value=data.get('color', '')).props('outlined dense')
                    weight_input = ui.input('Trọng lượng (kg)', value=data.get('weight', '')).props('outlined dense')
                    os_input = ui.input('Hệ điều hành', value=data.get('os', '')).props('outlined dense')

            with ui.tab_panel(tab_desc):
                ui.label('MÔ TẢ SẢN PHẨM').classes('text-sm font-bold text-gray-400 uppercase tracking-wider mb-4')
                short_desc_input = ui.textarea('Mô tả ngắn (Short Description)', value=data.get('short_desc', '')).props('outlined autogrow').classes('w-full mb-4')
                highlights_input = ui.textarea('Điểm nổi bật (Highlights - mỗi dòng 1 ý)', value=data.get('highlights', '')).props('outlined autogrow').classes('w-full mb-4')
                full_desc_input = ui.textarea('Bài viết chi tiết (Full Description)', value=data.get('full_desc', '')).props('outlined autogrow').classes('w-full h-48')

            with ui.tab_panel(tab_inventory):
                ui.label('QUẢN LÝ KHO & BẢO HÀNH').classes('text-sm font-bold text-gray-400 uppercase tracking-wider mb-4')
                with ui.row().classes('gap-4'):
                    min_stock_input = ui.number('Cảnh báo tồn tối thiểu', value=data.get('min_stock', 5)).props('outlined dense')
                    warranty_input = ui.input('Thời gian bảo hành', value=data.get('warranty', '24 tháng')).props('outlined dense')

    def handle_save():
        if app.storage.user.get('role') != 'admin':
            ui.notify('Chỉ Quản trị viên (Admin) mới có quyền lưu chỉnh sửa!', type='negative')
            return

        n = name_input.value.strip()
        if not n:
            ui.notify('Vui lòng nhập tên sản phẩm!', type='warning')
            return
        
        pr = float(price_input.value or 0)
        ipr = float(iprice_input.value or 0)
        stk = int(stock_input.value or 0)
        br = brand_input.value.strip() or 'Khác'
        cat = category_input.value.strip() or 'Laptop'
        sup = int(supplier_id_input.value or 1)

        kwargs = {
            'sku': sku_input.value.strip(),
            'max_ram': max_ram_input.value.strip(),
            'panel': panel_input.value.strip(),
            'brightness': bright_input.value.strip(),
            'battery': batt_input.value.strip(),
            'color': color_input.value.strip(),
            'warranty': warranty_input.value.strip(),
            'condition': condition_select.value,
            'short_desc': short_desc_input.value.strip(),
            'highlights': highlights_input.value.strip(),
            'min_stock': int(min_stock_input.value or 5),
        }

        success = False
        if is_new:
            success = container.product_service.add_product(
                n, cat, br, sup, ipr, pr, stk,
                cpu_input.value.strip(), ram_input.value.strip(),
                screen_input.value.strip(), ssd_input.value.strip(),
                gpu_input.value.strip(), weight_input.value.strip(),
                os_input.value.strip(), full_desc_input.value.strip(),
                **kwargs
            )
        else:
            success = container.product_service.update_product(
                int(product_id), n, cat, br, sup, ipr, pr, stk,
                cpu_input.value.strip(), ram_input.value.strip(),
                screen_input.value.strip(), ssd_input.value.strip(),
                gpu_input.value.strip(), weight_input.value.strip(),
                os_input.value.strip(), full_desc_input.value.strip(),
                **kwargs
            )

        if success:
            ui.notify('Đã cập nhật sản phẩm vào CSDL thành công!', type='positive')
            ui.timer(0.6, lambda: ui.navigate.to('/admin/inventory'), once=True)
        else:
            ui.notify('Lỗi lưu CSDL! Vui lòng kiểm tra lại kết nối.', type='negative')

