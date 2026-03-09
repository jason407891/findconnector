"""User API Handler - Registration and Authentication"""
import jwt
from jwt.exceptions import DecodeError
from flask import jsonify, request
import os
from dotenv import load_dotenv
from api.utils import BaseAPI

load_dotenv()


class UserAPI(BaseAPI):
    """Handle user registration and authentication"""
    
    def register(self):
        """Register a new user"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            data = request.get_json()
            
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            company_name = data.get("company_name")
            phone_number = data.get("phone_number")
            address = data.get("address")
            
            # Check if user already exists
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE user_email=%s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return jsonify({"error": True, "message": "此帳號已經被註冊過"}), 400
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (user_name, user_email, user_password, company_name, phone_number, warehouse_address) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, password, company_name, phone_number, address)
            )
            connection.commit()
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def login(self):
        """Authenticate user and return JWT token"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            data = request.get_json()
            
            email = data.get('email')
            password = data.get('password')
            
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, user_name, user_email, warehouse_address FROM users WHERE user_email = %s AND user_password = %s",
                (email, password)
            )
            user = cursor.fetchone()
            
            if user:
                user_info = {
                    "user_id": user[0],
                    "user_name": user[1],
                    "user_email": user[2],
                    "warehouse_address": user[3]
                }
                
                # Generate JWT Token
                token = jwt.encode(user_info, os.getenv("secret_key"), algorithm="HS256")
                return jsonify({"token": token}), 200
            else:
                return jsonify({"error": True, "message": "帳號或是密碼輸入錯誤"}), 400
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def verify_token(self):
        """Verify JWT token and return user info"""
        try:
            token = request.headers.get("Authorization")
            
            if token == "null" or not token:
                return jsonify({"error": True, "message": "user not login"}), 400
            
            try:
                user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
                return jsonify({"data": user_info}), 200
            except DecodeError as e:
                return jsonify({"error": True, "message": str(e)}), 500
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
    
    @staticmethod
    def get_user_from_token():
        """Helper method to extract user info from JWT token"""
        try:
            token = request.headers.get("Authorization")
            if token == "null" or not token:
                return None
            user_info = jwt.decode(token, os.getenv("secret_key"), algorithms=["HS256"])
            return user_info
        except Exception:
            return None
