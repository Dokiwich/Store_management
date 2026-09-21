from nicegui import ui, app
from gui.web.admin.layout import admin_layout
from logic.service_container import get_container

def format_currency(amount):
    try:
        val = float(amount or 0)
        if val >= 1_000_000_000:
            return f"{val / 1_000_000_000:.1f}B ₫"
        if val >= 1_000_000:
            return f"{val / 1_000_000:.1f}M ₫"
        return f"{int(val):,} ₫".replace(",", ".")
    except:
        return f"{amount} ₫"

@ui.page('/admin')
@admin_layout('Thống Kê Doanh Thu', active_tab='dashboard')
def dashboard_page():
    # RBAC Guard: Chỉ Quản Trị Viên (Admin) mới có quyền xem số liệu tài chính doanh thu
    if app.storage.user.get('role') != 'admin':
        with ui.column().classes('w-full items-center justify-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm'):
            ui.icon('lock', size='54px').classes('text-red-400 mb-3')
            ui.label('Không Có Quyền Truy Cập Bảng Điều Khiển').classes('text-xl font-bold text-gray-800')
            ui.label('Báo cáo thống kê tài chính và phân tích doanh thu chỉ dành riêng cho Quản Trị Viên (Admin).').classes('text-sm text-gray-500 mt-1')
            ui.button('Về Trang Chủ', on_click=lambda: ui.navigate.to('/')).classes('mt-4 bg-[#0071e3] text-white rounded-xl').props('no-caps')
        return

    container = get_container()
    products = []
    stats = {"revenue": 0, "orders": 0, "customers": 0, "low_stock": 0}
    top_selling = []
    years = [2026, 2025, 2024]
    current_year_state = {'year': 2026}

    if container.product_service:
        products = container.product_service.get_all_products() or []
    if container.report_service:
        try:
            stats = container.report_service.get_summary_stats() or stats
            top_selling = container.report_service.get_top_selling_products(limit=5) or []
            db_years = container.report_service.get_available_years()
            if db_years:
                years = db_years
                current_year_state['year'] = db_years[0]
        except Exception:
            pass

    total_stock = sum(int(p[7] or 0) for p in products)
    low_stock_products = [p for p in products if p[7] is not None and int(p[7]) <= 5]

    # KPI Cards
    with ui.row().classes('w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8'):
        def kpi_card(title, value, icon, bg_color, text_color):
            with ui.card().classes('p-5 items-center justify-between flex-row shadow-sm rounded-2xl border border-gray-100 bg-white'):
                with ui.column().classes('gap-1'):
                    ui.label(title).classes('text-xs text-gray-500 font-bold uppercase tracking-wider')
                    ui.label(value).classes('text-2xl font-bold text-[#1d1d1f]')
                with ui.element('div').classes(f'w-12 h-12 rounded-xl flex items-center justify-center {bg_color}'):
                    ui.icon(icon, size='24px').classes(text_color)

        kpi_card('Tổng doanh thu', format_currency(stats.get('revenue', 0)), 'payments', 'bg-blue-50', 'text-blue-600')
        kpi_card('Tổng đơn hàng', str(stats.get('orders', 0)), 'receipt_long', 'bg-purple-50', 'text-purple-600')
        kpi_card('Khách hàng', str(stats.get('customers', 0)), 'group', 'bg-emerald-50', 'text-emerald-600')
        kpi_card('Laptop tồn kho', f"{total_stock} máy", 'laptop_mac', 'bg-amber-50', 'text-amber-600')

    # Chart Section (FR-09: Thống kê doanh thu theo năm tùy chọn)
    with ui.card().classes('w-full shadow-sm rounded-2xl border border-gray-100 p-6 mb-8 bg-white'):
        with ui.row().classes('w-full justify-between items-center mb-4 flex-wrap gap-3'):
            with ui.column().classes('gap-0'):
                ui.label('BIỂU ĐỒ DOANH THU 12 THÁNG').classes('text-sm font-bold text-gray-700 uppercase tracking-wider')
                ui.label(f'Dữ liệu tổng hợp từ các đơn hàng hoàn tất trong CSDL').classes('text-xs text-gray-400 font-medium')
            
            with ui.row().classes('items-center gap-2'):
                ui.label('Năm phân tích:').classes('text-xs font-semibold text-gray-600')
                year_select = ui.select(years, value=current_year_state['year']).classes('w-28 bg-gray-50').props('outlined dense')
                
                def on_year_change(e):
                    if year_select.value:
                        try:
                            current_year_state['year'] = int(year_select.value)
                            render_revenue_chart.refresh()
                        except (ValueError, TypeError):
                            pass

                year_select.on('update:model-value', on_year_change)
        
        @ui.refreshable
        def render_revenue_chart():
            sel_yr = current_year_state['year']
            rev_data = [0] * 12
            if container.report_service:
                try:
                    rev_data = container.report_service.get_revenue_by_year(sel_yr)
                except Exception:
                    pass
            
            echart = ui.echart({
                'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c} ₫'},
                'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
                'xAxis': {
                    'type': 'category',
                    'boundaryGap': False,
                    'data': [f'Tháng {i}' for i in range(1, 13)]
                },
                'yAxis': {'type': 'value'},
                'series': [{
                    'name': 'Doanh thu',
                    'type': 'line',
                    'smooth': True,
                    'areaStyle': {'color': 'rgba(0, 113, 227, 0.1)'},
                    'lineStyle': {'color': '#0071e3', 'width': 3},
                    'itemStyle': {'color': '#0071e3'},
                    'data': [float(r) for r in rev_data]
                }],
            })
            echart.classes('w-full h-72')

        render_revenue_chart()

    # Two columns: Top selling + Low stock
    with ui.row().classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-6'):
        # Top selling
        with ui.card().classes('p-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
            ui.label('TOP SẢN PHẨM BÁN CHẠY').classes('text-xs font-bold text-gray-400 uppercase tracking-wider mb-4')
            if top_selling:
                for item in top_selling:
                    name = item[0]
                    qty = item[1]
                    with ui.row().classes('w-full justify-between items-center py-2.5 border-b border-gray-50 last:border-0'):
                        ui.label(name).classes('text-sm font-semibold text-[#1d1d1f] line-clamp-1 max-w-[280px]')
                        ui.label(f'{qty} đã bán').classes('text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full')
            else:
                ui.label('Chưa có dữ liệu đơn hàng hoàn thành').classes('text-sm text-gray-400 italic py-4')

        # Low stock
        with ui.card().classes('p-6 rounded-2xl shadow-sm border border-gray-100 bg-white'):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.label('CẢNH BÁO TỒN KHO THẤP (≤ 5)').classes('text-xs font-bold text-rose-500 uppercase tracking-wider')
                ui.label(f'{len(low_stock_products)} sản phẩm').classes('text-xs font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full')
            
            if low_stock_products:
                for p in low_stock_products[:5]:
                    name = p[2]
                    stk = p[7]
                    pid = p[0]
                    with ui.row().classes('w-full justify-between items-center py-2.5 border-b border-gray-50 last:border-0'):
                        ui.link(name, f'/admin/product/{pid}').classes('text-sm font-semibold text-[#1d1d1f] hover:text-blue-600 line-clamp-1 max-w-[280px] no-underline')
                        ui.label(f'Còn {stk}').classes('text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full')
            else:
                ui.label('Tất cả sản phẩm đều đủ tồn kho').classes('text-sm text-gray-400 italic py-4')
