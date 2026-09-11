# database/history_dao.py

class HistoryDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_sales_history(self, user_id=None, limit=50, offset=0):
        """Lấy danh sách đơn hàng đã bán, lọc theo user_id nếu có"""
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = """
                    SELECT o.id, u.full_name, c.full_name, o.total_amount, o.created_at 
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    LEFT JOIN customers c ON o.customer_id = c.id
                """
                params = []
                if user_id is not None:
                    sql += " WHERE o.user_id = %s"
                    params.append(user_id)
                
                sql += " ORDER BY o.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def count_sales_history(self, user_id=None):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT COUNT(*) FROM orders o"
                params = []
                if user_id is not None:
                    sql += " WHERE o.user_id = %s"
                    params.append(user_id)
                cursor.execute(sql, tuple(params))
                return cursor.fetchone()[0]
            finally:
                cursor.close()
        return 0

    def get_import_history(self, limit=50, offset=0):
        """Lấy danh sách lịch sử nhập hàng"""
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = """
                    SELECT id, product_name, quantity, import_price, total_cost, created_at 
                    FROM import_logs 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (limit, offset))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def count_import_history(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT COUNT(*) FROM import_logs"
                cursor.execute(sql)
                return cursor.fetchone()[0]
            finally:
                cursor.close()
        return 0