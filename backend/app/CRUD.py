from .database import db
from bson.objectid import ObjectId

async def create_user(user_data):
    user_dict = user_data.dict()
    result = await db["users"].insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return user_dict

async def create_mutualfund(mf_data):
    mf_dict = mf_data.dict()
    result = await db["mutual_funds"].insert_one(mf_dict)
    mf_dict["id"] = str(result.inserted_id)
    return mf_dict

# Add similar functions for getting, updating, deleting documents as needed
async def get_user_by_email(email: str):
    user = await db["users"].find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
    return user