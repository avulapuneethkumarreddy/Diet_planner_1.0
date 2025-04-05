from pymongo import MongoClient
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb+srv://tetraPack:DFpAB4rJTOl4GVow@tetrapack.bp5jdmc.mongodb.net/")  # Replace with your actual URI

# Access database and collection
db = client["test"]
user_collection = db["users"]  # Replace with actual collection name

def get_user_by_id(user_id):
    try:
        obj_id = ObjectId(user_id)  # Convert string to ObjectId
        user = user_collection.find_one({"_id": obj_id})
        if user:
            user["_id"] = str(user["_id"])  # Optional: make ObjectId readable
            return user
        else:
            return {"message": "User not found"}
    except Exception as e:
        return {"error": str(e)}

# Example usage
user_id = "67f0ffba413f441c8d2db49f"  # Replace with actual ObjectId
user_data = get_user_by_id(user_id)
print(user_data)


