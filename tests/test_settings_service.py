import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic.settings_service import SettingsService

class TestSettingsService(unittest.TestCase):
    def setUp(self):
        self.mock_dao = MagicMock()
        self.service = SettingsService(self.mock_dao)

    def test_get_all(self):
        self.mock_dao.get_all_settings.return_value = {"store_name": "Pro Laptop", "loyalty_rate": "0.01"}
        res = self.service.get_all()
        self.assertEqual(res["store_name"], "Pro Laptop")
        self.mock_dao.get_all_settings.assert_called_once()

    def test_get_with_default(self):
        self.mock_dao.get_setting.return_value = "default_val"
        val = self.service.get("unknown_key", "default_val")
        self.assertEqual(val, "default_val")
        self.mock_dao.get_setting.assert_called_once_with("unknown_key", "default_val")

    def test_set_setting(self):
        self.mock_dao.update_setting.return_value = True
        ok = self.service.set("store_name", "New Store")
        self.assertTrue(ok)
        self.mock_dao.update_setting.assert_called_once_with("store_name", "New Store")

    def test_update_multiple_settings(self):
        self.mock_dao.update_multiple_settings.return_value = True
        payload = {"store_name": "New Store", "low_stock_threshold": "10"}
        ok = self.service.update_settings(payload)
        self.assertTrue(ok)
        self.mock_dao.update_multiple_settings.assert_called_once_with(payload)

if __name__ == '__main__':
    unittest.main()
