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

                # 1. Khóa dòng sản phẩm và lấy giá, tồn kho hiện tại (Pessimistic Locking)
                cursor.execute("SELECT price, stock_quantity FROM products WHERE id = %s FOR UPDATE", (p_id,))
                db_row = cursor.fetchone()
                
                if not db_row:
                    conn.rollback()
                    return False, f"Không tìm thấy sản phẩm ID {p_id}"
                
                verified_price = db_row[0]
                current_stock = db_row[1]
                
                # 2. Kiểm tra tồn kho
                if current_stock < qty:
                    conn.rollback()
                    return False, f"Sản phẩm ID {p_id} không đủ số lượng (Chỉ còn {current_stock})"

                # 3. Trừ số lượng tồn kho an toàn
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                    (qty, p_id)
                )

                # 4. Lưu chi tiết đơn hàng
                cursor.execute(sql_detail, (order_id, p_id, qty, verified_price))

            # 5. Tự động tích lũy điểm thưởng thành viên (FR-07: 100.000đ = 1 điểm)
            if customer_id:
                earned_points = int(float(total_amount or 0) / 100000)
                if earned_points > 0:
                    cursor.execute(
                        "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE id = %s",
                        (earned_points, customer_id)
                    )

            # 6. Lưu tất cả thay đổi (Commit)
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
            if conn: conn.close()