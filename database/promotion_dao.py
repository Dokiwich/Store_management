from decimal import Decimal

class PromotionDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def check_promotion(self, code, total_bill):
        conn = self.db_manager.get_connection()
        if not conn:
            return False, "Lỗi kết nối CSDL"
        
        cursor = conn.cursor()
        try:
            # Lấy đúng 4 cột cần thiết. 
            # YÊU CẦU: Bảng promotions phải có đủ 4 cột này (đã thêm ở Bước 1)
            sql = "SELECT code, discount_value, discount_type, min_order_value FROM promotions WHERE code = %s AND is_active = 1"
            
            cursor.execute(sql, (code,))
            promo = cursor.fetchone()

            if not promo:
                return False, "Mã giảm giá không tồn tại hoặc đã hết hạn!"

            # Lấy dữ liệu từ kết quả query
            # promo[0] là code
            p_val = Decimal(promo[1])           # discount_value
            p_type = str(promo[2]).lower()    # discount_type ('percent' hoặc 'money')
            min_bill = Decimal(promo[3])        # min_bill_value (Vừa thêm cột này)

            total_bill_dec = Decimal(total_bill)

            # 1. Kiểm tra điều kiện đơn tối thiểu
            if total_bill_dec < min_bill:
                return False, f"Đơn hàng phải từ {min_bill:,.0f}đ mới được dùng mã này!"

            # 2. Tính toán số tiền giảm
            discount_amt = Decimal('0')
            if 'percent' in p_type: # Nếu là giảm theo phần trăm
                discount_amt = total_bill_dec * (p_val / Decimal('100'))
                # Giới hạn giảm tối đa 1 triệu (Hardcode rule)
                if discount_amt > Decimal('1000000'): 
                    discount_amt = Decimal('1000000')
            else: # Nếu là giảm số tiền cố định (money)
                discount_amt = p_val
            
            # Đảm bảo mức giảm giá không bao giờ vượt quá tổng tiền hóa đơn
            discount_amt = min(discount_amt, total_bill_dec)
            return True, float(discount_amt)

        except Exception as e:
            # Trả về thông báo lỗi chung chung cho user
            return False, f"Lỗi kiểm tra mã: {str(e)}"
        finally:
            cursor.close()
            if conn: conn.close()

    def get_active_promotions(self, limit=50, offset=0):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Chỉ lấy các mã đang kích hoạt
                cursor.execute("SELECT code, discount_value, discount_type FROM promotions WHERE is_active = 1 LIMIT %s OFFSET %s", (limit, offset))
                return cursor.fetchall()
            except Exception as e: 
                return []
            finally:
                cursor.close()
                if conn: conn.close()
        return []