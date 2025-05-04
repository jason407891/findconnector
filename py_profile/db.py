import os
from mysql.connector import pooling
from dotenv import load_dotenv
load_dotenv()


dbconfig = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": 3306,
    "charset": "utf8mb4",
    "collation":"utf8mb4_general_ci"
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=20, 
    **dbconfig
)