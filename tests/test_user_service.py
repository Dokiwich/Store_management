import unittest
from unittest.mock import MagicMock
from logic.user_service import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        # Tạo Mock DAO để cô lập hoàn toàn tầng DAO
        self.mock_dao = MagicMock()
        self.service = UserService(self.mock_dao)

    def test_add_user_password_too_short(self):
        # Kiểm thử biên: Mật khẩu < 6 ký tự
        success, msg = self.service.add_user("testuser", "12345", "Test User", "admin")
        self.assertFalse(success)
        self.assertEqual(msg, "Mật khẩu phải có ít nhất 6 ký tự")
        # Đảm bảo hàm DAO không được gọi
        self.mock_dao.add_user.assert_not_called()

    def test_add_user_invalid_role(self):
        # Kiểm thử biên: Role không hợp lệ
        success, msg = self.service.add_user("testuser", "123456", "Test User", "superadmin")
        self.assertFalse(success)
        self.assertTrue(msg.startswith("Vai trò không hợp lệ"))
        self.mock_dao.add_user.assert_not_called()

    def test_add_user_success(self):
        # Trọng tâm: Kiểm tra DAO được gọi đúng tham số khi hợp lệ
        self.mock_dao.add_user.return_value = (True, "Thêm thành công")
        
        success, msg = self.service.add_user("testuser", "123456", "Test User", "admin")
        
        self.assertTrue(success)
        self.assertEqual(msg, "Thêm thành công")
        self.mock_dao.add_user.assert_called_once_with("testuser", "123456", "Test User", "admin")
