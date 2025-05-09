from flask import *
import jwt
from jwt.exceptions import DecodeError
from datetime import datetime, date
import requests
import os
from py_profile.s3 import insert_file_s3
from dotenv import load_dotenv #載入環境
import os
import pandas as pd
from mysql.connector import pooling
load_dotenv()


app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSONIFY_MIMETYPE"] = 'application/json; charset=utf-8'
app.config ['JSON_SORT_KEYS'] = False


dbconfig = {
    "pool_name": "mypool",
    "pool_size": 10,
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": 3306,
    "charset": "utf8mb4",
    "collation":"utf8mb4_general_ci"
}

# 創建 MySQL 連接池
connection_pool = pooling.MySQLConnectionPool(**dbconfig)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bom")
def bom():
    return render_template("bom.html")

@app.route("/category/<category_name>")
def category(category_name):
    return render_template("category.html",category_name=category_name)
@app.route("/brand")
def brand():
    return render_template("brand.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/search/<partnumber>")
def product(partnumber):
    return render_template("product.html",partnumber=partnumber)

@app.route("/upload")
def upload():
    return render_template("upload.html")
@app.route("/introduction")
def introduction():
    return render_template("introduction.html")


#產品種類
@app.route("/api/showcategories", methods=["GET"])
def showcategories():
    connection = connection_pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()       
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#註冊
@app.route("/api/user",methods=["POST"])
def api_register():
    try:
        connection = connection_pool.get_connection()
        data=request.get_json()
        name=data.get("name")
        email=data.get("email")
        password=data.get("password")
        company_name=data.get("company_name")
        phone_number=data.get("phone_number")
        address=data.get("address")
        
        #檢查是否存在USER
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_email=%s", (email,))
        existing_user=cursor.fetchone()
        if existing_user:
            return jsonify({"error": True, "message": "此帳號已經被註冊過"}), 400
        #註冊到RDS資料庫
        cursor.execute("INSERT INTO users (user_name, user_email, user_password, company_name, phone_number, warehouse_address) VALUES (%s, %s, %s, %s, %s, %s)", (name, email, password, company_name, phone_number, address))
        connection.commit()
        return jsonify({"ok": True}), 200
    
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#登入/驗證
@app.route("/api/user/auth",methods=["PUT","GET"])
def api_login():
    connection = connection_pool.get_connection()
    cursor = None
    try:
        if request.method == "PUT":
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            cursor = connection.cursor()
            cursor.execute("SELECT id, user_name, user_email, warehouse_address FROM users WHERE user_email = %s AND user_password = %s", (email, password))
            user = cursor.fetchone()
            if user:
                user_info = {
                    "user_id": user[0],
                    "user_name": user[1],
                    "user_email": user[2],
                    "warehouse_address": user[3]
                }

                # 生成 JWT Token
                token = jwt.encode(user_info, os.getenv("secret_key"), algorithm="HS256")

                return jsonify({"token": token})
            else:
                return jsonify({"error":True, "message":"帳號或是密碼輸入錯誤"}), 400
        elif request.method == "GET":
            token = request.headers.get("Authorization")
            if token=="null":
                return jsonify({"error":True,"message":"user not login"}), 400
            try:
                user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
                return jsonify({"data": user_info}),200
            except DecodeError as e:
                return jsonify({"error":True,"message":str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#上傳單筆產品
@app.route("/api/uploadone",methods=["POST"])
def api_uploadone():
    connection = connection_pool.get_connection()
    try:
        #取得登入者資料
        token=request.headers.get("Authorization")
        token=str(token)
        user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
        upload_user=user_info["user_email"] 
        warehouse_address=user_info["warehouse_address"] 
        user_id=user_info["user_id"] 
        #取得產品上傳資料 因為有檔案類型，所以要用form.get
        time=datetime.now()
        brand=request.form.get("brand")
        partnumber=request.form.get("partnumber")
        qty=request.form.get("quantity")
        dc=request.form.get("datecode")
        category=request.form.get("category")
        description=request.form.get("description")
        price=request.form.get("price")
        #取得照片資料
        getimg=request.files['product_img'] ##前端需設置INPUT的name為product_img type=file!
        if getimg:
            product_img = insert_file_s3(time.strftime("%H:%M:%S"),user_id,partnumber,getimg) ##上傳圖片到S3並取得圖片網址
        else:
            product_img=None
        yearmonthday=time.strftime("%Y-%m-%d")
        #上傳到RDS資料庫
        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (upload_user, product_img,update_time,partnumber,brand, dc, qty,warehouse_address,price,category,description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", (upload_user,product_img,yearmonthday,partnumber,brand, dc, qty, warehouse_address, price,category,description))
        connection.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#編輯產品
@app.route("/api/editproduct",methods=["PUT"])
def api_editproduct():
    connection = connection_pool.get_connection()
    try:
        #取得登入者資料
        token=request.headers.get("Authorization")
        token=str(token)
        user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
        upload_user=user_info["user_email"]
        #取得產品上傳資料
        data=request.get_json()
        partnumber=data.get("partnumber")
        qty=data.get("quantity")
        price=data.get("price")
        cursor = connection.cursor()
        query="""
        UPDATE products
        SET qty=%s,price=%s
        WHERE partnumber=%s AND upload_user=%s
        """
        cursor.execute(query,(qty,price,partnumber,upload_user))
        connection.commit()
        return jsonify({"ok": True}), 200
    
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


#刪除上傳紀錄
@app.route("/api/deleteproduct",methods=["DELETE"])
def api_deleteproduct():
    connection = connection_pool.get_connection()
    cursor = None
    try:
        #取得登入者資料
        token=request.headers.get("Authorization")
        token=str(token)
        user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
        upload_user=user_info["user_email"]
        #取得產品上傳資料
        data=request.get_json()
        partnumber=data.get("partnumber")
        cursor = connection.cursor()
        query="""
        DELETE FROM products
        WHERE partnumber=%s AND upload_user=%s
        """
        cursor.execute(query,(partnumber,upload_user))
        connection.commit()
        return jsonify({"ok": True}), 200
    
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#搜尋產品
@app.route("/api/search/<product>",methods=["GET"])
def api_search(product):
    cursor = None
    connection = connection_pool.get_connection()
    #取得產品頁數
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    #1頁=10筆資料
    offset=(page-1)*10
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
                       SELECT * FROM products 
                       WHERE partnumber LIKE %s
                       LIMIT 10 OFFSET %s
                       """,("%"+product+"%",offset))
        products = cursor.fetchall()
        #將日期轉換為字串，只有年月日
        for product in products:
            if isinstance(product["update_time"], (date, datetime)):
                product["update_time"] = product["update_time"].strftime("%Y-%m-%d")      
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#搜尋上傳歷史紀錄
@app.route("/api/uploadhistory",methods=["GET"])
def api_uploadhistory():
    connection = connection_pool.get_connection()
    #取得登入者資料
    token=request.headers.get("Authorization")
    token=str(token)
    user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
    upload_user=user_info["user_email"]
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE upload_user=%s ORDER BY update_time DESC",(upload_user,))
        products = cursor.fetchall()
        #將日期轉換為字串，只有年月日
        for product in products:
            if isinstance(product["update_time"], (date, datetime)):
                product["update_time"] = product["update_time"].strftime("%Y-%m-%d")      
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#批量上傳產品
@app.route("/api/batchupload",methods=["POST"])
def api_batchupload():
    try:
        #取得登入者資料
        token=request.headers.get("Authorization")
        token=str(token)
        user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
        upload_user=user_info["user_email"] 
        warehouse_address=user_info["warehouse_address"] 
        time=datetime.now()
        time=time.strftime("%Y-%m-%d")
        #取得上傳檔案
        profile=request.files['uploadfile']
        upload_many(profile,upload_user,warehouse_address,time)
        return jsonify({"message": "batch upload successfully"}),200
    except Exception as e:
        return jsonify({"message": "fail to batch upload "+str(e)}),500

#製造商
@app.route("/api/manufacturer",methods=["GET"])
def api_allmfr():
    connection = connection_pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT brand FROM products")
        manufacturers = cursor.fetchall()       
        return jsonify(manufacturers), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#聯繫我
@app.route("/api/contact",methods=["POST"])
def api_sendmsg():
    try:
        webhook_url=os.getenv("dc_url")
        data=request.get_json()
        content=data["content"]
        headers = {'Content-Type': 'application/json'}
        output={"content":content}
        requests.post(webhook_url, json=output, headers=headers)
        return jsonify({"message": "feedback send successfully"}),200
    except Exception as e:
	    return jsonify({"message": "fail to give feedback "+str(e)}),500


#一次上傳多個檔案
def upload_many(profile,upload_user,warehouse_address,time):
    df = pd.read_excel(profile)
    #column=df.columns.tolist()
    data = df.values.tolist()
    upload_user=upload_user
    warehouse_address=warehouse_address
    time=time
    query="""
    INSERT INTO products (
        upload_user, warehouse_address, update_time, 
        partnumber, brand, dc, qty, price, category, description
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        price = VALUES(price),
        qty = VALUES(qty)
    """

    insert_data=[(upload_user,warehouse_address,time,*row) for row in data]
    

    connection = None
    cursor = None
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














app.run(host="0.0.0.0", port=3000)