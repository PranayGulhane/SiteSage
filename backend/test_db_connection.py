
#!/usr/bin/env python3
"""Test database connection."""
import os
from sqlalchemy import create_engine, text

def test_connection():
    """Test the database connection."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        print("Please set it in Replit Secrets or .env file")
        return False
    
    print(f"Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'database'}")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Check if DATABASE_URL is correct")
        print("2. Ensure PostgreSQL is running")
        print("3. Check database permissions")
        print("4. Verify network/firewall settings")
        return False

if __name__ == "__main__":
    test_connection()
