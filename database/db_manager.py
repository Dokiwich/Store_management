import os
import sys
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv
from contextlib import contextmanager

class DatabaseManager:
    _pool = None

    def __init__(self):
        # Load biến môi trường từ file .env (tìm cả thư mục chứa file, _MEIPASS lẫn cwd)
        candidate_paths = [
            os.path.join(getattr(sys, '_MEIPASS', ''), '.env'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),
            os.path.join(os.getcwd(), '.env')
        ]
        for env_p in candidate_paths:
            if env_p and os.path.exists(env_p):
                load_dotenv(dotenv_path=env_p)
                break
        load_dotenv()
        
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "laptop_shop_pro")
        self._init_pool()

    def _init_pool(self):
        """Khởi tạo Connection Pool một lần duy nhất"""
        if DatabaseManager._pool is None:
            try:
                DatabaseManager._pool = pooling.MySQLConnectionPool(
                    pool_name="laptop_shop_pool",
                    pool_size=15,  # Tối ưu cho ứng dụng web đồng thời
                    pool_reset_session=True,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                print("Đã khởi tạo Database Connection Pool thành công.")
            except Error as e:
                print(f"Lỗi khởi tạo Connection Pool: {e}")

    @property
    def pool(self):
        return DatabaseManager._pool

    def get_connection(self):
        """Lấy kết nối từ Pool"""
        if DatabaseManager._pool is None:
            self._init_pool()
            
        if DatabaseManager._pool is not None:
            try:
                return DatabaseManager._pool.get_connection()
            except Error as e:
                print(f"Lỗi lấy kết nối MySQL từ Pool: {e}")
                return None
        return None

    @contextmanager
    def get_cursor(self):
        """Context manager hỗ trợ lấy cursor tiện lợi"""
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
                conn.close() # Trả kết nối về pool

    def close_connection(self):
        # Với Connection Pool, không cần đóng kết nối chung của app.
        pass
