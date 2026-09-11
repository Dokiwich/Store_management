import mysql.connector
import bcrypt

class UserDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login(self, username, password):
        """
        Kiểm tra đăng nhập bằng cách so sánh Hash
        """
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True) 
            try:
                # 1. Chỉ tìm theo username trước (không check pass trong SQL nữa)
                sql = "SELECT * FROM users WHERE username = %s AND is_active = 1"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
            finally:
                cursor.close()
            
            if user:
                # 2. Lấy mật khẩu đã mã hóa từ DB
                stored_hash = user['password']
                
                # 3. Kiểm tra mật khẩu nhập vào có khớp với Hash không
                # Lưu ý: bcrypt cần dữ liệu dạng bytes (dùng .encode('utf-8'))
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        user.pop('password', None)
                        return user
                except ValueError:
                    # Invalid hash format - do not fall back to plaintext comparison
                    return None
                    
        return None

    def add_user(self, username, password, full_name, role):
        """
        Thêm nhân viên mới với mật khẩu đã được mã hóa
        """
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # 1. Mã hóa mật khẩu (Hashing)
                # gensalt() tạo ra một chuỗi ngẫu nhiên để chống lại Rainbow Table attack
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                
                # 2. Lưu password đã mã hóa vào DB
                sql = "INSERT INTO users (username, password, full_name, role, is_active) VALUES (%s, %s, %s, %s, 1)"
                cursor.execute(sql, (username, hashed_pw, full_name, role))
                conn.commit()
                return True, "Thêm thành công!"
            except mysql.connector.Error as err:
                return False, f"Lỗi Database: {err}"
            except Exception as e:
                return False, str(e)
            finally:
                cursor.close()
        return False, "Lỗi kết nối"

    def delete_user(self, user_id):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "UPDATE users SET is_active = 0 WHERE id = %s"
                cursor.execute(sql, (user_id,))
                conn.commit()
                return True
            except Exception as e:
                print(e)
                return False
            finally:
                cursor.close()
        return False

    def get_all_users(self):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT id, username, full_name, role, is_active FROM users"
                cursor.execute(sql)
                return cursor.fetchall()
            finally:
                cursor.close()
        return []

    # Hàm phụ trợ: Cập nhật hash cho tài khoản cũ (Tự động chạy khi login lần đầu)
    def update_password_hash(self, user_id, plain_password):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
                conn.commit()
                print(f"Đã tự động nâng cấp bảo mật cho User ID {user_id}")
            except Exception as e:
                print(f"Lỗi nâng cấp bảo mật: {e}")
            finally:
                cursor.close()