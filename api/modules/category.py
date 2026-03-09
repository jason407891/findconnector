"""Category and Manufacturer API Handler"""
from flask import jsonify
from api.utils import BaseAPI


class CategoryAPI(BaseAPI):
    """Handle category and manufacturer related APIs"""
    
    def get_categories(self):
        """Get all product categories"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            return jsonify(categories), 200
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_manufacturers(self):
        """Get all manufacturers/brands"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL ORDER BY brand")
            manufacturers = cursor.fetchall()
            return jsonify(manufacturers), 200
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
