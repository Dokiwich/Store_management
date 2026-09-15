class CartItem:
    def __init__(self, product_id, name, price, qty, max_stock):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.qty = int(qty)
        self.max_stock = int(max_stock)

    @property
    def total(self):
        return self.price * self.qty

    def to_dict(self):
        """Dùng để tương thích ngược với format cũ của hệ thống."""
        return {
            'id': self.product_id,
            'name': self.name,
            'price': self.price,
            'qty': self.qty,
            'total': self.total
        }

class Cart:
    def __init__(self):
        self.items = {}  # product_id -> CartItem
        self.voucher_code = None
        self.discount_amount = 0

    def add_item(self, product_id, name, price, qty, max_stock):
        if qty <= 0:
            raise ValueError("Số lượng phải lớn hơn 0.")
        
        if product_id in self.items:
            new_qty = self.items[product_id].qty + qty
        else:
            new_qty = qty
            
        if new_qty > max_stock:
            raise ValueError(f"Đã đạt giới hạn tồn kho ({max_stock}) cho sản phẩm này.")
            
        if product_id in self.items:
            self.items[product_id].qty = new_qty
        else:
            self.items[product_id] = CartItem(product_id, name, price, new_qty, max_stock)

    def remove_item(self, product_id):
        if product_id in self.items:
            del self.items[product_id]
            
    def clear(self):
        self.items.clear()
        self.voucher_code = None
        self.discount_amount = 0

    @property
    def cart_total(self):
        return sum(item.total for item in self.items.values())

    @property
    def final_total(self):
        return max(0, self.cart_total - self.discount_amount)

    def apply_discount(self, voucher_code, discount_amount):
        self.voucher_code = voucher_code
        self.discount_amount = discount_amount

    def get_items_as_dict_list(self):
        """Trả về danh sách dictionary tương thích với DAO cũ."""
        return [item.to_dict() for item in self.items.values()]
