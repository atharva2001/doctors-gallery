async def get_user_by_id(cursor, id):
    query = """
    SELECT * FROM users
    WHERE id = %s;
    """
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    if result:
        return dict(zip(columns, result)) 
    else:
        return {"error": "User not found."}

async def get_all_users(cursor):
    query = """
    SELECT * FROM users;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result
    else:
        return {"error": "No users found."}



async def delete_user(cursor, id):
    query = """
    DELETE FROM users
    WHERE id = %s;
    """
    try:
        cursor.execute(query, (id,))
        cursor.connection.commit()
        return {"message": "User deleted successfully."}
    except Exception as e:
        cursor.connection.rollback()
        return {"error": str(e)}
    finally:
        cursor.close()


async def get_user_by_email(cursor, email):
    query = """
    SELECT * FROM users
    WHERE email = %s;
    """
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result
    else:
        return {"error": "User not found."}