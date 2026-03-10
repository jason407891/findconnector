"""Upload History API Handler"""
from flask import jsonify, request
from datetime import date, datetime
import json
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
        """Process batch upload from Excel file with support for tiered pricing
        
        Logic:
        - INSERT: If part number is new OR same part number but different date code
        - UPDATE: If same part number, supplier (upload_user), and date code exist,
                  automatically update price and quantity
        
        Expected Excel columns: 
        - Required: partnumber, brand, dc, qty, category, description
        - Price options (pick one):
          1. Single column 'price' -> [{"quantity": 1, "price": X}]
          2. Multiple price columns 'price_1', 'price_5', 'price_10' -> [{"quantity": 1, "price": X}, {"quantity": 5, "price": Y}, ...]
        
        Example Excel structure:
        partnumber | brand | dc    | qty | price | category | description
        ABC123     | ABC   | 2024  | 100 | 150   | Header   | Details...
        
        Or with tiered pricing:
        partnumber | brand | dc    | qty | price_1 | price_5 | price_10 | category | description
        ABC123     | ABC   | 2024  | 100 | 150     | 145     | 140      | Header   | Details...
        """
        import pandas as pd
        import re
        
        try:
            db = BaseAPI().db
            df = pd.read_excel(profile)
            
            # Function to parse tiered prices from row
            def extract_tiered_price(row):
                """Extract tiered pricing from a row
                
                Looks for:
                1. Single 'price' column
                2. Multiple 'price_N' columns where N is quantity
                
                Returns JSON string or None
                """
                tiers = []
                
                # Check for price_N pattern columns (e.g., price_1, price_5, price_10)
                tier_columns = {col: row[col] for col in row.index 
                              if re.match(r'^price_(\d+)$', col, re.IGNORECASE)}
                
                if tier_columns:
                    # Parse tiered prices
                    for col, value in tier_columns.items():
                        try:
                            match = re.match(r'^price_(\d+)$', col, re.IGNORECASE)
                            if match and pd.notna(value):
                                quantity = int(match.group(1))
                                price = float(value)
                                tiers.append({"quantity": quantity, "price": price})
                        except (ValueError, TypeError, AttributeError):
                            continue
                elif 'price' in row.index and pd.notna(row['price']):
                    # Single price column
                    try:
                        price_val = float(row['price'])
                        tiers.append({"quantity": 1, "price": price_val})
                    except (ValueError, TypeError):
                        pass
                
                # Sort by quantity ascending
                if tiers:
                    tiers.sort(key=lambda x: x['quantity'])
                    return json.dumps(tiers)
                
                return None
            
            # Process each row
            query = """
            INSERT INTO products (
                upload_user, warehouse_address, update_time, 
                partnumber, brand, dc, qty, price, category, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            price = VALUES(price),
            qty = VALUES(qty),
            update_time = VALUES(update_time)
            """
            
            insert_data = []
            for _, row in df.iterrows():
                # Extract tiered pricing
                price_json = extract_tiered_price(row)
                if not price_json:
                    print(f"⚠ Warning: No valid price found for product {row.get('partnumber', 'unknown')}")
                    price_json = json.dumps([{"quantity": 1, "price": 0}])
                
                # Build insert tuple
                try:
                    insert_data.append((
                        upload_user,
                        warehouse_address,
                        time,
                        row.get('partnumber'),
                        row.get('brand'),
                        row.get('dc', ''),
                        int(row.get('qty', 0)),
                        price_json,
                        row.get('category', ''),
                        row.get('description', '')
                    ))
                except (ValueError, KeyError, TypeError) as e:
                    print(f"⚠ Warning: Error processing row {_}: {e}")
                    continue
            
            # Execute batch insert
            connection = None
            cursor = None
            try:
                connection = db.get_connection()
                cursor = connection.cursor()
                if insert_data:
                    cursor.executemany(query, insert_data)
                    connection.commit()
                    print(f"✓ Batch upload processed: {len(insert_data)} records inserted or updated")
                else:
                    print("⚠ Warning: No valid data found in uploaded file")
            except Exception as e:
                print(f"✗ Batch upload error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        
        except Exception as e:
            print(f"✗ Error processing batch upload: {e}")
