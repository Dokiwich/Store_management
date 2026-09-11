class ProductService:
    def __init__(self, product_dao):
        self.dao = product_dao

    def get_all_products(self):
        return self.dao.get_all_products()

    def get_product_by_id(self, p_id):
        return self.dao.get_product_by_id(p_id)

    def delete_product(self, p_id):
        return self.dao.delete_product(p_id)

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

    def get_distinct_values(self, col):
        """Lấy danh sách giá trị duy nhất cho cột hợp lệ."""
        return self.dao._get_distinct(col)

