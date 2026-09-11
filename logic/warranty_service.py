class WarrantyService:
    def __init__(self, warranty_dao):
        self.dao = warranty_dao

    def search_warranty(self, keyword):
        keyword = keyword.strip() if keyword else ''
        if len(keyword) < 3:
            return []  # Tối thiểu 3 ký tự để tìm kiếm
        return self.dao.search_warranty(keyword)
