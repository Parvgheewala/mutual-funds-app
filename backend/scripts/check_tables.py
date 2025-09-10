# scripts/check_tables.py
import asyncio
from app.database import connect_to_db, disconnect_from_db, engine
from sqlalchemy import text

async def check_all_tables():
    await connect_to_db()
    async with engine.connect() as conn:
        # List all tables
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()
        print("Existing tables:")
        for table in tables:
            print(f"  - {table.table_name}")
    await disconnect_from_db()

asyncio.run(check_all_tables())
