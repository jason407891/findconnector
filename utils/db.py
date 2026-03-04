import os
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

# 資料庫設定 (確保你的 .env 裡面有這些變數)
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": 3306
}

# 建立連線池
# pool_size=5 代表它會先開好 5 個連線備用，不用每次都握手
pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

def get_db_connection():
    """從池子裡借一個連線出來"""
    return pool.get_connection()