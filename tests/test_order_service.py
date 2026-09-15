import unittest
from unittest.mock import MagicMock
from logic.order_service import OrderService

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.mock_dao = MagicMock()
        self.mock_promotion = MagicMock()
        self.mock_product = MagicMock()
        self.service = OrderService(self.mock_dao, self.mock_promotion, self.mock_product)

    def test_add_to_cart_not_found(self):
        self.mock_product.get_product_by_id.return_value = None
        success, msg = self.service.add_to_cart(999, 1)
        self.assertFalse(success)
        self.assertTrue("Không tìm thấy" in msg)

    def test_add_to_cart_out_of_stock(self):
        # Tuple product giả: p[2]=name, p[6]=price, p[7]=stock
        self.mock_product.get_product_by_id.return_value = (1, 'Cat', 'Laptop A', 'Brand', 1, 1000, 2000, 0, 'CPU', 'RAM')
        success, msg = self.service.add_to_cart(1, 1)
        self.assertFalse(success)
        self.assertTrue("hết hàng" in msg)

    def test_add_to_cart_exceeds_stock(self):
        # Stock = 5
        self.mock_product.get_product_by_id.return_value = (1, 'Cat', 'Laptop A', 'Brand', 1, 1000, 2000, 5, 'CPU', 'RAM')
        
        # Lần 1 mua 3 cái -> OK
        success, msg = self.service.add_to_cart(1, 3)
        self.assertTrue(success)
        
        # Lần 2 mua thêm 3 cái -> Vượt tồn kho (3+3 > 5)
        success, msg = self.service.add_to_cart(1, 3)
        self.assertFalse(success)
        self.assertTrue("Đã đạt giới hạn tồn kho" in msg)

    def test_cart_total_and_apply_voucher(self):
        self.mock_product.get_product_by_id.return_value = (1, 'Cat', 'Laptop A', 'Brand', 1, 1000, 2000, 10, 'CPU', 'RAM')
        
        # Mua 2 cái, giá 2000 -> Tổng 4000
        self.service.add_to_cart(1, 2)
        cart = self.service.get_cart()
        self.assertEqual(cart.cart_total, 4000)
        self.assertEqual(cart.final_total, 4000)

        # Apply voucher thành công giảm 500
        self.mock_promotion.check_promotion.return_value = (True, 500)
        success, result = self.service.apply_voucher("DISCOUNT500")
        
        self.assertTrue(success)
        self.assertEqual(result, 500)
        self.assertEqual(cart.discount_amount, 500)
        self.assertEqual(cart.final_total, 3500)
