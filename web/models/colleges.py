import mysql.connector
from flask import current_app

def get_colleges(offset, per_page):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        cursor.execute("SELECT COUNT(*) AS total FROM college")
        total_colleges = cursor.fetchone()['total']

        query = """
            SELECT code, name
            FROM college
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        colleges = cursor.fetchall()

        total_pages = (total_colleges + per_page - 1) // per_page
        return colleges, total_colleges, total_pages

    except mysql.connector.Error as err:
        return [], 0, 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def add_college(college_code, college_name):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "SELECT COUNT(*) FROM college WHERE code = %s"
        cursor.execute(query, (college_code,))
        count = cursor.fetchone()['COUNT(*)']

        if count > 0:
            raise ValueError("College code already exists. Please choose a different code.")
        
        query = "INSERT INTO college (code, name) VALUES (%s, %s)"
        cursor.execute(query, (college_code, college_name))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def update_college(college_code, college_name, original_college_code):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "SELECT COUNT(*) FROM college WHERE code = %s AND code != %s"
        cursor.execute(query, (college_code, original_college_code))
        count = cursor.fetchone()['COUNT(*)']

        if count > 0:
            raise ValueError("Another college with the same code already exists.")
        
        query = "UPDATE college SET code = %s, name = %s WHERE code = %s"
        cursor.execute(query, (college_code, college_name, original_college_code))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def delete_college(college_code):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "DELETE FROM college WHERE code = %s"
        cursor.execute(query, (college_code,))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def search_colleges(query, field, offset, per_page):
    """Search for colleges based on query and field."""

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        if field == "College Code":
            sql_query = "SELECT * FROM college WHERE LOWER(code) LIKE %s"
            params = ('%' + query.lower() + '%',)
        elif field == "College Name":
            sql_query = "SELECT * FROM college WHERE LOWER(name) LIKE %s"
            params = ('%' + query.lower() + '%',)
        else:
            sql_query = """
                SELECT * FROM college 
                WHERE LOWER(code) LIKE %s 
                OR LOWER(name) LIKE %s
            """
            params = ('%' + query.lower() + '%',) * 2

        sql_query += " LIMIT %s OFFSET %s"
        cursor.execute(sql_query, params + (per_page, offset))
        colleges = cursor.fetchall()

        return colleges
    except mysql.connector.Error as err:
        return [], str(err)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def count_colleges(query, field):
    """Count the number of colleges matching the search query and field."""

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        if field == "College Code":
            count_query = "SELECT COUNT(*) AS total FROM college WHERE LOWER(code) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "College Name":
            count_query = "SELECT COUNT(*) AS total FROM college WHERE LOWER(name) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        else:
            count_query = """
                SELECT COUNT(*) AS total FROM college 
                WHERE LOWER(code) LIKE %s 
                OR LOWER(name) LIKE %s
            """
            count_params = ('%' + query.lower() + '%',) * 2

        cursor.execute(count_query, count_params)
        total_colleges = cursor.fetchone()['total']
        return total_colleges
    except mysql.connector.Error as err:
        return 0
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def get_db_connection():
    """Helper function to establish and return a database connection and cursor."""
    connection = mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB']
    )
    cursor = connection.cursor(dictionary=True)
    return connection, cursor