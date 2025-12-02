"""
Test PostgreSQL Database Connection
This script helps you verify your database connection settings.
"""

import psycopg2
from psycopg2 import sql
import sys

def test_connection(host='localhost', port=5432, database='MyPortalDb', user='postgres', password='rahul'):
    """Test PostgreSQL connection with given credentials."""
    print("=" * 60)
    print("PostgreSQL Connection Test")
    print("=" * 60)
    print(f"\nAttempting to connect to:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {database}")
    print(f"  User: {user}")
    print(f"  Password: {'*' * len(password)}")
    print("\n")
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("✓ Connection successful!")
        
        # Get PostgreSQL version
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\nPostgreSQL Version: {version.split(',')[0]}")
        
        # Check if database exists and list tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"\n✓ Found {len(tables)} existing tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n✓ Database is empty (no tables yet)")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Connection test PASSED!")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ Connection failed!")
        print(f"  Error: {str(e)}")
        print("\nPlease check:")
        print("  1. PostgreSQL server is running")
        print("  2. Database 'MyPortalDb' exists (create it in pgAdmin if needed)")
        print("  3. Username and password are correct")
        print("  4. Host and port are correct")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    # Try to load from .env file first
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Get values from environment or use defaults
    host = os.getenv('DATABASE_HOST', 'localhost')
    port = int(os.getenv('DATABASE_PORT', '5432'))
    database = os.getenv('DATABASE_NAME', 'MyPortalDb')
    user = os.getenv('DATABASE_USER', 'postgres')
    password = os.getenv('DATABASE_PASSWORD', 'postgres')
    
    # Allow command line override
    import argparse
    parser = argparse.ArgumentParser(description='Test PostgreSQL connection')
    parser.add_argument('--host', default=host, help='Database host')
    parser.add_argument('--port', type=int, default=port, help='Database port')
    parser.add_argument('--database', default=database, help='Database name')
    parser.add_argument('--user', default=user, help='Database user')
    parser.add_argument('--password', default=password, help='Database password')
    
    args = parser.parse_args()
    
    success = test_connection(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    
    if not success:
        print("\n💡 Tip: Create a .env file with your credentials:")
        print("   DATABASE_USER=postgres")
        print("   DATABASE_PASSWORD=your_password")
        print("   DATABASE_HOST=localhost")
        print("   DATABASE_PORT=5432")
        print("   DATABASE_NAME=MyPortalDb")
    
    sys.exit(0 if success else 1)

