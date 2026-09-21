class UserService:
    def __init__(self, user_dao):
        self.dao = user_dao

    def login(self, username, password):
        return self.dao.login(username, password)

    def add_user(self, username, password, full_name, role):
        username = username.strip() if username else ""
        full_name = full_name.strip() if full_name else ""
        if not username:
            return False, "Tên đăng nhập không được để trống"
        if not full_name:
            return False, "Họ và tên không được để trống"
        if not password or len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự"
        valid_roles = {'admin', 'staff', 'customer'}
        if role not in valid_roles:
            return False, f"Vai trò không hợp lệ. Chọn: {', '.join(valid_roles)}"
        return self.dao.add_user(username, password, full_name, role)

    def toggle_user_status(self, user_id):
        return self.dao.toggle_user_status(user_id)

    def get_all_users(self):
        return self.dao.get_all_users()

    def update_password_hash(self, user_id, plain_password):
        return self.dao.update_password_hash(user_id, plain_password)

    def delete_user(self, user_id, current_user_role="admin"):
        """Khóa/xóa tài khoản - có xác thực phân quyền 2 lớp (RBAC Service-level Enforcement)."""
        if current_user_role != "admin":
            return False, "403 Forbidden: Chỉ Quản trị viên mới có quyền thao tác này"
        return self.toggle_user_status(user_id)

