"""Product Management API Handler"""
from flask import jsonify, request
from datetime import datetime
import json
from api.utils import BaseAPI
from api.modules.user import UserAPI
from py_profile.s3 import insert_file_s3


class ProductManagementAPI(BaseAPI):
    """Handle product upload, edit, and delete operations"""
    
    @staticmethod
    def _parse_tiered_price(price_data):
        """Parse tiered price from form data
        
        Accepts multiple formats:
        1. Single price (string/number): "100" -> [{"quantity": 1, "price": 100}]
        2. JSON array string: '[{"quantity": 1, "price": 100}]' -> same format
        3. Form with individual price fields: price_tier_1, price_tier_5, price_tier_10, etc.
        
        Returns JSON array of tier objects, or None if invalid
        """
        try:
            if isinstance(price_data, str):
                # Try to parse as JSON array
                if price_data.strip().startswith('['):
                    tiers = json.loads(price_data)
                    # Validate structure
                    if isinstance(tiers, list) and all(
                        isinstance(t, dict) and 'quantity' in t and 'price' in t 
                        for t in tiers
                    ):
                        return tiers
                else:
                    # Single price value
                    price_val = float(price_data)
                    return [{"quantity": 1, "price": price_val}]
            elif isinstance(price_data, (int, float)):
                return [{"quantity": 1, "price": float(price_data)}]
            elif isinstance(price_data, list):
                # Already a list, validate it
                if all(isinstance(t, dict) and 'quantity' in t and 'price' in t for t in price_data):
                    return price_data
        except (ValueError, TypeError, json.JSONDecodeError):
            pass
        
        return None
    
    def upload_single_product(self):
        """Upload a single product with image and tiered pricing
        
        Logic:
        - INSERT: If part number is new OR same part number but different date code
        - UPDATE: If same part number, supplier (upload_user), and date code exist,
                  automatically update price and quantity
        
        Price format: Can be single value or JSON array of tiered prices
        - Single: "100" -> [{"quantity": 1, "price": 100}]
        - Array: '[{"quantity": 1, "price": 100}, {"quantity": 5, "price": 95}]'
        """
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
            price_input = request.form.get("price")
            
            # Parse tiered pricing
            price_tiers = self._parse_tiered_price(price_input)
            if not price_tiers:
                return jsonify({"error": True, "message": "Invalid price format"}), 400
            
            price_json = json.dumps(price_tiers)
            
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
            
            # Insert to database with automatic update on duplicate key
            # Unique key: (partnumber, upload_user, dc)
            # - If new: INSERT all fields
            # - If duplicate: UPDATE price and qty only
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO products 
                   (upload_user, product_img, update_time, partnumber, brand, dc, qty, warehouse_address, price, category, description) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE 
                   price = VALUES(price),
                   qty = VALUES(qty),
                   update_time = VALUES(update_time)""",
                (upload_user, product_img, yearmonthday, partnumber, brand, dc, qty, warehouse_address, price_json, category, description)
            )
            connection.commit()
            return jsonify({"ok": True, "message": "Product uploaded successfully"}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def edit_product(self):
        """Edit existing product (quantity and price with tiered pricing support)
        
        Matches product by: partnumber, upload_user (supplier), and dc (date code)
        
        Price can be:
        - Single value: {"price": 100}
        - Array of tiers: {"price": [{"quantity": 1, "price": 100}, {"quantity": 5, "price": 95}]}
        """
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
            price_input = data.get("price")
            dc = data.get("datecode", "")  # Date code is required for unique identification
            
            # Parse tiered pricing
            price_tiers = self._parse_tiered_price(price_input)
            if not price_tiers:
                return jsonify({"error": True, "message": "Invalid price format"}), 400
            
            price_json = json.dumps(price_tiers)
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Update by partnumber, upload_user (supplier), and dc (date code)
            # This matches the unique key constraint
            query = """
            UPDATE products
            SET qty=%s, price=%s, update_time=NOW()
            WHERE partnumber=%s AND upload_user=%s AND dc=%s
            """
            cursor.execute(query, (qty, price_json, partnumber, upload_user, dc))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": True, "message": "Product not found"}), 404
            
            return jsonify({"ok": True, "message": "Product updated successfully"}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def delete_product(self):
        """Delete a product
        
        Matches product by: partnumber, upload_user (supplier), and dc (date code)
        """
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
            dc = data.get("datecode", "")  # Date code is required for unique identification
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Delete by partnumber, upload_user (supplier), and dc (date code)
            # This matches the unique key constraint
            query = """
            DELETE FROM products
            WHERE partnumber=%s AND upload_user=%s AND dc=%s
            """
            cursor.execute(query, (partnumber, upload_user, dc))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": True, "message": "Product not found"}), 404
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
