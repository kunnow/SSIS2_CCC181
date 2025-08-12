import mysql.connector
import os
import mimetypes
import cloudinary.uploader
from flask import current_app

extensions = {'.jpg', '.jpeg', '.png', '.gif'}
types = {'image/jpeg', 'image/png', 'image/gif'}

def get_students(offset, per_page):

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()
        
        cursor.execute("SELECT COUNT(*) AS total FROM student")
        total_students = cursor.fetchone()['total']

        query = """
            SELECT image_url, id, firstname, lastname, year, gender, course
            FROM student
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        students = cursor.fetchall()

        total_pages = (total_students + per_page - 1) // per_page
        return students, total_students, total_pages

    except mysql.connector.Error as err:
        return [], 0, 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def is_valid_image(file):
    
    """Check if the file is a valid image based on its extension and type."""
    _, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in extensions:
        raise ValueError("Invalid file type. Only JPG, JPEG, PNG, and GIF are allowed.")
    
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in types:
        raise ValueError("Invalid MIME type. Only image files are allowed.")
    
    return True

def add_student(image_url, student_id, first_name, last_name, year_level, gender, course):
    """Add a new student with image file constraints."""

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = """INSERT INTO student (image_url, id, firstname, lastname, year, gender, course) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (image_url, student_id, first_name, last_name, year_level, gender, course))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def update_student(image_url, first_name, last_name, year_level, gender, course, student_id):
    """Update student information."""

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = """UPDATE student 
                   SET image_url = %s, firstname = %s, lastname = %s, year = %s, gender = %s, course = %s 
                   WHERE id = %s"""
        cursor.execute(query, (image_url, first_name, last_name, year_level, gender, course, student_id))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def delete_student_by_id(student_id):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "DELETE FROM student WHERE id = %s"
        cursor.execute(query, (student_id,))
        connection.commit()

    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def get_student_by_id(student_id):
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        query = "SELECT * FROM student WHERE id = %s"
        cursor.execute(query, (student_id,))
        return cursor.fetchone()
    
    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def search_students(query, field, offset, per_page):
    """Search for students based on query and field."""

    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        sql_query = """
            SELECT * FROM student 
            WHERE LOWER(id) LIKE %s 
            OR LOWER(firstname) LIKE %s 
            OR LOWER(lastname) LIKE %s 
            OR year LIKE %s 
            OR LOWER(gender) LIKE %s 
            OR LOWER(course) LIKE %s
            LIMIT %s OFFSET %s
        """
        params = ('%' + query.lower() + '%',) * 6 + (per_page, offset)

        if field == "Student I.D.":
            sql_query = "SELECT * FROM student WHERE LOWER(id) LIKE %s LIMIT %s OFFSET %s"
            params = ('%' + query.lower() + '%', per_page, offset)
        elif field == "First Name":
            sql_query = "SELECT * FROM student WHERE LOWER(firstname) LIKE %s LIMIT %s OFFSET %s"
            params = ('%' + query.lower() + '%', per_page, offset)
        elif field == "Last Name":
            sql_query = "SELECT * FROM student WHERE LOWER(lastname) LIKE %s LIMIT %s OFFSET %s"
            params = ('%' + query.lower() + '%', per_page, offset)
        elif field == "Year Level":
            sql_query = "SELECT * FROM student WHERE year = %s LIMIT %s OFFSET %s"
            params = (query, per_page, offset)
        elif field == "Gender":
            sql_query = "SELECT * FROM student WHERE LOWER(gender) LIKE %s LIMIT %s OFFSET %s"
            params = ('%' + query.lower() + '%', per_page, offset)
        elif field == "Course":
            sql_query = "SELECT * FROM student WHERE LOWER(course) LIKE %s LIMIT %s OFFSET %s"
            params = ('%' + query.lower() + '%', per_page, offset)

        cursor.execute(sql_query, params)
        students = cursor.fetchall()

        return students
    except mysql.connector.Error as err:
        return [], str(err)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def count_students(query, field):
    """Count the number of students matching the search query and field."""
    
    connection = None
    cursor = None
    try:
        connection, cursor = get_db_connection()

        count_query = """
            SELECT COUNT(*) AS total FROM student 
            WHERE LOWER(id) LIKE %s 
            OR LOWER(firstname) LIKE %s
            OR LOWER(lastname) LIKE %s 
            OR year LIKE %s 
            OR LOWER(gender) LIKE %s 
            OR LOWER(course) LIKE %s
        """
        count_params = ('%' + query.lower() + '%',) * 6

        if field == "Student I.D.":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE LOWER(id) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "First Name":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE LOWER(firstname) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "Last Name":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE LOWER(lastname) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "Year Level":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE year = %s"
            count_params = (query,)
        elif field == "Gender":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE LOWER(gender) LIKE %s"
            count_params = ('%' + query.lower() + '%',)
        elif field == "Course":
            count_query = "SELECT COUNT(*) AS total FROM student WHERE LOWER(course) LIKE %s"
            count_params = ('%' + query.lower() + '%',)

        cursor.execute(count_query, count_params)
        total_students = cursor.fetchone()['total']
        return total_students
    except mysql.connector.Error as err:
        return 0
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def list_course_code():
    connection = None
    cursor = None

    try:
        connection, cursor = get_db_connection()

        cursor.execute("""
            SELECT DISTINCT code, name
            FROM program
            WHERE code IS NOT NULL
            ORDER BY code
        """)

        results = cursor.fetchall()

        return [(row['code'], row['name']) for row in results]
    
    except Exception as e:
        print(f"Error fetching course codes: {e}")
        return []
    
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
 