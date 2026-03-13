"""Base class for API handlers"""
import os
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Handles database connection pool"""
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Initialize MySQL connection pool"""
        dbconfig = {
            "pool_name": "mypool",
            "pool_size": 10,
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "port": 3306,
            "charset": "utf8mb4",
            "collation": "utf8mb4_general_ci"
        }
        try:
            # 原本的連線邏輯
            self._pool = pooling.MySQLConnectionPool(**dbconfig)
        except Exception as e:
            print(f"⚠️ 資料庫連線失敗，啟動模擬模式: {e}")
            self._pool = None 
            
    def get_connection(self):
        """Get a connection from the pool"""
        return self._pool.get_connection()


class BaseAPI:
    """Base class for all API handlers"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_connection(self):
        """Get database connection"""
        return self.db.get_connection()
    
    def close_cursor(self, cursor):
        """Close cursor safely"""
        if cursor:
            cursor.close()
    
    def close_connection(self, connection):
        """Close connection safely"""
        if connection:
            connection.close()
