# scripts/check_data.py
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import connect_to_db, disconnect_from_db, engine
from sqlalchemy import text

async def check_data_quality():
    """Check NAV data using direct SQL queries"""
    try:
        print("🚀 Starting data quality check...")
        print("🔄 Connecting to database...")
        await connect_to_db()
        print("✅ Database connected successfully")
        
        async with engine.connect() as conn:
            # Check if table exists
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'fund_navs'
            """))
            tables = result.fetchall()
            
            if not tables:
                print("❌ fund_navs table not found! Run ingest_navs.py first")
                return
            
            print("✅ fund_navs table exists")
            
            # Count total records
            result = await conn.execute(text("SELECT COUNT(*) FROM fund_navs"))
            total_records = result.scalar()
            print(f"📊 Total NAV records: {total_records}")
            
            if total_records == 0:
                print("❌ No NAV records found! Run ingest_navs.py first")
                return
            
            # Count unique funds
            result = await conn.execute(text("SELECT COUNT(DISTINCT fund_id) FROM fund_navs"))
            unique_funds = result.scalar()
            print(f"🏛️  Unique funds: {unique_funds}")
            
            # Check date range
            result = await conn.execute(text("""
                SELECT MIN(date) as earliest, MAX(date) as latest 
                FROM fund_navs
            """))
            date_range = result.fetchone()
            if date_range:
                print(f"📅 Date range: {date_range.earliest} to {date_range.latest}")
            
            # Sample recent data
            print("\n📝 Sample recent NAV records:")
            result = await conn.execute(text("""
                SELECT fund_id, date, nav, 
                       COALESCE(scheme_name, 'N/A') as scheme_name
                FROM fund_navs 
                ORDER BY date DESC 
                LIMIT 5
            """))
            samples = result.fetchall()
            
            for row in samples:
                scheme_name = row.scheme_name[:50] + "..." if len(row.scheme_name) > 50 else row.scheme_name
                print(f"  {row.fund_id}: {row.date} -> NAV: {row.nav} ({scheme_name})")
            
            # Check data quality
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM fund_navs 
                WHERE scheme_name IS NULL OR scheme_name = ''
            """))
            missing_names = result.scalar()
            print(f"⚠️  Records without scheme names: {missing_names}")
            
            print("\n✅ Data quality check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data check: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await disconnect_from_db()
        print("🔌 Database disconnected")

if __name__ == "__main__":
    asyncio.run(check_data_quality())
    print("🏁 Check completed")
