import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        # Load biến môi trường từ file .env
        load_dotenv()
        
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "laptop_shop_pro")
        self.connection = None

    def get_connection(self):
        """Tạo kết nối đến CSDL"""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            except Error as e:
                print(f"Lỗi kết nối MySQL trong DatabaseManager.get_connection: {e}")
                return None
        return self.connection

    @contextmanager
    def get_cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
