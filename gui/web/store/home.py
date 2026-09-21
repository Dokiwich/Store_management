"""Shop page — Professional Apple-style product grid with detailed cards, filters, cart, and detail modal."""

from nicegui import ui, app
from gui.web.store.layout import store_layout
from logic.service_container import get_container

# ─── Brand colour palette ───
BRAND_BG = {
    'Apple': '#f5f5f7', 'Dell': '#f3f4f6', 'Asus': '#f3f4f6',
    'HP': '#f3f4f6', 'Acer': '#f3f4f6', 'Lenovo': '#f3f4f6',
    'MSI': '#f3f4f6', 'LG': '#f3f4f6', 'Samsung': '#f3f4f6',
}

ITEMS_PER_PAGE = 10

def _inject_styles():
    ui.add_head_html('''
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            body, .q-page { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
            .product-card {
                transition: all 0.3s ease;
                border: 1px solid rgba(0,0,0,0.05);
            }
            .product-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 32px rgba(0,0,0,0.08) !important;
                border: 1px solid rgba(0,0,0,0.1);
            }
            .line-clamp-2 {
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .sidebar-btn { transition: all 0.2s ease; }
            .sidebar-btn:hover { background: #f5f5f7 !important; }
            .custom-scrollbar::-webkit-scrollbar { width: 6px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
        </style>
    ''')

# ═══════════════════════════════════════════════════
#  MAIN PAGE BUILDER
# ═══════════════════════════════════════════════════

