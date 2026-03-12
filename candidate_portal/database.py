import sqlite3

DB_PATH = 'portal.db'

def get_connection():
    """Get database connection with row factory for named column access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This lets you access columns by name
    return conn
      
def create_tables():
    """Create all necessary tables if they don't exist"""
    conn = get_connection()
    
    # Create candidates table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            skills TEXT,
            experience_years INTEGER,
            location TEXT,
            resume_filename TEXT
        )
    ''')
    
    # Create recruiters table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recruiters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

def init_recruiter():
    """Initialize a default recruiter account (run once)"""
    from werkzeug.security import generate_password_hash
    
    conn = get_connection()
    
    # Check if recruiters table is empty
    cursor = conn.execute("SELECT COUNT(*) as count FROM recruiters")
    count = cursor.fetchone()['count']
    
    if count == 0:
        # Create a default recruiter account
        hashed_password = generate_password_hash('recruiter123')
        conn.execute(
            "INSERT INTO recruiters (email, password) VALUES (?, ?)",
            ('recruiter@example.com', hashed_password)
        )
        conn.commit()
        print("Default recruiter account created: recruiter@example.com / recruiter123")
    
    conn.close()

if __name__ == '__main__':
    create_tables()
    init_recruiter()