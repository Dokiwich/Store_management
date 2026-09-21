"""Admin web modules package — Clean 1-to-1 modular architecture matching gui/tabs/."""

from gui.web.admin.dashboard import dashboard_page
from gui.web.admin.inventory import inventory_page
from gui.web.admin.product_editor import product_editor_page
from gui.web.admin.warranty import warranty_page
from gui.web.admin.customers import customers_page
from gui.web.admin.employees import employees_page
from gui.web.admin.orders import orders_page
from gui.web.admin.settings import settings_page

__all__ = [
    'dashboard_page',
    'inventory_page',
    'product_editor_page',
    'warranty_page',
    'customers_page',
    'employees_page',
    'orders_page',
    'settings_page',
]
