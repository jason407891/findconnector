from flask import *
import mysql.connector
import jwt
from jwt.exceptions import DecodeError
from datetime import datetime, date
import mysql.connector
import requests
from mysql.connector import pooling
import os
from dotenv import load_dotenv #載入環境
from py_profile.s3 import insert_file_s3
from py_profile.upload import upload_many
from py_profile.db import connection_pool
load_dotenv()

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSONIFY_MIMETYPE"] = 'application/json; charset=utf-8'
app.config ['JSON_SORT_KEYS'] = False




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
    connection=None
    cursor=None
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
    connection=None
    cursor=None
    connection = connection_pool.get_connection()
    try:
        if request.method == "PUT":
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            cursor = connection.cursor()
            cursor.execute("SELECT id, user_name, user_email, warehouse_address FROM users WHERE user_email = %s AND user_password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
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
    connection=None
    cursor=None
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
        product_img = insert_file_s3(time.strftime("%H:%M:%S"),user_id,partnumber,getimg) ##上傳圖片到S3並取得圖片網址
        yearmonthday=time.strftime("%Y-%m-%d")
        #上傳到RDS資料庫
        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (upload_user, product_img,update_time,partnumber,brand, dc, qty,warehouse_address,price,category,description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (upload_user,product_img,yearmonthday,partnumber,brand, dc, qty, warehouse_address, price,category,description))
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
    connection=None
    cursor=None
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
    connection=None
    cursor=None
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
    connection=None
    cursor=None
    connection = connection_pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE partnumber LIKE %s",("%"+product+"%",))
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
    connection=None
    cursor=None
    connection = connection_pool.get_connection()
    #取得登入者資料
    token=request.headers.get("Authorization")
    token=str(token)
    user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
    upload_user=user_info["user_email"]
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE upload_user=%s",(upload_user,))
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
    connection=None
    cursor=None
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


app.run(host="0.0.0.0", port=3000)