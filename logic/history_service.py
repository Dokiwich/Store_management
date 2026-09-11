class HistoryService:
    def __init__(self, history_dao):
        self.dao = history_dao

    def get_sales_history(self, user_id=None, limit=50, offset=0):
        return self.dao.get_sales_history(user_id, limit, offset)

    def get_import_history(self, limit=50, offset=0):
        return self.dao.get_import_history(limit, offset)
