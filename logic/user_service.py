class UserService:
    def __init__(self, user_dao):
        self.dao = user_dao

    def login(self, username, password):
        return self.dao.login(username, password)

    def add_user(self, username, password, full_name, role):
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự"
        valid_roles = {'admin', 'staff', 'customer'}
        if role not in valid_roles:
            return False, f"Vai trò không hợp lệ. Chọn: {', '.join(valid_roles)}"
        return self.dao.add_user(username, password, full_name, role)

    def delete_user(self, user_id):
        return self.dao.delete_user(user_id)

    def get_all_users(self):
        return self.dao.get_all_users()

    def update_password_hash(self, user_id, plain_password):
        return self.dao.update_password_hash(user_id, plain_password)

