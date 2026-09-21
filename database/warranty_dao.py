# database/warranty_dao.py
class WarrantyDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def search_warranty(self, keyword, limit=50):
        """Tìm theo SĐT khách hoặc mã đơn hàng"""
        conn = self.db_manager.get_connection()
        results = []
        if conn:
            cursor = conn.cursor()
            try:
                # Join các bảng để lấy tên khách, tên máy, ngày mua
                sql = """
                    SELECT 
                        o.id as order_id,
                        c.full_name,
                        c.phone,
                        p.name as product_name,
                        od.price_at_sale,
                        o.created_at,
                        p.warranty_time
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    JOIN order_details od ON o.id = od.order_id
                    JOIN products p ON od.product_id = p.id
                    WHERE (c.phone LIKE %s OR o.id LIKE %s)
                    ORDER BY o.created_at DESC LIMIT %s
                """
                # Tìm gần đúng (%)
                param = f"%{keyword}%"
                cursor.execute(sql, (param, param, limit))
                results = cursor.fetchall()
            finally:
                cursor.close()
                if conn: conn.close()
        return results