"""Admin API Handler - User and Product Management"""
from flask import jsonify, request
from datetime import datetime
from api.utils import BaseAPI
from api.modules.user import UserAPI


class AdminAPI(BaseAPI):
    """Handle admin operations for user and product management"""
    
    @staticmethod
    def check_admin_permission():
        """Check if user has admin privileges"""
        user_info = UserAPI.get_user_from_token()
        if not user_info:
            return None
        
        connection = None
        cursor = None
        try:
            connection = BaseAPI().get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT role FROM users WHERE id=%s",
                (user_info["user_id"],)
            )
            result = cursor.fetchone()
            if result and result["role"] in ["admin", "super_admin"]:
                return user_info
            return None
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # ========================
    # USER MANAGEMENT
    # ========================
    
    def get_all_users(self):
        """Get all users with pagination"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            page = int(request.args.get("page", 1))
            if page < 1:
                page = 1
            
            search = request.args.get("search", "")
            role_filter = request.args.get("role", "")
            
            limit = 20
            offset = (page - 1) * limit
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build query
            where_clause = "WHERE 1=1"
            params = []
            
            if search:
                where_clause += " AND (user_name LIKE %s OR user_email LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            if role_filter:
                where_clause += " AND role=%s"
                params.append(role_filter)
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM users {where_clause}", params)
            total = cursor.fetchone()["total"]
            
            # Get users
            cursor.execute(
                f"""SELECT id, user_name, user_email, company_name, phone_number, 
                           warehouse_address, role, created_at, updated_at 
                   FROM users {where_clause} 
                   ORDER BY created_at DESC 
                   LIMIT %s OFFSET %s""",
                params + [limit, offset]
            )
            users = cursor.fetchall()
            
            return jsonify({
                "users": users,
                "page": page,
                "total": total,
                "pages": (total + limit - 1) // limit
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_user_detail(self, user_id):
        """Get specific user details"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, user_name, user_email, company_name, phone_number, 
                           warehouse_address, role, created_at, updated_at 
                   FROM users WHERE id=%s""",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"error": True, "message": "User not found"}), 404
            
            return jsonify(user), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def edit_user(self, user_id):
        """Edit user information"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            data = request.get_json()
            
            # Only super_admin can change role
            user_info = self.check_admin_permission()
            if data.get("role") and user_info["role"] != "super_admin":
                return jsonify({"error": True, "message": "Only super admin can change user role"}), 403
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Update allowed fields
            update_fields = []
            params = []
            
            allowed_fields = ["user_name", "company_name", "phone_number", "warehouse_address"]
            if user_info["role"] == "super_admin":
                allowed_fields.append("role")
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field}=%s")
                    params.append(data[field])
            
            if not update_fields:
                return jsonify({"error": True, "message": "No fields to update"}), 400
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)}, updated_at=NOW() WHERE id=%s"
            cursor.execute(query, params)
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def delete_user(self, user_id):
        """Delete user"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        user_info = self.check_admin_permission()
        if user_info["role"] != "super_admin":
            return jsonify({"error": True, "message": "Only super admin can delete users"}), 403
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Don't delete super_admin users
            cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if user and user[0] == "super_admin":
                return jsonify({"error": True, "message": "Cannot delete super admin user"}), 403
            
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def set_user_role(self, user_id):
        """Set user role (super_admin only)"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        user_info = self.check_admin_permission()
        if user_info["role"] != "super_admin":
            return jsonify({"error": True, "message": "Only super admin can set roles"}), 403
        
        connection = None
        cursor = None
        try:
            data = request.get_json()
            role = data.get("role")
            
            valid_roles = ["user", "admin", "super_admin"]
            if role not in valid_roles:
                return jsonify({"error": True, "message": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}), 400
            
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET role=%s WHERE id=%s", (role, user_id))
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    # ========================
    # PRODUCT MANAGEMENT
    # ========================
    
    def get_all_products(self):
        """Get all products with pagination and filters"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            page = int(request.args.get("page", 1))
            if page < 1:
                page = 1
            
            search = request.args.get("search", "")
            status_filter = request.args.get("status", "")
            category_filter = request.args.get("category", "")
            
            limit = 20
            offset = (page - 1) * limit
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Build query
            where_clause = "WHERE 1=1"
            params = []
            
            if search:
                where_clause += " AND (partnumber LIKE %s OR product_name LIKE %s OR brand LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
            if status_filter:
                where_clause += " AND status=%s"
                params.append(status_filter)
            
            if category_filter:
                where_clause += " AND category=%s"
                params.append(category_filter)
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM products {where_clause}", params)
            total = cursor.fetchone()["total"]
            
            # Get products
            cursor.execute(
                f"""SELECT id, upload_user, partnumber, brand, qty, price, 
                           category, status, product_img, update_time, created_at 
                   FROM products {where_clause} 
                   ORDER BY update_time DESC 
                   LIMIT %s OFFSET %s""",
                params + [limit, offset]
            )
            products = cursor.fetchall()
            
            return jsonify({
                "products": products,
                "page": page,
                "total": total,
                "pages": (total + limit - 1) // limit
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_product_detail(self, product_id):
        """Get specific product details"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT * FROM products WHERE id=%s""",
                (product_id,)
            )
            product = cursor.fetchone()
            
            if not product:
                return jsonify({"error": True, "message": "Product not found"}), 404
            
            return jsonify(product), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def edit_product(self, product_id):
        """Edit product information"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            data = request.get_json()
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Update allowed fields
            update_fields = []
            params = []
            
            allowed_fields = ["brand", "qty", "price", "category", "description", "status"]
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field}=%s")
                    params.append(data[field])
            
            if not update_fields:
                return jsonify({"error": True, "message": "No fields to update"}), 400
            
            params.append(product_id)
            query = f"UPDATE products SET {', '.join(update_fields)}, update_time=NOW() WHERE id=%s"
            cursor.execute(query, params)
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def delete_product(self, product_id):
        """Delete product"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def approve_product(self, product_id):
        """Approve/publish product"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "UPDATE products SET status='published' WHERE id=%s",
                (product_id,)
            )
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def reject_product(self, product_id):
        """Reject product"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            data = request.get_json() or {}
            reason = data.get("reason", "")
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "UPDATE products SET status='rejected', description=%s WHERE id=%s",
                (reason, product_id)
            )
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_statistics(self):
        """Get admin dashboard statistics"""
        if not self.check_admin_permission():
            return jsonify({"error": True, "message": "Unauthorized"}), 401
        
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Total users
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()["total"]
            
            # Total products
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total_products = cursor.fetchone()["total"]
            
            # Pending products
            cursor.execute("SELECT COUNT(*) as total FROM products WHERE status='pending'")
            pending_products = cursor.fetchone()["total"]
            
            # Active conversations
            cursor.execute("SELECT COUNT(*) as total FROM conversations WHERE status='open'")
            active_chats = cursor.fetchone()["total"]
            
            return jsonify({
                "total_users": total_users,
                "total_products": total_products,
                "pending_products": pending_products,
                "active_chats": active_chats
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
