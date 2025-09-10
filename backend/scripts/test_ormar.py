import asyncio
from datetime import date
from app.database import connect_to_db, disconnect_from_db
from app.models import FundNav

async def test():
    print("Connecting to DB...")
    await connect_to_db()
    print("Connected.")

    fund_id = "TEST123"
    d = date.today()

    print("Upserting FundNav...")
    obj, created = await FundNav.objects.get_or_create(
        fund_id=fund_id,
        date=d,
        _defaults={
            "nav": 100.0,
            "aum": 5000000.0,
            "scheme_name": "Test Fund",
            "category": "Equity",
            "source": "api.mfapi.in",
        },
    )
    if not created:
        await obj.update(nav=100.0, aum=5000000.0, scheme_name="Test Fund", category="Equity")
    print(f"{'Created' if created else 'Updated'} FundNav.")

    retrieved = await FundNav.objects.get(fund_id=fund_id, date=d)
    print(f"Retrieved FundNav: fund_id={retrieved.fund_id}, nav={retrieved.nav}")

    await disconnect_from_db()
    print("Disconnected DB.")

if __name__ == "__main__":
    asyncio.run(test())
