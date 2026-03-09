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

def init_all():
    """Initialize all migrations"""
    print("=" * 50)
    print("Starting database migrations...")
    print("=" * 50)
    
    init_chat_tables()
    add_role_to_users()
    add_status_to_products()
    
    print("=" * 50)
    print("✓ All migrations completed successfully!")
    print("=" * 50)
