import os
import sys
import tkinter as tk

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối tới tài nguyên (hỗ trợ đóng gói PyInstaller --onefile)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    # 1. Kết nối CSDL
    db_manager = DatabaseManager()
    test_conn = db_manager.get_connection()
    if not test_conn:
        print("Lỗi kết nối CSDL")
        return
    test_conn.close()

    # 2. Khởi tạo toàn bộ DAO
    product_dao = ProductDAO(db_manager)
    order_dao = OrderDAO(db_manager)
    report_dao = ReportDAO(db_manager)
    customer_dao = CustomerDAO(db_manager)
    warranty_dao = WarrantyDAO(db_manager)
    user_dao = UserDAO(db_manager)
    promotion_dao = PromotionDAO(db_manager)
    history_dao = HistoryDAO(db_manager)
    supplier_dao = SupplierDAO(db_manager)
    settings_dao = SettingsDAO(db_manager)
    
    # 3. Đóng gói vào Service Container (Dependency Injection)
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

    # Khởi tạo Service và nhét vào Container
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

    # Đăng ký Singleton instance cho toàn hệ thống
    ServiceContainer.set_instance(container)

    # Biến trạng thái để kiểm soát vòng lặp ứng dụng
    app_state = {
        "user": None,   # Lưu user đang đăng nhập
        "action": "login" # 'login', 'main', 'exit'
    }

    while True:
        if app_state["action"] == "login":
            # --- MÀN HÌNH ĐĂNG NHẬP ---
            def on_login_success(user_info):
                app_state["user"] = user_info
                app_state["action"] = "main" # Chuyển sang màn hình chính

            login_app = LoginWindow(container.user_service, on_login_success)
            login_app.mainloop()
            
            # Nếu tắt login mà chưa đăng nhập -> Thoát luôn
            if app_state["action"] == "login":
                break

        elif app_state["action"] == "main":
            # --- MÀN HÌNH CHÍNH ---
            def on_logout():
                app_state["user"] = None
                app_state["action"] = "login" # Quay lại đăng nhập

            app = MainWindow(
                current_user=app_state["user"],
                on_logout=on_logout,
                
                service_container=container
            )
            app.mainloop()

            # Nếu tắt main window bằng dấu X -> Thoát vòng lặp
            if app_state["action"] == "main":
                break
        
        elif app_state["action"] == "exit":
            break

    db_manager.close_connection()

if __name__ == "__main__":
    main()