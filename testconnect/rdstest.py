from mysql.connector import pooling

#  DB 設定
dbconfig = {
    "host": "mydbinstance.cpeog482490h.ap-southeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "mypassword",
    "database": "test02",
    "port": 3306,
    "charset": "utf8mb4",
    "collation":"utf8mb4_general_ci"
}

# 建立連線池
connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    **dbconfig
)

# 測試連線是否成功
def test_db_connection():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")  # 查目前使用的 DB 名
        result = cursor.fetchone()
        print("資料庫連線成功，當前資料庫為：", result[0])
        cursor.close()
        connection.close()
    except Exception as e:
        print("資料庫連線失敗：", e)

# 呼叫測試函式
test_db_connection()
