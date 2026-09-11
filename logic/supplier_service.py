class SupplierService:
    def __init__(self, supplier_dao):
        self.dao = supplier_dao

    def get_all_suppliers(self, limit=50, offset=0):
        return self.dao.get_all_suppliers(limit, offset)
