class ProductDAO:
    ALLOWED_COLUMNS = {'category', 'brand', 'supplier_id'}

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_products(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Dùng SELECT * để lấy đủ cột (tránh lỗi index ở POS/Home)
                query = "SELECT * FROM products WHERE is_active = 1 ORDER BY id DESC"
                cursor.execute(query)
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def get_product_by_id(self, p_id):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM products WHERE id = %s"
                cursor.execute(query, (p_id,))
                return cursor.fetchone()
            finally:
                cursor.close()
        return None

    # [QUAN TRỌNG] Đã thêm tham số supplier_id vào đây
    def add_product(self, name, category, brand, supplier_id, import_price, price, stock, 
                    cpu, ram, screen, hard_drive, gpu, weight, os_sys, description):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Câu lệnh SQL đã thêm cột supplier_id
                query_prod = """
                    INSERT INTO products 
                    (name, category, brand, supplier_id, import_price, price, stock_quantity, 
                     spec_cpu, spec_ram, spec_screen, spec_hard_drive, spec_gpu, spec_weight, spec_os, 
                     description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query_prod, (name, category, brand, supplier_id, import_price, price, stock, 
                                            cpu, ram, screen, hard_drive, gpu, weight, os_sys, description))
                product_id = cursor.lastrowid
                
                # Ghi log nhập hàng
                if stock > 0:
                    total_cost = stock * import_price
                    query_log = "INSERT INTO import_logs (product_id, product_name, quantity, import_price, total_cost) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(query_log, (product_id, name, stock, import_price, total_cost))

                conn.commit()
                return True
            except Exception as e:
                print(f"Lỗi: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
        return False

    def delete_product(self, p_id):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE products SET is_active = 0 WHERE id = %s", (p_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Lỗi: {e}")
                return False
            finally:
                cursor.close()
        return False

    def search_products(self, keyword, category_filter=None):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT * FROM products WHERE is_active = 1"
                params = []

                if keyword:
                    sql += " AND (name LIKE %s OR brand LIKE %s)"
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                if category_filter and category_filter != "Tất cả":
                    sql += " AND category = %s"
                    params.append(category_filter)
                
                sql += " ORDER BY id DESC"
                
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []
    
    # Hỗ trợ bộ lọc (dùng chung logic search cho gọn)
    def filter_products(self, category=None, brand=None, price_range=None, keyword=None):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT * FROM products WHERE is_active = 1"
                params = []

                if category and category != "Tất cả":
                    sql += " AND category = %s"
                    params.append(category)
                if brand and brand != "Tất cả":
                    sql += " AND brand = %s"
                    params.append(brand)
                if keyword:
                    sql += " AND name LIKE %s"
                    params.append(f"%{keyword}%")
                
                # Logic lọc giá
                if price_range and price_range != "Tất cả":
                    if price_range == "< 10 Triệu": sql += " AND price < 10000000"
                    elif price_range == "10 - 20 Triệu": sql += " AND price BETWEEN 10000000 AND 20000000"
                    elif price_range == "20 - 30 Triệu": sql += " AND price BETWEEN 20000000 AND 30000000"
                    elif price_range == "> 30 Triệu": sql += " AND price > 30000000"

                sql += " ORDER BY id DESC"
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    # --- HÀM GỢI Ý AI ---
    def get_similar_products(self, current_id, category, price):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Logic AI: Tìm sản phẩm cùng loại HOẶC giá chênh lệch không quá 20%
                min_p = price * 0.8
                max_p = price * 1.2
                sql = """
                    SELECT * FROM products 
                    WHERE is_active=1 AND id != %s 
                    AND (category=%s OR price BETWEEN %s AND %s) 
                    ORDER BY id DESC LIMIT 3
                """
                cursor.execute(sql, (current_id, category, min_p, max_p))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def get_all_categories(self): return self._get_distinct("category")
    def get_all_brands(self): return self._get_distinct("brand")
    
    def _get_distinct(self, col):
        if col not in self.ALLOWED_COLUMNS:
            return []
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT DISTINCT {col} FROM products WHERE {col} IS NOT NULL ORDER BY {col}")
                return [row[0] for row in cursor.fetchall()]
            except Exception as e:
                print(f"Lỗi: {e}")
                return []
            finally:
                cursor.close()
        return []