from logic.models import Cart

class OrderService:
    def __init__(self, dao, promotion_service, product_service):
        self.dao = dao
        self.promotion_service = promotion_service
        self.product_service = product_service
        # Khởi tạo một đối tượng giỏ hàng cho session hiện tại
        self.cart = Cart()

    def get_cart(self):
        return self.cart

    def add_to_cart(self, product_id, qty=1):
        """Logic thêm sản phẩm vào giỏ hàng, bao gồm kiểm tra tồn kho."""
        product = self.product_service.get_product_by_id(product_id)
        if not product:
            return False, f"Không tìm thấy sản phẩm ID {product_id}"

        p_name = product[2]
        p_price = float(product[6])
        p_stock = int(product[7])

        if p_stock <= 0:
            return False, f"Sản phẩm {p_name} tạm hết hàng!"

        try:
            self.cart.add_item(product_id, p_name, p_price, qty, p_stock)
            return True, "Thêm thành công"
        except ValueError as e:
            return False, str(e)

    def remove_from_cart(self, product_id):
        self.cart.remove_item(product_id)

    def clear_cart(self):
        self.cart.clear()

    def apply_voucher(self, voucher_code):
        """Logic kiểm tra và áp dụng voucher."""
        code = voucher_code.strip().upper()
        if not code:
            return False, "Voucher không được rỗng"
        
        cart_total = self.cart.cart_total
        if cart_total == 0:
            return False, "Giỏ hàng trống"
            
        is_valid, result = self.promotion_service.check_promotion(code, cart_total)
        if is_valid:
            self.cart.apply_discount(code, result)
            return True, result
        else:
            self.cart.apply_discount(None, 0)
            return False, result

    def checkout(self, user_id, customer_id=None):
        """Thực hiện thanh toán."""
        if not self.cart.items:
            return False, "Giỏ hàng trống"
            
        cart_items_dict = self.cart.get_items_as_dict_list()
        total_amount = self.cart.final_total
        voucher_code = self.cart.voucher_code if self.cart.voucher_code else ""

        # Gọi DAO để lưu order
        success, msg = self.dao.create_order(user_id, customer_id, cart_items_dict, total_amount, voucher_code)
        if success:
            self.clear_cart()
            
        return success, msg

    def create_order(self, user_id, voucher_code, total_amount, cart_items, customer_id=None):
        """Pass-through function cho home_tab.py tự quản lý giỏ hàng."""
        return self.dao.create_order(user_id, voucher_code, total_amount, cart_items, customer_id)
