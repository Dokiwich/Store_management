import mysql.connector

class OrderDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_order(self, user_id, voucher_code, total_amount, cart_items, customer_id=None):
        # 1. Kiểm tra kết nối
        conn = self.db_manager.get_connection()
        if not conn:
            return False, "Mất kết nối CSDL"

        # 2. Xử lý transaction cũ bị treo (nếu có)
        try:
            if conn.in_transaction:
                conn.rollback()
        except Exception as e:
            print(f"Lỗi rollback transaction cũ: {e}")

        cursor = conn.cursor()
        try:
            # 3. Bắt đầu giao dịch mới
            conn.start_transaction()

            # --- BƯỚC A: TẠO HÓA ĐƠN (Bảng orders) ---
            # Đã thêm cột voucher_code và status
            sql_order = """
                INSERT INTO orders (user_id, customer_id, voucher_code, total_amount, status, created_at)
                VALUES (%s, %s, %s, %s, 'Completed', NOW())
            """
            val_order = (user_id, customer_id, voucher_code, total_amount)
            cursor.execute(sql_order, val_order)
            order_id = cursor.lastrowid # Lấy ID đơn hàng vừa tạo

            # --- BƯỚC B: LƯU CHI TIẾT & TRỪ KHO ---
            # Quan trọng: Đã sửa 'price' thành 'price_at_sale' để hết lỗi 1054
            sql_detail = """
                INSERT INTO order_details (order_id, product_id, quantity, price_at_sale)
                VALUES (%s, %s, %s, %s)
            """

            for item in cart_items:
                p_id = item['id']
                qty = item['qty']

                # Trừ số lượng tồn kho
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s AND stock_quantity >= %s",
                    (qty, p_id, qty)
                )
                if cursor.rowcount == 0:
                    conn.rollback()
                    return False, f"Sản phẩm ID {p_id} hết hàng hoặc không đủ số lượng"

                # Verify price from DB
                cursor.execute("SELECT price FROM products WHERE id = %s", (p_id,))
                db_price_row = cursor.fetchone()
                if db_price_row:
                    verified_price = db_price_row[0]
                else:
                    conn.rollback()
                    return False, f"Không tìm thấy sản phẩm ID {p_id}"

                # Lưu chi tiết đơn hàng
                cursor.execute(sql_detail, (order_id, p_id, qty, verified_price))

            # 4. Lưu tất cả thay đổi (Commit)
            conn.commit()
            return True, f"Thanh toán thành công! Mã đơn: {order_id}"

        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Transaction failed: {err}")
            return False, f"Lỗi giao dịch: {err}"
        except Exception as e:
            conn.rollback()
            print(f"General Error: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            cursor.close()