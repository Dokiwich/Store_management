class ServiceContainer:
    """
    Dependency Injection Container (Service Locator Pattern)
    Lưu trữ toàn bộ các class logic, dao, utility của hệ thống để tránh tình trạng Long Parameter List.
    """
    def __init__(self):
        self.db_manager = None
        self.product_service = None
        self.order_service = None
        self.report_service = None
        self.customer_service = None
        self.warranty_service = None
        self.user_service = None
        self.promotion_service = None
        self.history_service = None
        self.supplier_service = None
        self.exporter = None
