from motor.motor_asyncio import AsyncIOMotorClient


MONGODB_URL = "mongodb://localhost:27017"  # Change to your MongoDB connection URL
DATABASE_NAME = "users"             # Set your database name

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]