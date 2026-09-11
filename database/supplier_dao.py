class SupplierDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_suppliers(self, limit=50, offset=0):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, name, phone, email, address, is_active FROM suppliers WHERE is_active = 1 LIMIT %s OFFSET %s", (limit, offset))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []