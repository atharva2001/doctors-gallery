async def insert_data(db, collection, data):
    try:
        # print(db, collection, data)
        if await db[collection].find_one({"id": data["id"]}):
            return "Data already exists!"
            
        result = await db[collection].insert_one(data)
        print(result)
        return {"message": "success"}
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise e
    
async def update_data(db, collection, data):
    try:
        # print(db, collection, data)
        result = await db[collection].update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        print(result)
        return {"message": "success"}
    except Exception as e:
        print(f"Error updating data: {e}")
        raise e
    
async def delete_data(db, collection, data):
    try:
        # print(db, collection, data)
        result = await db[collection].delete_one(
            {"id": data["id"]},
        )
        print(result)
        return {"message": "success"}
    except Exception as e:
        print(f"Error deleting data: {e}")
        raise e