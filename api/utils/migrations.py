"""Database migrations for Chat functionality"""

# SQL to create the chat tables
CREATE_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    status ENUM('open', 'closed', 'waiting') DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assigned_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
)
"""

CREATE_CHAT_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    user_id INT NOT NULL,
    message LONGTEXT NOT NULL,
    message_type ENUM('user', 'agent') DEFAULT 'user',
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
)
"""

# SQL to add admin role to users table
ADD_ROLE_TO_USERS = """
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role ENUM('user', 'admin', 'super_admin') DEFAULT 'user',
ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD INDEX IF NOT EXISTS idx_role (role)
"""

# SQL to add status to products table
ADD_STATUS_TO_PRODUCTS = """
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS status ENUM('pending', 'published', 'rejected') DEFAULT 'published',
ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD INDEX IF NOT EXISTS idx_status (status),
ADD INDEX IF NOT EXISTS idx_created_at (created_at)
"""

# SQL to add unique indexed composite key for product uploads
# This enforces that (partnumber, upload_user, dc) must be unique
# to support insert/update logic based on part number, supplier, and date code
ADD_UNIQUE_PRODUCT_KEY = """
ALTER TABLE products 
ADD UNIQUE INDEX IF NOT EXISTS idx_unique_product (partnumber, upload_user, dc)
"""

# SQL to convert price column to JSON for tiered pricing support
# Tiered pricing format: [{"quantity": 1, "price": 100}, {"quantity": 5, "price": 95}, ...]
CONVERT_PRICE_TO_JSON = """
ALTER TABLE products 
MODIFY COLUMN price JSON COMMENT 'JSON array of tiered pricing: [{"quantity": N, "price": X}, ...]'
"""

# Python function to initialize chat tables
def init_chat_tables():
    """Initialize chat-related database tables"""
    from api.utils import DatabaseManager
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    try:
        print("Creating conversations table...")
        cursor.execute(CREATE_CONVERSATIONS_TABLE)
        print("✓ conversations table created")
        
        print("Creating chat_messages table...")
        cursor.execute(CREATE_CHAT_MESSAGES_TABLE)
        print("✓ chat_messages table created")
        
        connection.commit()
        print("✓ All chat tables initialized successfully")
    
    except Exception as e:
        print(f"✗ Error creating chat tables: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def add_role_to_users():
    """Add role column to users table"""
    from api.utils import DatabaseManager
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    try:
        print("Adding role column to users table...")
        cursor.execute(ADD_ROLE_TO_USERS)
        connection.commit()
        print("✓ Role column added to users table")
    
    except Exception as e:
        print(f"✗ Error adding role column: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def add_status_to_products():
    """Add status column to products table"""
    from api.utils import DatabaseManager
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    try:
        print("Adding status column to products table...")
        cursor.execute(ADD_STATUS_TO_PRODUCTS)
        connection.commit()
        print("✓ Status column added to products table")
    
    except Exception as e:
        print(f"✗ Error adding status column: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def add_unique_product_key():
    """Add unique composite index (partnumber, upload_user, dc) to products table"""
    from api.utils import DatabaseManager
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    try:
        print("Adding unique composite index to products table...")
        cursor.execute(ADD_UNIQUE_PRODUCT_KEY)
        connection.commit()
        print("✓ Unique composite index (partnumber, upload_user, dc) added to products table")
        print("  This enables automatic update when same part number, supplier, and date code are uploaded")
    
    except Exception as e:
        print(f"✗ Error adding unique composite index: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def convert_price_to_json():
    """Convert price column from DECIMAL to JSON to support tiered pricing
    
    Tiered pricing format: [{"quantity": 1, "price": 100}, {"quantity": 5, "price": 95}, ...]
    Existing price values will be wrapped in this format during conversion.
    """
    from api.utils import DatabaseManager
    import json
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        print("Converting price column to JSON format for tiered pricing...")
        
        # First, get all existing price values
        cursor.execute("SELECT id, price FROM products WHERE price IS NOT NULL")
        products = cursor.fetchall()
        
        # Convert price column to JSON
        cursor.execute(CONVERT_PRICE_TO_JSON)
        connection.commit()
        print("✓ Price column converted to JSON type")
        
        # Migrate existing price values to tiered format
        # Each single price becomes [{"quantity": 1, "price": X}]
        if products:
            print(f"  Converting {len(products)} existing price records to tiered format...")
            for product in products:
                if product["price"]:
                    try:
                        # Try to parse as float
                        price_val = float(product["price"])
                        # Wrap in tiered format
                        tiered_price = json.dumps([{"quantity": 1, "price": price_val}])
                        cursor.execute(
                            "UPDATE products SET price = %s WHERE id = %s",
                            (tiered_price, product["id"])
                        )
                    except (ValueError, TypeError):
                        print(f"  ⚠ Warning: Could not convert price for product id {product['id']}: {product['price']}")
            connection.commit()
            print(f"✓ Migrated {len(products)} existing price records")
        
        print("✓ Tiered pricing support enabled")
        print("  Format: [{'quantity': 1, 'price': 100}, {'quantity': 5, 'price': 95}, ...]")
    
    except Exception as e:
        print(f"✗ Error converting price column to JSON: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def init_all():
    """Initialize all migrations"""
    print("=" * 50)
    print("Starting database migrations...")
    print("=" * 50)
    
    init_chat_tables()
    add_role_to_users()
    add_status_to_products()
    add_unique_product_key()
    convert_price_to_json()
    
    print("=" * 50)
    print("✓ All migrations completed successfully!")
    print("=" * 50)
