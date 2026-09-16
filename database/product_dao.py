class ProductDAO:
    BASE_SELECT = """
        SELECT p.id, p.supplier_id, p.name, c.name, b.name, 
               p.import_price, p.price, p.stock_quantity, 
               p.spec_cpu, p.spec_ram, p.spec_screen, p.spec_hard_drive, 
               p.spec_gpu, p.spec_weight, p.spec_os, p.description, p.is_active 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        LEFT JOIN brands b ON p.brand_id = b.id 
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_products(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = self.BASE_SELECT + " WHERE p.is_active = 1 ORDER BY p.id DESC"
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
                query = self.BASE_SELECT + " WHERE p.id = %s"
                cursor.execute(query, (p_id,))
                return cursor.fetchone()
            finally:
                cursor.close()
        return None

    def _get_or_create_category(self, cursor, name):
        cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
        res = cursor.fetchone()
        if res: return res[0]
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        return cursor.lastrowid

    def _get_or_create_brand(self, cursor, name):
        cursor.execute("SELECT id FROM brands WHERE name = %s", (name,))
        res = cursor.fetchone()
        if res: return res[0]
        cursor.execute("INSERT INTO brands (name) VALUES (%s)", (name,))
        return cursor.lastrowid

    def add_product(self, name, category, brand, supplier_id, import_price, price, stock, 
                    cpu, ram, screen, hard_drive, gpu, weight, os_sys, description):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cat_id = self._get_or_create_category(cursor, category)
                brand_id = self._get_or_create_brand(cursor, brand)

                query_prod = """
                    INSERT INTO products 
                    (name, category_id, brand_id, supplier_id, import_price, price, stock_quantity, 
                     spec_cpu, spec_ram, spec_screen, spec_hard_drive, spec_gpu, spec_weight, spec_os, 
                     description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query_prod, (name, cat_id, brand_id, supplier_id, import_price, price, stock, 
                                            cpu, ram, screen, hard_drive, gpu, weight, os_sys, description))
                product_id = cursor.lastrowid
                
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
                sql = self.BASE_SELECT + " WHERE p.is_active = 1"
                params = []

                if keyword:
                    sql += " AND (p.name LIKE %s OR b.name LIKE %s)"
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                if category_filter and category_filter != "Tất cả":
                    sql += " AND c.name = %s"
                    params.append(category_filter)
                
                sql += " ORDER BY p.id DESC"
                
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []
    
    def filter_products(self, category=None, brand=None, price_range=None, keyword=None):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = self.BASE_SELECT + " WHERE p.is_active = 1"
                params = []

                if category and category != "Tất cả":
                    sql += " AND c.name = %s"
                    params.append(category)
                if brand and brand != "Tất cả":
                    sql += " AND b.name = %s"
                    params.append(brand)
                if keyword:
                    sql += " AND p.name LIKE %s"
                    params.append(f"%{keyword}%")
                
                if price_range and price_range != "Tất cả":
                    if price_range == "< 10 Triệu": sql += " AND p.price < 10000000"
                    elif price_range == "10 - 20 Triệu": sql += " AND p.price BETWEEN 10000000 AND 20000000"
                    elif price_range == "20 - 30 Triệu": sql += " AND p.price BETWEEN 20000000 AND 30000000"
                    elif price_range == "> 30 Triệu": sql += " AND p.price > 30000000"

                sql += " ORDER BY p.id DESC"
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def get_similar_products(self, current_id, category, price):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                min_p = price * 0.8
                max_p = price * 1.2
                sql = self.BASE_SELECT + """
                    WHERE p.is_active=1 AND p.id != %s 
                    AND (c.name=%s OR p.price BETWEEN %s AND %s) 
                    ORDER BY p.id DESC LIMIT 3
                """
                cursor.execute(sql, (current_id, category, min_p, max_p))
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    def get_all_categories(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT name FROM categories ORDER BY name")
                return [row[0] for row in cursor.fetchall()]
            except: pass
            finally: cursor.close()
        return []

    def get_all_brands(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT name FROM brands ORDER BY name")
                return [row[0] for row in cursor.fetchall()]
            except: pass
            finally: cursor.close()
        return []