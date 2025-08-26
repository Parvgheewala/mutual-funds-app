import asyncio
from database import AsyncSessionLocal
from models import Base


async def fetch_funds():
    async with AsyncSessionLocal() as session:
        # Access the reflected table
        Fund = Base.classes.funds  # reflected "funds" table

        result = await session.execute(Fund.__table__.select().limit(5))
        rows = result.fetchall()
        for row in rows:
            print(row)


if __name__ == "__main__":
    asyncio.run(fetch_funds())
