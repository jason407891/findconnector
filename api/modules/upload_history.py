"""Upload History API Handler"""
from flask import jsonify, request
from datetime import date, datetime
from api.utils import BaseAPI
from api.modules.user import UserAPI


class UploadHistoryAPI(BaseAPI):
    """Handle upload history and batch upload operations"""
    
    def get_upload_history(self):
        """Get upload history for authenticated user"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            upload_user = user_info["user_email"]
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM products WHERE upload_user=%s ORDER BY update_time DESC",
                (upload_user,)
            )
            products = cursor.fetchall()
            
            # Convert date objects to strings (YYYY-MM-DD format)
            for product in products:
                if isinstance(product["update_time"], (date, datetime)):
                    product["update_time"] = product["update_time"].strftime("%Y-%m-%d")
            
            return jsonify(products), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def batch_upload(self):
        """Upload multiple products from Excel file"""
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            upload_user = user_info["user_email"]
            warehouse_address = user_info["warehouse_address"]
            
            time = datetime.now()
            time_str = time.strftime("%Y-%m-%d")
            
            # Get uploaded file
            if 'uploadfile' not in request.files:
                return jsonify({"error": True, "message": "No file provided"}), 400
            
            profile = request.files['uploadfile']
            self._process_batch_upload(profile, upload_user, warehouse_address, time_str)
            
            return jsonify({"message": "batch upload successfully"}), 200
        
        except Exception as e:
            return jsonify({"message": f"fail to batch upload {str(e)}"}), 500
    
    @staticmethod
    def _process_batch_upload(profile, upload_user, warehouse_address, time):
        """Process batch upload from Excel file"""
        import pandas as pd
        
        try:
            db = BaseAPI().db
            df = pd.read_excel(profile)
            data = df.values.tolist()
            
            query = """
            INSERT INTO products (
                upload_user, warehouse_address, update_time, 
                partnumber, brand, dc, qty, price, category, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            price = VALUES(price),
            qty = VALUES(qty)
            """
            
            insert_data = [(upload_user, warehouse_address, time, *row) for row in data]
            
            connection = None
            cursor = None
            try:
                connection = db.get_connection()
                cursor = connection.cursor()
                cursor.executemany(query, insert_data)
                connection.commit()
            except Exception as e:
                print(f"Batch upload error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        
        except Exception as e:
            print(f"Error processing batch upload: {e}")
