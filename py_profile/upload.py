import pandas as pd
from py_profile.db import connection_pool

def upload_many(profile,upload_user,warehouse_address,time):
    df = pd.read_excel(profile)
    #column=df.columns.tolist()
    data = df.values.tolist()
    print(data)
    upload_user=upload_user
    warehouse_address=warehouse_address
    time=time
    query="""
    INSERT INTO products (
        upload_user, warehouse_address, update_time, 
        partnumber, brand, dc, qty, price, category, description
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        brand = VALUES(brand),
        qty = VALUES(qty)
    """
    insert_data=[(upload_user,warehouse_address,time,*row) for row in data]
    
    #插入數據
    try:
        connection = connection_pool.get_connection()
        cursor=connection.cursor()
        cursor.executemany(query, insert_data)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()