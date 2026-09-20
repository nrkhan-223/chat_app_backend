"""
Database initialization script.
Run this to create all database tables.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.models import *  # noqa: F401, F403


async def main():
    """Initialize the database."""
    print("🔄 Initializing database...")
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - channels")
        print("  - channel_members")
        print("  - messages")
        print("  - attachments")
        print("  - reactions")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'chatapp' exists")
        print("  3. DATABASE_URL in .env is correct")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
