"""Product Search API Handler"""
from flask import jsonify, request
from datetime import date, datetime
from api.utils import BaseAPI


class ProductSearchAPI(BaseAPI):
    """Handle product search functionality"""
    
    def search_products(self, product_name):
        """Search products by part number with pagination"""
        connection = None
        cursor = None
        try:
            # Get page number from query parameters
            page = int(request.args.get("page", 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # 10 items per page
        offset = (page - 1) * 10
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT * FROM products 
                WHERE partnumber LIKE %s
                LIMIT 10 OFFSET %s
                """,
                ("%" + product_name + "%", offset)
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
