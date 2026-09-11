import tkinter as tk
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

from logic.product_service import ProductService
from logic.order_service import OrderService
from logic.report_service import ReportService
from logic.customer_service import CustomerService
from logic.user_service import UserService
from logic.warranty_service import WarrantyService
from logic.promotion_service import PromotionService
from logic.history_service import HistoryService
from logic.supplier_service import SupplierService

from logic.exporter import Exporter
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    # 1. Kết nối CSDL
    db_manager = DatabaseManager()
    if not db_manager.get_connection():
        print("Lỗi kết nối CSDL")
        return

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
    
    # 3. Khởi tạo toàn bộ Service (Business Logic)
    product_service = ProductService(product_dao)
    order_service = OrderService(order_dao)
    report_service = ReportService(report_dao)
    customer_service = CustomerService(customer_dao)
    warranty_service = WarrantyService(warranty_dao)
    user_service = UserService(user_dao)
    promotion_service = PromotionService(promotion_dao)
    history_service = HistoryService(history_dao)
    supplier_service = SupplierService(supplier_dao)
    
    exporter = Exporter(db_manager)

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

            login_app = LoginWindow(user_service, on_login_success)
            login_app.mainloop()
            
            # Nếu tắt login mà chưa đăng nhập -> Thoát luôn
            if app_state["action"] == "login":
                break

        elif app_state["action"] == "main":
            # --- MÀN HÌNH CHÍNH ---
            def on_logout():
                app_state["user"] = None
                app_state["action"] = "login" # Quay lại đăng nhập

            app = MainWindow(db_manager, product_service, order_service, report_service, 
                             customer_service, warranty_service, exporter, promotion_service, 
                             history_service, user_service, supplier_service, app_state["user"], 
                             on_logout) # Truyền callback logout
            
            app.mainloop()

            # Nếu tắt main window bằng dấu X -> Thoát vòng lặp
            if app_state["action"] == "main":
                break
        
        elif app_state["action"] == "exit":
            break

    db_manager.close_connection()

if __name__ == "__main__":
    main()