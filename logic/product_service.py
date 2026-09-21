class ProductService:
    def __init__(self, product_dao):
        self.dao = product_dao

    def get_all_products(self):
        return self.dao.get_all_products()

    def get_product_by_id(self, p_id):
        return self.dao.get_product_by_id(p_id)

    def delete_product(self, p_id, current_user_role="admin"):
        """Xóa sản phẩm - có xác thực phân quyền 2 lớp (RBAC Service-level Enforcement)."""
        if current_user_role != "admin":
            return False
        return self.dao.delete_product(p_id)

    def add_product(self, name, category, brand, supplier_id, import_price, price, stock, 
                    cpu, ram, screen, hard_drive, gpu, weight, os_sys, description, *args, **kwargs):
        if not name or not str(name).strip():
            return False
        try:
            if float(price or 0) < 0 or int(stock or 0) < 0 or float(import_price or 0) < 0:
                return False
        except (ValueError, TypeError):
            return False
        return self.dao.add_product(name, category, brand, supplier_id, import_price, price, stock, 
                                    cpu, ram, screen, hard_drive, gpu, weight, os_sys, description, *args, **kwargs)

    def update_product(self, p_id, name, category, brand, supplier_id, import_price, price, stock, 
                       cpu, ram, screen, hard_drive, gpu, weight, os_sys, description, *args, **kwargs):
        if not name or not str(name).strip():
            return False
        try:
            if float(price or 0) < 0 or int(stock or 0) < 0 or float(import_price or 0) < 0:
                return False
        except (ValueError, TypeError):
            return False
        return self.dao.update_product(p_id, name, category, brand, supplier_id, import_price, price, stock, 
                                       cpu, ram, screen, hard_drive, gpu, weight, os_sys, description, *args, **kwargs)

    def search_products(self, keyword, category_filter=None):
        return self.dao.search_products(keyword, category_filter=category_filter)

    def filter_products(self, category=None, brand=None, price_range=None, keyword=None):
        return self.dao.filter_products(category=category, brand=brand, price_range=price_range, keyword=keyword)

    def get_similar_products(self, current_id, category, price):
        return self.dao.get_similar_products(current_id, category, price)

    def get_all_categories(self):
        return self.dao.get_all_categories()

    def get_all_brands(self):
        return self.dao.get_all_brands()

