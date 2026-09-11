import re

class CustomerService:
    def __init__(self, dao):
        self.dao = dao

    def get_all_customers(self, limit=50, offset=0):
        return self.dao.get_all_customers(limit, offset)

    def count_customers(self):
        return self.dao.count_customers()

    def add_customer(self, name, phone, email, address):
        name = name.strip()
        phone = phone.strip()
        email = email.strip()
        if not name:
            return False, "Tên không được để trống"
        if not re.match(r'^0\d{9}$', phone):
            return False, "SĐT phải gồm 10 chữ số, bắt đầu bằng 0"
        if email and not re.match(r'^[\w.+-]+@[\w-]+\.[\w.]+$', email):
            return False, "Email không hợp lệ"
        return self.dao.add_customer(name, phone, email, address)
