"""Product Management API Handler"""
from flask import jsonify, request
from datetime import datetime
from api.utils import BaseAPI
from api.modules.user import UserAPI
from py_profile.s3 import insert_file_s3


class ProductManagementAPI(BaseAPI):
    """Handle product upload, edit, and delete operations"""
    
    def upload_single_product(self):
        """Upload a single product with image"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            upload_user = user_info["user_email"]
            warehouse_address = user_info["warehouse_address"]
            user_id = user_info["user_id"]
            
            # Get product data from form
            time = datetime.now()
            brand = request.form.get("brand")
            partnumber = request.form.get("partnumber")
            qty = request.form.get("quantity")
            dc = request.form.get("datecode")
            category = request.form.get("category")
            description = request.form.get("description")
            price = request.form.get("price")
            
            # Get image file
            product_img = None
            if 'product_img' in request.files:
                getimg = request.files['product_img']
                if getimg:
                    # Upload image to S3 and get URL
                    product_img = insert_file_s3(
                        time.strftime("%H:%M:%S"),
                        user_id,
                        partnumber,
                        getimg
                    )
            
            yearmonthday = time.strftime("%Y-%m-%d")
            
            # Insert to database
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO products 
                   (upload_user, product_img, update_time, partnumber, brand, dc, qty, warehouse_address, price, category, description) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (upload_user, product_img, yearmonthday, partnumber, brand, dc, qty, warehouse_address, price, category, description)
            )
            connection.commit()
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def edit_product(self):
        """Edit existing product (quantity and price)"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            upload_user = user_info["user_email"]
            
            # Get product data
            data = request.get_json()
            partnumber = data.get("partnumber")
            qty = data.get("quantity")
            price = data.get("price")
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query = """
            UPDATE products
            SET qty=%s, price=%s
            WHERE partnumber=%s AND upload_user=%s
            """
            cursor.execute(query, (qty, price, partnumber, upload_user))
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def delete_product(self):
        """Delete a product"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            upload_user = user_info["user_email"]
            
            # Get product data
            data = request.get_json()
            partnumber = data.get("partnumber")
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query = """
            DELETE FROM products
            WHERE partnumber=%s AND upload_user=%s
            """
            cursor.execute(query, (partnumber, upload_user))
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