@ui.page('/')
@store_layout('Trang Chủ', active_tab='home')
def store_home_page():
    """Build the complete shop page."""
    container = get_container()
    user = app.storage.user
    _inject_styles()

    # ── Page-level state ──
    state = {
        'page': 1,
        'products': [],
    }

    # ═══════════════════════════════════════════════
    #  MAIN CONTENT
    # ═══════════════════════════════════════════════
    with ui.column().classes('w-full gap-0'):

        # ── Hero Banner ──
        with ui.element('div').classes(
            'w-full rounded-3xl overflow-hidden relative mb-8'
        ).style(
            'height: 220px; background: linear-gradient(135deg, #111827 0%, #374151 100%);'
        ):
            # Text overlay
            with ui.element('div').classes('absolute inset-0 flex items-center px-12 z-10'):
                with ui.column().classes('gap-1 max-w-lg'):
                    ui.label('Laptop Store').classes('text-sm font-semibold text-blue-400 uppercase tracking-wider')
                    ui.label('Khám phá bộ sưu tập mới nhất').classes(
                        'text-3xl sm:text-4xl font-bold text-white tracking-tight leading-tight mt-1'
                    )
                    ui.label('Ưu đãi hấp dẫn — Miễn phí giao hàng toàn quốc').classes(
                        'text-base text-gray-300 mt-2'
                    )
                    ui.button('Khám phá danh mục', icon='arrow_downward', on_click=lambda: ui.run_javascript("document.getElementById('product-catalog')?.scrollIntoView({behavior: 'smooth'})")).classes(
                        'mt-5 rounded-full h-10 px-6 text-sm font-semibold transition-all hover:opacity-90'
                    ).style('background: #3b82f6; color: white; text-transform: none; box-shadow: 0 4px 12px rgba(59,130,246,0.3);').props('no-caps')
            
            # Background image
            ui.image('/static/assets/laptop_silver.jpg').classes(
                'absolute right-0 top-0 h-full w-1/2 object-cover opacity-35 mix-blend-overlay'
            )

        # ── Filter Bar ──
        with ui.card().classes('w-full rounded-[20px] mb-6 p-2').props('flat bordered id="search-filter-bar"').style('border-color: #e5e7eb;'):
            with ui.row().classes('w-full items-center gap-4 p-2 flex-wrap'):
                search_kw = ui.input(placeholder='Tìm kiếm sản phẩm...').classes(
                    'flex-1 min-w-[240px]'
                ).props('outlined dense rounded bg-gray-50')
                search_kw.props('prepend-icon=search')

                categories = ['Tất cả'] + container.product_service.get_all_categories()
                cat_select = ui.select(categories, value='Tất cả', label='Danh mục').classes(
                    'w-40'
                ).props('outlined dense')

                brands = ['Tất cả'] + container.product_service.get_all_brands()
                brand_select = ui.select(brands, value='Tất cả', label='Hãng').classes(
                    'w-40'
                ).props('outlined dense')

                price_opts = ['Tất cả', '< 10 Triệu', '10 - 20 Triệu', '20 - 30 Triệu', '> 30 Triệu']
                price_select = ui.select(price_opts, value='Tất cả', label='Mức giá').classes(
                    'w-40'
                ).props('outlined dense')

                ui.button('Lọc kết quả', on_click=lambda: _apply()).classes(
                    'rounded-xl h-10 px-6 text-sm font-semibold'
                ).style('background-color: #111827; color: white; text-transform: none;')

        # ── Results count ──
        count_label = ui.label('').classes('text-sm font-medium text-gray-500 mb-4')

        # ── Product Grid ──
        grid_container = ui.row().classes('w-full flex-wrap gap-6 justify-start')

        # ── Pagination ──
        pagination_container = ui.row().classes('justify-center mt-10 gap-2 w-full')

        # ═══ Logic ═══
        def _apply():
            kw = search_kw.value.strip() if search_kw.value else None
            cat = cat_select.value if cat_select.value != 'Tất cả' else None
            brand_val = brand_select.value if brand_select.value != 'Tất cả' else None
            price_val = price_select.value if price_select.value != 'Tất cả' else None

            state['products'] = container.product_service.filter_products(
                category=cat, brand=brand_val, price_range=price_val, keyword=kw,
            )
            state['page'] = 1
            _render()

        def _render():
            grid_container.clear()
            pagination_container.clear()

            products = state['products']
            total = len(products)
            start = (state['page'] - 1) * ITEMS_PER_PAGE
            end = min(start + ITEMS_PER_PAGE, total)
            page_products = products[start:end]
            total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

            count_label.text = f'Hiển thị {end} trên tổng số {total} sản phẩm'

            if not products:
                with grid_container:
                    with ui.column().classes('items-center justify-center py-24 w-full'):
                        ui.icon('search_off').classes('text-6xl text-gray-300 mb-4')
                        ui.label('Không tìm thấy sản phẩm nào').classes('text-lg text-gray-900 font-medium')
                        ui.label('Vui lòng thử lại với từ khóa khác').classes('text-sm text-gray-500 mt-1')
                return

            with grid_container:
                for p in page_products:
                    _build_card(p, container)

            # Pagination buttons
            if total_pages > 1:
                with pagination_container:
                    ui.button(icon='chevron_left', on_click=lambda: _go(state['page'] - 1)).classes(
                        'rounded-xl w-10 h-10'
                    ).props('flat dense color=dark' + (' disable' if state['page'] <= 1 else ''))

                    for pg in range(1, total_pages + 1):
                        cur = pg == state['page']
                        ui.button(str(pg), on_click=lambda p=pg: _go(p)).classes(
                            'rounded-xl w-10 h-10 text-sm font-semibold'
                        ).style(
                            f'background: {"#111827" if cur else "transparent"}; '
                            f'color: {"white" if cur else "#374151"};'
                        ).props('flat dense')

                    ui.button(icon='chevron_right', on_click=lambda: _go(state['page'] + 1)).classes(
                        'rounded-xl w-10 h-10'
                    ).props('flat dense color=dark' + (' disable' if state['page'] >= total_pages else ''))

        def _go(page):
            total_pages = max(1, (len(state['products']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
            if 1 <= page <= total_pages:
                state['page'] = page
                _render()

        search_kw.on('keydown.enter', lambda: _apply())
        _apply()

        # ── Sticky Quick-Cart Floating Widget ──
        @ui.refreshable
        def render_floating_cart():
            curr_cart = app.storage.user.get('cart', [])
            total_count = sum(i.get('qty', 1) for i in curr_cart)
            total_val = sum(float(i['price']) * int(i.get('qty', 1)) for i in curr_cart)
            if total_count > 0:
                with ui.element('div').classes('fixed bottom-8 right-8 z-40'):
                    with ui.button(on_click=lambda: open_cart_dialog(container, on_cart_changed=render_floating_cart.refresh)).classes(
                        'bg-[#111827] text-white px-5 h-14 rounded-full shadow-2xl flex items-center gap-3 hover:scale-105 transition-all border border-gray-700'
                    ).props('no-caps'):
                        ui.icon('shopping_bag', size='22px').classes('text-blue-400')
                        with ui.column().classes('gap-0 text-left'):
                            ui.label(f'{total_count} sản phẩm').classes('text-xs font-bold text-white leading-tight')
                            ui.label(f'{total_val:,.0f} ₫').classes('text-[11px] font-semibold text-emerald-400 leading-tight')
                        ui.icon('chevron_right', size='18px').classes('text-gray-400')

        render_floating_cart()

# ═══════════════════════════════════════════════════
#  PRODUCT CARD
# ═══════════════════════════════════════════════════

def _build_card(product, container):
    """Render a professional product card."""
    p_id = product[0]
    name = product[2] or 'Sản phẩm'
    brand = product[4] or ''
    price = float(product[6]) if product[6] else 0
    stock = int(product[7]) if product[7] else 0
    cpu = str(product[8] or '')
    ram = str(product[9] or '')
    screen = str(product[10]) if len(product) > 10 and product[10] else ''
    hdd = str(product[11]) if len(product) > 11 and product[11] else ''
    
    old_price = price * 1.05
    discount_pct = 5
    bg = BRAND_BG.get(brand, '#f9fafb')

    with ui.card().tight().classes(
        'product-card rounded-[20px] overflow-hidden cursor-pointer bg-white flex-col flex'
    ).style('width: 240px; flex-shrink: 0;').on('click', lambda: _show_detail(p_id, container)):

        # Image area
        is_gaming = 'Gaming' in (product[3] or '') or any(k in name for k in ('ROG', 'TUF', 'Nitro', 'Legion', 'Gaming'))
        img_src = '/static/assets/laptop_gaming.jpg' if is_gaming else '/static/assets/laptop_silver.jpg'

        with ui.element('div').classes('relative w-full h-48 flex items-center justify-center p-3 bg-white overflow-hidden'):
            ui.image(img_src).classes('w-full h-full object-contain hover:scale-105 transition-transform duration-300')
            
            # Badges
            with ui.row().classes('absolute top-3 left-3 right-3 justify-between items-start'):
                ui.label(f'-{discount_pct}%').classes(
                    'text-[10px] font-bold px-2 py-1 rounded bg-red-500 text-white leading-none tracking-wide'
                )
                if price >= 15_000_000:
                    ui.label('Trả góp 0%').classes(
                        'text-[10px] font-semibold px-2 py-1 rounded bg-white text-blue-600 border border-blue-100 leading-none tracking-wide'
                    )

            if stock <= 0:
                with ui.element('div').classes('absolute inset-0 bg-white/60 flex items-center justify-center backdrop-blur-[2px]'):
                    ui.label('Tạm hết hàng').classes('text-gray-900 font-bold text-xs bg-white px-4 py-1.5 rounded-full shadow-sm border border-gray-200')

        # Content area
        with ui.column().classes('p-4 flex-1 w-full gap-0'):
            # Brand & CPU
            with ui.row().classes('w-full justify-between items-center mb-1'):
                ui.label(brand).classes('text-[10px] font-bold text-gray-400 uppercase tracking-wider')
                
                # CPU Highlight
                cpu_label = ''
                if cpu:
                    for kw in ('M1', 'M2', 'M3', 'M4', 'i5', 'i7', 'i9', 'Ryzen'):
                        if kw in cpu:
                            cpu_label = kw
                            break
                if cpu_label:
                    ui.label(cpu_label).classes('text-[10px] font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded')

            # Title
            ui.label(name).classes('text-[14px] font-semibold text-gray-900 line-clamp-2 leading-snug h-10')

            # Specs
            specs = [s for s in (ram, hdd, screen) if s]
            if specs:
                ui.label(' • '.join(specs)).classes('text-[11px] font-medium text-gray-500 mt-2 truncate w-full')

            ui.element('div').classes('flex-1') # Spacer

            # Price
            with ui.column().classes('mt-4 gap-0 w-full'):
                ui.label(f'{price:,.0f} ₫').classes('text-[16px] font-bold text-red-600')
                ui.label(f'{old_price:,.0f} ₫').classes('text-[12px] text-gray-400 line-through')

            # Promo tag
            with ui.row().classes('w-full items-center gap-1 mt-3 bg-red-50 rounded px-2 py-1.5 border border-red-100'):
                ui.icon('local_offer').classes('text-[12px] text-red-500')
                ui.label('Giảm thêm cho thành viên').classes('text-[10px] font-medium text-red-700')

            # Actions row
            with ui.row().classes('w-full justify-between items-center mt-3 pt-2.5 border-t border-gray-100'):
                ui.button('Xem chi tiết', icon='visibility', on_click=lambda: _show_detail(p_id, container)).classes(
                    'text-xs font-semibold text-blue-600 hover:text-blue-800'
                ).props('flat dense no-caps')
                if stock > 0:
                    ui.button(icon='add_shopping_cart', on_click=lambda: _add_to_cart(product, container)).classes(
                        'bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white rounded-lg text-xs font-medium px-2 py-1 transition-colors'
                    ).props('flat dense no-caps')

# ═══════════════════════════════════════════════════
#  PRODUCT DETAIL DIALOG
# ═══════════════════════════════════════════════════

def _show_detail(p_id, container):
    product = container.product_service.get_product_by_id(p_id)
    if not product:
        ui.notify('Sản phẩm không tồn tại', type='negative')
        return

    name = product[2] or ''
    brand = product[4] or ''
    price = float(product[6]) if product[6] else 0
    stock = int(product[7]) if product[7] else 0
    cpu = str(product[8] or 'Đang cập nhật')
    ram = str(product[9] or 'Đang cập nhật')
    screen = str(product[10]) if len(product) > 10 and product[10] else 'Đang cập nhật'
    hdd = str(product[11]) if len(product) > 11 and product[11] else 'Đang cập nhật'
    gpu = str(product[12]) if len(product) > 12 and product[12] else 'Đang cập nhật'
    weight = str(product[13]) if len(product) > 13 and product[13] else ''
    os_name = str(product[14]) if len(product) > 14 and product[14] else ''
    desc = str(product[15]) if len(product) > 15 and product[15] else ''
    
    # New fields
    sku = str(product[17]) if len(product) > 17 and product[17] else f'SKU-{p_id}'
    max_ram = str(product[18]) if len(product) > 18 and product[18] else ''
    panel = str(product[19]) if len(product) > 19 and product[19] else ''
    brightness = str(product[20]) if len(product) > 20 and product[20] else ''
    battery = str(product[21]) if len(product) > 21 and product[21] else ''
    color = str(product[22]) if len(product) > 22 and product[22] else ''
    warranty = str(product[23]) if len(product) > 23 and product[23] else '12 tháng'
    condition = str(product[24]) if len(product) > 24 and product[24] else 'Mới'
    short_desc = str(product[25]) if len(product) > 25 and product[25] else ''
    highlights = str(product[26]) if len(product) > 26 and product[26] else ''

    bg = BRAND_BG.get(brand, '#f9fafb')

    is_gaming = any(k in name for k in ('Gaming', 'ROG', 'TUF', 'Nitro', 'Legion'))
    img_src = '/static/assets/laptop_gaming.jpg' if is_gaming else '/static/assets/laptop_silver.jpg'

    with ui.dialog() as dlg, ui.card().classes(
        'w-[900px] max-w-[95vw] rounded-[24px] p-0 overflow-hidden bg-white shadow-2xl'
    ):
        ui.button(icon='close', on_click=dlg.close).classes(
            'absolute top-4 right-4 z-20 rounded-full bg-white/80 text-gray-600 hover:bg-gray-100'
        ).props('flat round dense').style('backdrop-filter: blur(8px);')

        # Header Image (Hero)
        with ui.element('div').classes('w-full h-80 flex items-center justify-center relative bg-gray-50/60 p-6'):
            ui.image(img_src).classes('w-full h-full object-contain drop-shadow-lg')
            with ui.row().classes('absolute bottom-4 left-6'):
                ui.label(brand).classes('text-xs font-bold text-gray-600 bg-white/90 px-3 py-1 rounded-full uppercase tracking-widest')
                ui.label(f'SKU: {sku}').classes('text-xs font-bold text-gray-600 bg-white/90 px-3 py-1 rounded-full')

        # Content
        with ui.element('div').classes('px-8 py-6 custom-scrollbar').style('max-height: 60vh; overflow-y: auto;'):
            ui.label(name).classes('text-3xl font-bold text-[#1d1d1f] leading-tight')
            
            if short_desc:
                ui.label(short_desc).classes('text-sm text-gray-500 mt-2')

            # Price & Stock row
            with ui.row().classes('items-end justify-between w-full mt-6 pb-6 border-b border-gray-100'):
                with ui.row().classes('items-baseline gap-3'):
                    ui.label(f'{price:,.0f} ₫').classes('text-3xl font-bold text-[#1d1d1f] tracking-tight')
                    ui.label(f'{price * 1.05:,.0f} ₫').classes('text-lg text-gray-400 line-through')
                
                with ui.row().classes('gap-3'):
                    if stock > 0:
                        with ui.row().classes('items-center gap-1 text-green-700 bg-green-50 px-3 py-1.5 rounded-full border border-green-100'):
                            ui.icon('check_circle', size='sm')
                            ui.label(f'Còn {stock} sản phẩm').classes('text-sm font-semibold')
                    else:
                        with ui.row().classes('items-center gap-1 text-red-700 bg-red-50 px-3 py-1.5 rounded-full border border-red-100'):
                            ui.icon('error_outline', size='sm')
                            ui.label('Hết hàng').classes('text-sm font-semibold')
                    
                    with ui.row().classes('items-center gap-1 text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100'):
                        ui.icon('verified', size='sm')
                        ui.label(f'Bảo hành {warranty}').classes('text-sm font-semibold')

            # Content split: Highlights vs Specs
            with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-3 gap-8 mt-6'):
                
                # Left Col (Highlights & Desc)
                with ui.column().classes('col-span-2 gap-6'):
                    if highlights:
                        with ui.column().classes('w-full bg-gray-50 p-6 rounded-2xl border border-gray-100'):
                            ui.label('ĐẶC ĐIỂM NỔI BẬT').classes('text-xs font-bold text-gray-400 mb-2 tracking-wider')
                            ui.label(highlights).classes('text-sm text-[#1d1d1f] whitespace-pre-line leading-relaxed')

                    if desc:
                        with ui.column().classes('w-full'):
                            ui.label('MÔ TẢ SẢN PHẨM').classes('text-xs font-bold text-gray-400 mb-2 tracking-wider')
                            ui.label(desc).classes('text-sm text-gray-600 leading-relaxed whitespace-pre-line')

                # Right Col (Specs)
                with ui.column().classes('col-span-1'):
                    ui.label('THÔNG SỐ KỸ THUẬT').classes('text-xs font-bold text-gray-400 mb-4 tracking-wider')
                    
                    specs = [
                        ('CPU', cpu), ('GPU', gpu), ('RAM', ram), 
                        ('Max RAM', max_ram), ('Ổ cứng', hdd), 
                        ('Màn hình', screen), ('Tấm nền', panel),
                        ('Độ sáng', brightness), ('Pin', battery),
                        ('Trọng lượng', weight), ('Màu sắc', color),
                        ('Hệ điều hành', os_name), ('Tình trạng', condition)
                    ]
                    
                    for label, value in specs:
                        if value and value != 'Đang cập nhật':
                            with ui.row().classes('w-full justify-between items-start py-2 border-b border-gray-100 last:border-0'):
                                ui.label(label).classes('text-xs text-gray-500 w-1/3')
                                ui.label(value).classes('text-sm font-semibold text-[#1d1d1f] w-2/3 text-right')

        # Footer Actions
        with ui.row().classes('w-full justify-end items-center gap-3 p-6 bg-gray-50 border-t border-gray-100'):
            ui.button('Đóng', on_click=dlg.close).classes(
                'rounded-xl h-12 px-6 text-sm font-medium text-gray-700 hover:bg-gray-200'
            ).props('flat no-caps')

            add_btn = ui.button(
                'Thêm vào giỏ hàng',
                on_click=lambda: _add_to_cart(product, container, dlg),
            ).classes('rounded-xl h-12 px-8 text-sm font-semibold transition-transform hover:scale-105').style(
                'background-color: #3b82f6; color: white; text-transform: none; box-shadow: 0 4px 12px rgba(59,130,246,0.3);'
            ).props('icon=shopping_cart')
            if stock <= 0:
                add_btn.disable()

    dlg.open()


# ═══════════════════════════════════════════════════
#  CART INTEGRATION
# ═══════════════════════════════════════════════════

from gui.web.cart_dialog import open_cart_dialog


def _add_to_cart(product, container, dialog=None):
    p_id = product[0]
    name = product[2]
    price = float(product[6])
    stock = int(product[7])

    cart = app.storage.user.get('cart', [])

    for item in cart:
        if item['id'] == p_id:
            if item['qty'] < stock:
                item['qty'] += 1
                item['total'] = item['qty'] * price
                app.storage.user['cart'] = cart
                ui.notify(f'Đã tăng số lượng {name} lên {item["qty"]}', type='positive')
            else:
                ui.notify(f'Sản phẩm {name} đã đạt giới hạn tồn kho ({stock})', type='warning')
            if dialog:
                dialog.close()
            open_cart_dialog(container)
            return

    cart.append({'id': p_id, 'name': name, 'price': price, 'qty': 1, 'total': price})
    app.storage.user['cart'] = cart
    ui.notify(f'Đã thêm {name} vào giỏ hàng!', type='positive')
    if dialog:
        dialog.close()
    open_cart_dialog(container)


def _logout():
    app.storage.user.clear()
    ui.navigate.to('/login')

