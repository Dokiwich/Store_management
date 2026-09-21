class WarrantyService:
    def __init__(self, warranty_dao):
        self.dao = warranty_dao

    def search_warranty(self, keyword='', limit=50):
        kw = keyword.strip() if keyword else ''
        if kw and len(kw) < 3:
            return []  # Nếu có nhập từ khóa thì tối thiểu 3 ký tự
        return self.dao.search_warranty(kw, limit=limit)
