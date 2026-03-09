"""Chat API Handler - User and Customer Service Communication"""
from flask import jsonify, request
from datetime import datetime
from api.utils import BaseAPI
from api.modules.user import UserAPI


class ChatAPI(BaseAPI):
    """Handle real-time chat between users and customer service"""
    
    def send_message(self):
        """Send a message in chat"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            user_email = user_info["user_email"]
            
            # Get message data
            data = request.get_json()
            conversation_id = data.get("conversation_id")
            message_content = data.get("message")
            message_type = data.get("type", "user")  # "user" or "agent"
            
            if not message_content:
                return jsonify({"error": True, "message": "Message content is required"}), 400
            
            # Insert message to database
            connection = self.get_connection()
            cursor = connection.cursor()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # If no conversation_id, create a new conversation
            if not conversation_id:
                cursor.execute(
                    """INSERT INTO conversations 
                       (user_id, user_email, created_at, updated_at) 
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, user_email, timestamp, timestamp)
                )
                connection.commit()
                conversation_id = cursor.lastrowid
            
            # Insert message
            cursor.execute(
                """INSERT INTO chat_messages 
                   (conversation_id, user_id, message, message_type, created_at) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (conversation_id, user_id, message_content, message_type, timestamp)
            )
            
            # Update conversation updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at=%s WHERE id=%s",
                (timestamp, conversation_id)
            )
            connection.commit()
            
            message_id = cursor.lastrowid
            
            return jsonify({
                "ok": True,
                "message_id": message_id,
                "conversation_id": conversation_id,
                "created_at": timestamp
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_conversation_history(self, conversation_id):
        """Get chat history for a conversation"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Verify user owns this conversation
            cursor.execute(
                "SELECT id FROM conversations WHERE id=%s AND user_id=%s",
                (conversation_id, user_id)
            )
            if not cursor.fetchone():
                return jsonify({"error": True, "message": "Conversation not found"}), 404
            
            # Get messages
            cursor.execute(
                """SELECT id, user_id, message, message_type, created_at, is_read 
                   FROM chat_messages 
                   WHERE conversation_id=%s 
                   ORDER BY created_at ASC""",
                (conversation_id,)
            )
            messages = cursor.fetchall()
            
            # Mark messages as read
            cursor.execute(
                "UPDATE chat_messages SET is_read=1 WHERE conversation_id=%s AND message_type='agent'",
                (conversation_id,)
            )
            connection.commit()
            
            return jsonify({
                "conversation_id": conversation_id,
                "messages": messages,
                "total": len(messages)
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_user_conversations(self):
        """Get all conversations for authenticated user"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            
            # Get pagination parameters
            page = int(request.args.get("page", 1))
            if page < 1:
                page = 1
            
            limit = 10
            offset = (page - 1) * limit
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get total count
            cursor.execute(
                "SELECT COUNT(*) as total FROM conversations WHERE user_id=%s",
                (user_id,)
            )
            total = cursor.fetchone()["total"]
            
            # Get conversations with latest message
            cursor.execute(
                """SELECT c.id, c.created_at, c.updated_at, 
                          (SELECT message FROM chat_messages WHERE conversation_id=c.id ORDER BY created_at DESC LIMIT 1) as last_message,
                          (SELECT COUNT(*) FROM chat_messages WHERE conversation_id=c.id AND is_read=0 AND message_type='agent') as unread_count
                   FROM conversations c 
                   WHERE c.user_id=%s 
                   ORDER BY c.updated_at DESC 
                   LIMIT %s OFFSET %s""",
                (user_id, limit, offset)
            )
            conversations = cursor.fetchall()
            
            return jsonify({
                "conversations": conversations,
                "page": page,
                "total": total,
                "pages": (total + limit - 1) // limit
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def get_unread_count(self):
        """Get count of unread messages for user"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """SELECT COUNT(*) as unread 
                   FROM chat_messages 
                   WHERE user_id=%s AND message_type='agent' AND is_read=0""",
                (user_id,)
            )
            result = cursor.fetchone()
            
            return jsonify({"unread_count": result["unread"]}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def mark_conversation_as_read(self, conversation_id):
        """Mark all messages in conversation as read"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Verify user owns this conversation
            cursor.execute(
                "SELECT id FROM conversations WHERE id=%s AND user_id=%s",
                (conversation_id, user_id)
            )
            if not cursor.fetchone():
                return jsonify({"error": True, "message": "Conversation not found"}), 404
            
            # Mark messages as read
            cursor.execute(
                "UPDATE chat_messages SET is_read=1 WHERE conversation_id=%s AND message_type='agent'",
                (conversation_id,)
            )
            connection.commit()
            
            return jsonify({"ok": True}), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
    
    def start_conversation(self):
        """Start a new conversation"""
        connection = None
        cursor = None
        try:
            # Get user info from token
            user_info = UserAPI.get_user_from_token()
            if not user_info:
                return jsonify({"error": True, "message": "Unauthorized"}), 401
            
            user_id = user_info["user_id"]
            user_email = user_info["user_email"]
            
            # Get optional subject
            data = request.get_json() or {}
            subject = data.get("subject", "New Conversation")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """INSERT INTO conversations 
                   (user_id, user_email, subject, created_at, updated_at) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, user_email, subject, timestamp, timestamp)
            )
            connection.commit()
            
            conversation_id = cursor.lastrowid
            
            return jsonify({
                "ok": True,
                "conversation_id": conversation_id,
                "created_at": timestamp
            }), 200
        
        except Exception as e:
            return jsonify({"error": True, "message": str(e)}), 500
        finally:
            self.close_cursor(cursor)
            self.close_connection(connection)
