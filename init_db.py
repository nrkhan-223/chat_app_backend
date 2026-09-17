"""
Database migration utilities using Alembic-compatible approach.
Run this script to create initial tables or reset the database.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, create_tables
from models import *  # noqa: F401, F403 - Import all models to register them


async def main():
    """Create all database tables."""
    print("🔄 Creating database tables...")
    await create_tables()
    print("✅ All tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - channels")
    print("  - channel_members")
    print("  - messages")
    print("  - attachments")
    print("  - reactions")


if __name__ == "__main__":
    asyncio.run(main())
