"""Contact API Handler"""
import requests
import os
from flask import jsonify, request
from dotenv import load_dotenv
from api.utils import BaseAPI

load_dotenv()


class ContactAPI(BaseAPI):
    """Handle contact/feedback messages"""
    
    def send_message(self):
        """Send feedback message via Discord webhook"""
        try:
            webhook_url = os.getenv("dc_url")
            data = request.get_json()
            
            if not webhook_url:
                return jsonify({"error": True, "message": "Webhook URL not configured"}), 500
            
            content = data.get("content")
            
            if not content:
                return jsonify({"error": True, "message": "Message content is required"}), 400
            
            headers = {'Content-Type': 'application/json'}
            output = {"content": content}
            
            response = requests.post(webhook_url, json=output, headers=headers)
            
            if response.status_code == 204:
                return jsonify({"message": "feedback send successfully"}), 200
            else:
                return jsonify({"error": True, "message": "Failed to send feedback"}), 500
        
        except Exception as e:
            return jsonify({"message": f"fail to give feedback {str(e)}"}), 500
