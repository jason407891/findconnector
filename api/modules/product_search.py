"""Product Search API Handler"""
from flask import jsonify, request
from datetime import date, datetime
import json
from api.utils import BaseAPI


class ProductSearchAPI(BaseAPI):
    """Handle product search functionality"""
    
    def search_products(self, product_name):
        """Search products by part number with pagination, filtering, and sorting"""
        connection = None
        cursor = None
        try:
            # Get parameters from query string
            page = int(request.args.get("page", 1))
            if page < 1:
                page = 1
            
            # Get sorting parameter
            sort_by = request.args.get("sort", "update_time")  # default: by update_time (newest first)
            sort_order = request.args.get("order", "DESC")  # ASC or DESC
            
            # Get filtering parameters
            min_price = request.args.get("min_price", None)
            max_price = request.args.get("max_price", None)
            min_qty = request.args.get("min_qty", None)
            max_qty = request.args.get("max_qty", None)
            brand_filter = request.args.get("brand", None)
            category_filter = request.args.get("category", None)
            
            # Validate sort parameters
            valid_sort_options = ["price", "qty", "update_time", "partnumber", "brand"]
            if sort_by not in valid_sort_options:
                sort_by = "update_time"
            
            if sort_order.upper() not in ["ASC", "DESC"]:
                sort_order = "DESC"
            
        except (ValueError, TypeError):
            page = 1
            sort_by = "update_time"
            sort_order = "DESC"
        
        # 10 items per page
        offset = (page - 1) * 10
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build the query dynamically
            query = "SELECT * FROM products WHERE partnumber LIKE %s"
            params = ["%" + product_name + "%"]
            
            # Add filtering conditions
            if min_price:
                try:
                    min_price_val = float(min_price)
                    query += " AND price >= %s"
                    params.append(min_price_val)
                except (ValueError, TypeError):
                    pass
            
            if max_price:
                try:
                    max_price_val = float(max_price)
                    query += " AND price <= %s"
                    params.append(max_price_val)
                except (ValueError, TypeError):
                    pass
            
            if min_qty:
                try:
                    min_qty_val = int(min_qty)
                    query += " AND qty >= %s"
                    params.append(min_qty_val)
                except (ValueError, TypeError):
                    pass
            
            if max_qty:
                try:
                    max_qty_val = int(max_qty)
                    query += " AND qty <= %s"
                    params.append(max_qty_val)
                except (ValueError, TypeError):
                    pass
            
            if brand_filter:
                query += " AND brand LIKE %s"
                params.append("%" + brand_filter + "%")
            
            if category_filter:
                query += " AND category LIKE %s"
                params.append("%" + category_filter + "%")
            
            # Add sorting
            query += f" ORDER BY {sort_by} {sort_order}"
            
            # Add pagination
            query += " LIMIT 10 OFFSET %s"
            params.append(offset)
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            # Convert date objects to strings (YYYY-MM-DD format) and handle JSON price
            for product in products:
                # Handle update_time
                if isinstance(product.get("update_time"), (date, datetime)):
                    product["update_time"] = product["update_time"].strftime("%Y-%m-%d")
                
                # Handle price - ensure it's parsed as JSON
                if product.get("price"):
                    try:
                        # If price is already a dict/list (from cursor), keep it
                        if isinstance(product["price"], (dict, list)):
                            product["price"] = product["price"]
                        # If it's a string, try to parse as JSON
                        elif isinstance(product["price"], str):
                            try:
                                product["price"] = json.loads(product["price"])
                            except (json.JSONDecodeError, ValueError):
                                # Fallback: wrap single price in format
                                try:
                                    price_val = float(product["price"])
                                    product["price"] = [{"quantity": 1, "price": price_val}]
                                except (ValueError, TypeError):
                                    product["price"] = None
                    except Exception:
                        product["price"] = None
            
            return jsonify(products), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
