"""Web entry point — NiceGUI server for Laptop Store."""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui, app

# ── Database & Service bootstrap (same as main.py) ──
from database.db_manager import DatabaseManager
from database.product_dao import ProductDAO
from database.order_dao import OrderDAO
from database.report_dao import ReportDAO
from database.customer_dao import CustomerDAO
from database.user_dao import UserDAO
from database.warranty_dao import WarrantyDAO
from database.promotion_dao import PromotionDAO
from database.history_dao import HistoryDAO
from database.supplier_dao import SupplierDAO
from database.settings_dao import SettingsDAO

from logic.product_service import ProductService
from logic.order_service import OrderService
from logic.report_service import ReportService
from logic.customer_service import CustomerService
from logic.user_service import UserService
from logic.warranty_service import WarrantyService
from logic.promotion_service import PromotionService
from logic.history_service import HistoryService
from logic.supplier_service import SupplierService
from logic.settings_service import SettingsService
from logic.exporter import Exporter
from logic.service_container import ServiceContainer

# Init DB
db_manager = DatabaseManager()
test_conn = db_manager.get_connection()
if not test_conn:
    print("❌ Lỗi kết nối CSDL. Kiểm tra file .env")
    sys.exit(1)
test_conn.close()
print("✅ Kết nối CSDL thành công")

# DAOs
product_dao = ProductDAO(db_manager)
order_dao = OrderDAO(db_manager)
report_dao = ReportDAO(db_manager)
customer_dao = CustomerDAO(db_manager)
user_dao = UserDAO(db_manager)
warranty_dao = WarrantyDAO(db_manager)
promotion_dao = PromotionDAO(db_manager)
history_dao = HistoryDAO(db_manager)
supplier_dao = SupplierDAO(db_manager)
settings_dao = SettingsDAO(db_manager)

# Service Container (DI)
container = ServiceContainer()
container.db_manager = db_manager
container.exporter = Exporter()

# Gán DAOs vào container
container.product_dao = product_dao
container.order_dao = order_dao
container.report_dao = report_dao
container.customer_dao = customer_dao
container.user_dao = user_dao
container.warranty_dao = warranty_dao
container.promotion_dao = promotion_dao
container.history_dao = history_dao
container.supplier_dao = supplier_dao
container.settings_dao = settings_dao

# Gán Services vào container
container.product_service = ProductService(product_dao)
container.promotion_service = PromotionService(promotion_dao)
container.order_service = OrderService(order_dao, container.promotion_service, container.product_service)
container.report_service = ReportService(report_dao)
container.customer_service = CustomerService(customer_dao)
container.warranty_service = WarrantyService(warranty_dao)
container.user_service = UserService(user_dao)
container.history_service = HistoryService(history_dao)
container.supplier_service = SupplierService(supplier_dao)
container.settings_service = SettingsService(settings_dao)
ServiceContainer.set_instance(container)

# ── Static files ──
base_dir = os.path.dirname(os.path.abspath(__file__))
app.add_static_files('/static/assets', os.path.join(base_dir, 'assets'))
app.add_static_files('/static/resources', os.path.join(base_dir, 'resources'))

# ── Pages ──
from gui.web.login_page import build_login_page
from gui.web.admin.layout import admin_layout
from fastapi.responses import RedirectResponse
import gui.web.admin # Registers all @ui.page from admin package
import gui.web.services_page # Registers /services page

# Register store pages
import gui.web.store.home
import gui.web.store.orders
import gui.web.store.warranty
import gui.web.store.profile

@ui.page('/login')
def login_page():
    # Already logged in? Go to home
    if app.storage.user.get('authenticated'):
        return RedirectResponse('/')
    build_login_page(container)

@ui.page('/shop')
def shop_page_redirect():
    if not app.storage.user.get('authenticated'):
        return RedirectResponse('/login')
    return RedirectResponse('/')

@ui.page('/admin/dashboard')
def admin_dashboard_redirect():
    return RedirectResponse('/admin')

# ── Start server ──
# Server configured for enterprise Laptop Store
ui.run(
    title='Laptop Store',
    port=8080,
    storage_secret='laptop-store-secret-2024',
    dark=False,
    reload=True,
)

