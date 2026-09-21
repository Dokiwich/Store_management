# database/report_dao.py
class ReportDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_summary_stats(self):
        """Lấy 4 chỉ số tổng quan: Doanh thu, Đơn hàng, Khách hàng, Tồn kho thấp"""
        conn = self.db_manager.get_connection()
        stats = {"revenue": 0, "orders": 0, "customers": 0, "low_stock": 0}
        
        if conn:
            cursor = conn.cursor()
            try:
                # 1. Tổng doanh thu
                cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status = 'Completed'")
                res = cursor.fetchone()
                stats["revenue"] = res[0] if res[0] else 0

                # 2. Tổng đơn hàng
                cursor.execute("SELECT COUNT(*) FROM orders")
                stats["orders"] = cursor.fetchone()[0]

                # 3. Tổng khách hàng
                cursor.execute("SELECT COUNT(*) FROM customers")
                stats["customers"] = cursor.fetchone()[0]

                # 4. Sản phẩm sắp hết hàng (< 5 cái)
                cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity < 5 AND is_active = 1")
                stats["low_stock"] = cursor.fetchone()[0]
            finally:
                cursor.close()
                if conn: conn.close()
        return stats

    def get_top_selling_products(self, limit=5, offset=0):
        """Lấy top sản phẩm bán chạy nhất"""
        conn = self.db_manager.get_connection()
        data = []
        if conn:
            cursor = conn.cursor()
            try:
                query = """
                    SELECT p.name, SUM(od.quantity) as total_qty
                    FROM order_details od
                    JOIN products p ON od.product_id = p.id
                    JOIN orders o ON od.order_id = o.id
                    WHERE o.status = 'Completed'
                    GROUP BY p.id, p.name
                    ORDER BY total_qty DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (int(limit), int(offset)))
                data = cursor.fetchall() # Trả về list các tuple [(Name, Qty), ...]
            finally:
                cursor.close()
                if conn: conn.close()
        return data

    def get_available_years(self):
        """Lấy danh sách các năm có hóa đơn"""
        conn = self.db_manager.get_connection()
        years = []
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT DISTINCT YEAR(created_at) FROM orders ORDER BY YEAR(created_at) DESC")
                res = cursor.fetchall()
                years = [str(r[0]) for r in res if r[0]]
            finally:
                cursor.close()
                if conn: conn.close()
        return years

    def get_revenue_by_year(self, year):
        """Lấy doanh thu 12 tháng của một năm"""
        conn = self.db_manager.get_connection()
        data = [0] * 12
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT MONTH(created_at), SUM(total_amount) 
                    FROM orders 
                    WHERE YEAR(created_at) = %s AND status = 'Completed'
                    GROUP BY MONTH(created_at)
                """, (year,))
                for row in cursor.fetchall():
                    month = row[0]
                    total = row[1]
                    if month and 1 <= month <= 12:
                        data[month - 1] = total
            finally:
                cursor.close()
                if conn: conn.close()
        return data

    def get_category_share(self):
        """Lấy tỷ trọng sản phẩm bán ra theo danh mục"""
        conn = self.db_manager.get_connection()
        data = []
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT c.name, SUM(od.quantity) 
                    FROM order_details od
                    JOIN products p ON od.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    JOIN orders o ON od.order_id = o.id
                    WHERE o.status = 'Completed'
                    GROUP BY c.name
                """)
                data = cursor.fetchall()
            finally:
                cursor.close()
                if conn: conn.close()
        return data