"""
Main Flask application with refactored API structure
This application uses object-oriented design with separate classes for different domains
"""
from flask import Flask, request, render_template
import os
from dotenv import load_dotenv

# Import API modules
from api.modules import (
    PageAPI,
    CategoryAPI,
    UserAPI,
    ProductSearchAPI,
    ProductManagementAPI,
    UploadHistoryAPI,
    ContactAPI,
    ChatAPI,
    AdminAPI
)

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSONIFY_MIMETYPE"] = 'application/json; charset=utf-8'
app.config['JSON_SORT_KEYS'] = False

# Initialize API handlers
page_api = PageAPI()
category_api = CategoryAPI()
user_api = UserAPI()
product_search_api = ProductSearchAPI()
product_management_api = ProductManagementAPI()
upload_history_api = UploadHistoryAPI()
contact_api = ContactAPI()
chat_api = ChatAPI()
admin_api = AdminAPI()


# ========================
# PAGE ROUTES
# ========================
@app.route("/")
def index():
    return page_api.index()

@app.route("/bom")
def bom():
    return page_api.bom()

@app.route("/category/<category_name>")
def category(category_name):
    return page_api.category(category_name)

@app.route("/brand")
def brand():
    return page_api.brand()

@app.route("/contact")
def contact():
    return page_api.contact()

@app.route("/faq")
def faq():
    return page_api.faq()

@app.route("/search/<partnumber>")
def product(partnumber):
    return page_api.product(partnumber)

@app.route("/upload")
def upload():
    return page_api.upload()

@app.route("/introduction")
def introduction():
    return page_api.introduction()

@app.route("/chat")
def chat():
    """聊天頁面"""
    return render_template("chat.html")

@app.route("/admin")
def admin():
    """後台管理頁面"""
    return render_template("admin.html")


# ========================
# CATEGORY OPERATIONS
# ========================
@app.route("/api/showcategories", methods=["GET"])
def show_categories():
    """Get all product categories"""
    return category_api.get_categories()

@app.route("/api/manufacturer", methods=["GET"])
def get_manufacturers():
    """Get all manufacturers/brands"""
    return category_api.get_manufacturers()


# ========================
# USER OPERATIONS
# ========================
@app.route("/api/user", methods=["POST"])
def register():
    """Register a new user"""
    return user_api.register()

@app.route("/api/user/auth", methods=["PUT", "GET"])
def user_auth():
    """User authentication - login (PUT) or verify token (GET)"""
    if request.method == "PUT":
        return user_api.login()
    else:  # GET
        return user_api.verify_token()


# ========================
# PRODUCT SEARCH
# ========================
@app.route("/api/search/<product>", methods=["GET"])
def search_products(product):
    """Search products by part number"""
    return product_search_api.search_products(product)


# ========================
# PRODUCT MANAGEMENT (Upload, Edit, Delete)
# ========================
@app.route("/api/uploadone", methods=["POST"])
def upload_single():
    """Upload a single product"""
    return product_management_api.upload_single_product()

@app.route("/api/editproduct", methods=["PUT"])
def edit_product():
    """Edit product details"""
    return product_management_api.edit_product()

@app.route("/api/deleteproduct", methods=["DELETE"])
def delete_product():
    """Delete a product"""
    return product_management_api.delete_product()


# ========================
# UPLOAD HISTORY & BATCH UPLOAD
# ========================
@app.route("/api/uploadhistory", methods=["GET"])
def get_upload_history():
    """Get user's upload history"""
    return upload_history_api.get_upload_history()

@app.route("/api/batchupload", methods=["POST"])
def batch_upload():
    """Upload multiple products from Excel file"""
    return upload_history_api.batch_upload()


# ========================
# CONTACT & FEEDBACK
# ========================
@app.route("/api/contact", methods=["POST"])
def send_contact_message():
    """Send contact/feedback message"""
    return contact_api.send_message()


# ========================
# CHAT & CUSTOMER SERVICE
# ========================
@app.route("/api/chat/start", methods=["POST"])
def start_chat_conversation():
    """Start a new conversation with customer service"""
    return chat_api.start_conversation()

@app.route("/api/chat/send", methods=["POST"])
def send_chat_message():
    """Send a message in chat"""
    return chat_api.send_message()

@app.route("/api/chat/conversations", methods=["GET"])
def get_chat_conversations():
    """Get all conversations for user"""
    return chat_api.get_user_conversations()

@app.route("/api/chat/conversation/<int:conversation_id>", methods=["GET"])
def get_chat_history(conversation_id):
    """Get chat history for a specific conversation"""
    return chat_api.get_conversation_history(conversation_id)

@app.route("/api/chat/conversation/<int:conversation_id>/read", methods=["PUT"])
def mark_chat_as_read(conversation_id):
    """Mark conversation as read"""
    return chat_api.mark_conversation_as_read(conversation_id)

@app.route("/api/chat/unread", methods=["GET"])
def get_chat_unread():
    """Get count of unread messages"""
    return chat_api.get_unread_count()


# ========================
# ADMIN OPERATIONS
# ========================

# ---- User Management ----
@app.route("/api/admin/users", methods=["GET"])
def get_all_users():
    """Get all users (admin only)"""
    return admin_api.get_all_users()

@app.route("/api/admin/users/<int:user_id>", methods=["GET"])
def get_user_detail(user_id):
    """Get specific user details (admin only)"""
    return admin_api.get_user_detail(user_id)

@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
def edit_user_info(user_id):
    """Edit user information (admin only)"""
    return admin_api.edit_user(user_id)

@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user_account(user_id):
    """Delete user account (super admin only)"""
    return admin_api.delete_user(user_id)

@app.route("/api/admin/users/<int:user_id>/role", methods=["PUT"])
def set_user_role(user_id):
    """Set user role (super admin only)"""
    return admin_api.set_user_role(user_id)

# ---- Product Management ----
@app.route("/api/admin/products", methods=["GET"])
def get_all_products():
    """Get all products (admin only)"""
    return admin_api.get_all_products()

@app.route("/api/admin/products/<int:product_id>", methods=["GET"])
def get_product_detail(product_id):
    """Get specific product details (admin only)"""
    return admin_api.get_product_detail(product_id)

@app.route("/api/admin/products/<int:product_id>", methods=["PUT"])
def edit_product_info(product_id):
    """Edit product information (admin only)"""
    return admin_api.edit_product(product_id)

@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def delete_product_item(product_id):
    """Delete product (admin only)"""
    return admin_api.delete_product(product_id)

@app.route("/api/admin/products/<int:product_id>/approve", methods=["PUT"])
def approve_product_item(product_id):
    """Approve/publish product (admin only)"""
    return admin_api.approve_product(product_id)

@app.route("/api/admin/products/<int:product_id>/reject", methods=["PUT"])
def reject_product_item(product_id):
    """Reject product (admin only)"""
    return admin_api.reject_product(product_id)

# ---- Admin Dashboard ----
@app.route("/api/admin/statistics", methods=["GET"])
def get_admin_statistics():
    """Get admin dashboard statistics (admin only)"""
    return admin_api.get_statistics()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
