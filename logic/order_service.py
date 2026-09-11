class OrderService:
    def __init__(self, dao):
        self.dao = dao

    def create_order(self, user_id, customer_id, cart_items, total_amount, voucher_code=None):
        if not cart_items:
            return False, "Giỏ hàng trống"
        for item in cart_items:
            if item.get('quantity', 0) <= 0:
                return False, f"Số lượng không hợp lệ cho sản phẩm {item.get('name', 'N/A')}"
        return self.dao.create_order(user_id, customer_id, cart_items, total_amount, voucher_code)
