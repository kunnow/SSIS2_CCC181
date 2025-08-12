import mysql.connector
from flask import current_app

def get_programs(offset, per_page):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        cursor.execute("SELECT COUNT(*) AS total FROM program")
        total_programs = cursor.fetchone()['total']
        total_pages = (total_programs + per_page - 1) // per_page

        query = """
            SELECT code, name, college_code
            FROM program
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        programs = cursor.fetchall()

        return programs, total_programs, total_pages

    except mysql.connector.Error as err:
        return [], 0, 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def add_program(course_code, course_name, college_code):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "INSERT INTO program (code, name, college_code) VALUES (%s, %s, %s)"
        cursor.execute(query, (course_code, course_name, college_code))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def update_program(course_code, course_name, college_code, original_course_code):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "SELECT COUNT(*) FROM program WHERE code = %s AND code != %s"
        cursor.execute(query, (course_code, original_course_code))
        count = cursor.fetchone()['COUNT(*)']

        if count > 0:
            raise ValueError("Course code must be unique.")
        
        query = "UPDATE program SET code = %s, name = %s, college_code = %s WHERE code = %s"
        cursor.execute(query, (course_code, course_name, college_code, original_course_code))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def delete_program(course_code):

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "DELETE FROM program WHERE code = %s"
        cursor.execute(query, (course_code,))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def check_college_exists(college_code):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "SELECT COUNT(*) FROM college WHERE code = %s"
        cursor.execute(query, (college_code,))
        return cursor.fetchone()['COUNT(*)'] > 0

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def search_programs(query, field, offset, per_page):
    """Search for programs based on query and field."""
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        if field == "Course Code":
            sql_query = "SELECT * FROM program WHERE LOWER(code) LIKE %s"
            params = ('%' + query.lower() + '%',)
        elif field == "Course Name":
            sql_query = "SELECT * FROM program WHERE LOWER(name) LIKE %s"
            params = ('%' + query.lower() + '%',)
        elif field == "College Code":
            sql_query = "SELECT * FROM program WHERE LOWER(college_code) LIKE %s"
            params = ('%' + query.lower() + '%',)
        else:
            sql_query = """
                SELECT * FROM program 
                WHERE LOWER(code) LIKE %s 
                OR LOWER(name) LIKE %s
                OR LOWER(college_code) LIKE %s
            """
            params = ('%' + query.lower() + '%',) * 3

        sql_query += " LIMIT %s OFFSET %s"
        cursor.execute(sql_query, params + (per_page, offset))
        programs = cursor.fetchall()

        return programs
    except mysql.connector.Error as err:
        return [], str(err)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def count_programs(query, field):
    """Count the number of programs matching the search query and field."""
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        if field == "Course Code":
            count_query = "SELECT COUNT(*) AS total FROM program WHERE LOWER(code) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "Course Name":
            count_query = "SELECT COUNT(*) AS total FROM program WHERE LOWER(name) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "College Code":
            count_query = "SELECT COUNT(*) AS total FROM program WHERE LOWER(college_code) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        else:
            count_query = """
                SELECT COUNT(*) AS total FROM program 
                WHERE LOWER(code) LIKE %s 
                OR LOWER(name) LIKE %s
                OR LOWER(college_code) LIKE %s
            """
            count_params = ('%' + query.lower() + '%',) * 3

        cursor.execute(count_query, count_params)
        total_programs = cursor.fetchone()['total']
        return total_programs
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

