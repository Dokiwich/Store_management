class ServiceContainer:
    """
    Dependency Injection Container (Service Locator Pattern)
    Lưu trữ toàn bộ các class logic, dao, utility của hệ thống để tránh tình trạng Long Parameter List.
    """
    _instance = None

    def __init__(self):
        self.db_manager = None
        self.product_dao = None
        self.order_dao = None
        self.report_dao = None
        self.customer_dao = None
        self.user_dao = None
        self.warranty_dao = None
        self.promotion_dao = None
        self.history_dao = None
        self.supplier_dao = None

        self.product_service = None
        self.order_service = None
        self.report_service = None
        self.customer_service = None
        self.warranty_service = None
        self.user_service = None
        self.promotion_service = None
        self.history_service = None
        self.supplier_service = None
        self.settings_dao = None
        self.settings_service = None
        self.exporter = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, instance):
        cls._instance = instance


def get_container() -> ServiceContainer:
    return ServiceContainer.get_instance()

