async def create_user(cursor, user):
    query = """
    INSERT INTO users (username, email, password, role)
    values (%s, %s, %s, %s);
    """
    try:
        cursor.execute(query, (user.username, user.email, user.password, user.role))
        cursor.connection.commit()
        return {"message": "User created successfully."}
    except Exception as e:
        cursor.connection.rollback()
        return {"error": str(e)}
    finally:
        cursor.close()