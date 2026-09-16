# database/customer_dao.py
class CustomerDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_customers(self, limit=50, offset=0):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM customers ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def count_customers(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM customers")
                return cursor.fetchone()[0]
            finally:
                cursor.close()
        return 0

    def get_customer_by_phone(self, phone):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
                return cursor.fetchone()
            finally:
                cursor.close()
        return None

    def add_customer(self, name, phone, email, address):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO customers (full_name, phone, email, address) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, phone, email, address))
                conn.commit()
                return True, "Thêm thành công"
            except Exception as e:
                conn.rollback()
                return False, str(e) # Thường lỗi trùng SĐT
            finally:
                cursor.close()
        return False, "Lỗi kết nối"