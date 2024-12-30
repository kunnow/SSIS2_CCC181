'''
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import mysql.connector
import cloudinary.uploader

views = Blueprint('views', __name__)

@views.route("/")
def sidebar():
    return render_template('base.html')

@views.route('/students', endpoint='students', methods=['GET', 'POST'])
def students():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    students = []

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) AS total FROM student")
        total_students = cursor.fetchone()['total']

        query = """
            SELECT id, firstname, lastname, year, gender, course
            FROM student
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        students = cursor.fetchall()

        total_pages = (total_students + per_page - 1) // per_page

    except mysql.connector.Error as err:
        flash(f"Error: {err}", category='danger')
        total_pages = 1

    finally:
        cursor.close()
        connection.close()

    if request.method == 'POST':
        image = request.files.get('image')
        student_id = request.form.get('id')
        firstName = request.form.get('firstname')
        lastName = request.form.get('lastname')
        yearLevel = request.form.get('year')
        gender = request.form.get('gender')
        course = request.form.get('course')
        action = request.form.get('action')

        if len(firstName) == 0:
            flash('Invalid first name.', category='danger')
        elif len(lastName) == 0:
            flash('Invalid last name.', category='danger')
        elif not yearLevel.isdigit() or int(yearLevel) not in range(1, 5):
            flash('Invalid Year Level. Must be between 1 and 4.', category='danger')
        else:
            try:
                connection = mysql.connector.connect(
                    host=current_app.config['MYSQL_HOST'],
                    user=current_app.config['MYSQL_USER'],
                    password=current_app.config['MYSQL_PASSWORD'],
                    database=current_app.config['MYSQL_DB']
                )
                cursor = connection.cursor()

                image_url = None
                if image:
                    upload_result = cloudinary.uploader.upload(image)
                    image_url = upload_result.get("url")

                if action == "add":
                    cursor.execute("SELECT * FROM student WHERE id = %s", (student_id,))
                    existing_student = cursor.fetchone()
                    if existing_student:
                        flash('Student ID already exists. Please use a different ID.', category='danger')
                    else:
                        query = """INSERT INTO student (image_url, id, firstname, lastname, year, gender, course) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (image_url, student_id, firstName, lastName, yearLevel, gender, course))
                        flash('Student added successfully.', category='success')

                elif action == "edit":
                    query = """UPDATE student 
                               SET image_url = %s, firstname = %s, lastname = %s, year = %s, gender = %s, course = %s 
                               WHERE id = %s"""
                    cursor.execute(query, (image_url, firstName, lastName, yearLevel, gender, course, student_id))
                    flash('Student updated successfully.', category='success')

                connection.commit()

            except mysql.connector.Error as err:
                flash(f"Error: {err}", category='danger')

            finally:
                cursor.close()
                connection.close()

    return render_template('students.html', students=students,page=page,total_pages=total_pages)

#rawr done
@views.route('/students/delete/<student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        query = "DELETE FROM student WHERE id = %s"
        cursor.execute(query, (student_id,))
        connection.commit()
        flash('Student deleted successfully.', category='success')

    except mysql.connector.Error as err:
        flash(f"Error: {err}", category='danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('views.students'))  

@views.route('/programs', methods=['GET', 'POST'])
def programs():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    programs = []

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)

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

        if request.method == 'POST':
            action = request.form.get('action')
            course_code = request.form.get('courseCode')
            course_name = request.form.get('courseName')
            college_code = request.form.get('collegeCode')
            original_course_code = request.form.get('originalCourseCode')

            if len(course_code) == 0 or len(course_name) == 0 or len(college_code) == 0:
                flash('All fields are required.', category='danger')
            else:
                cursor.execute("SELECT COUNT(*) FROM college WHERE code = %s", (college_code,))
                college_exists = cursor.fetchone()['COUNT(*)'] > 0

                if not college_exists:
                    flash('The College Code does not exist.', category='danger')
                else:
                    if action == 'add':
                        try:
                            query = "INSERT INTO program (code, name, college_code) VALUES (%s, %s, %s)"
                            cursor.execute(query, (course_code, course_name, college_code))
                            connection.commit()
                            flash('Program added successfully!', category='success')
                        except mysql.connector.Error as err:
                            flash('Program already exists. Please choose a different code.', category='danger')

                    elif action == 'edit':
                        try:
                            query = "SELECT COUNT(*) FROM program WHERE code = %s AND code != %s"
                            cursor.execute(query, (course_code, original_course_code))
                            count = cursor.fetchone()['COUNT(*)']

                            if count > 0:
                                flash('Course code must be unique.', category='danger')
                            else:
                                query = "UPDATE program SET code = %s, name = %s, college_code = %s WHERE code = %s"
                                cursor.execute(query, (course_code, course_name, college_code, original_course_code))
                                connection.commit()
                                flash('Program updated successfully!', category='success')
                        except mysql.connector.Error as err:
                            flash(f"Error updating program: {err}", category='danger')

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", category='danger')
        total_pages = 1

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return render_template(
        'programs.html',
        programs=programs,
        page=page,
        total_pages=total_pages
    )

#done grr
@views.route('/programs/delete/<course_code>', methods=['POST'])
def delete_program(course_code):
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        query = "DELETE FROM program WHERE code = %s"
        cursor.execute(query, (course_code,))
        connection.commit()
        flash('Program deleted successfully.', category='success')

    except mysql.connector.Error as err:
        flash(f"Error deleting program: {err}", category='danger')

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('views.programs'))

@views.route('/colleges', methods=['GET', 'POST'])
def colleges():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    colleges = []
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            action = request.form.get('action')
            college_code = request.form.get('code')
            college_name = request.form.get('name')
            original_college_code = request.form.get('originalCollegeCode')

            if not college_code or not college_name:
                flash('Both college code and name are required.', category='danger')
            else:
                if action == 'add':
                    try:
                        query = "SELECT COUNT(*) FROM college WHERE code = %s"
                        cursor.execute(query, (college_code,))
                        count = cursor.fetchone()['COUNT(*)']

                        if count > 0:
                            flash('College code already exists. Please choose a different code.', category='danger')
                        else:
                            query = "INSERT INTO college (code, name) VALUES (%s, %s)"
                            cursor.execute(query, (college_code, college_name))
                            connection.commit()
                            flash('College added successfully!', category='success')

                    except mysql.connector.Error as err:
                        flash(f"Error: {err}", category='danger')

                elif action == 'edit':
                    try:
                        query = "SELECT COUNT(*) FROM college WHERE code = %s AND code != %s"
                        cursor.execute(query, (college_code, original_college_code))
                        count = cursor.fetchone()['COUNT(*)']

                        if count > 0:
                            flash('Another college with the same code already exists.', category='danger')
                        else:
                            query = "UPDATE college SET code = %s, name = %s WHERE code = %s"
                            cursor.execute(query, (college_code, college_name, original_college_code))
                            connection.commit()
                            flash('College updated successfully!', category='success')

                    except mysql.connector.Error as err:
                        flash(f"Error updating college: {err}", category='danger')

        cursor.execute("SELECT COUNT(*) AS total FROM college")
        total_colleges = cursor.fetchone()['total']

        cursor.execute("SELECT code, name FROM college LIMIT %s OFFSET %s", (per_page, offset))
        colleges = cursor.fetchall()

        total_pages = (total_colleges + per_page - 1) // per_page

    except mysql.connector.Error as err:
        flash(f"Error: {err}", category='danger')

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('colleges.html', colleges=colleges, page=page, total_pages=total_pages)

@views.route('/colleges/delete/<code>', methods=['POST'])
def delete_college(code):
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        query = "DELETE FROM college WHERE code = %s"
        cursor.execute(query, (code,))
        connection.commit()
        flash("College deleted successfully!", "success")

    except mysql.connector.Error as err:
        connection.rollback()  
        flash(f"Error: {err}", "danger")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('views.colleges'))

@views.route('/search_student', methods=['GET', 'POST'])
def search_student():
    query = request.form.get('search_query', '').strip() or request.args.get('search_query', '').strip()
    field = request.form.get('search_field') or request.args.get('search_field')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('views.students'))

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)

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
        total_pages = (total_students + per_page - 1) // per_page

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        students = []
        total_pages = 1

    finally:
        cursor.close()
        connection.close()

    return render_template('students.html',students=students,page=page,total_pages=total_pages,search_query=query,search_field=field)

@views.route('/search_program', methods=['GET', 'POST'])
def search_program():
    query = request.form.get('search_query') or request.args.get('search_query', '')
    field = request.form.get('search_field') or request.args.get('search_field', '')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('views.programs'))

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)

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

        cursor.execute(f"SELECT COUNT(*) AS total FROM ({sql_query}) AS total_query", params)
        total_programs = cursor.fetchone()['total']

        sql_query += " LIMIT %s OFFSET %s"
        cursor.execute(sql_query, params + (per_page, offset))
        programs = cursor.fetchall()

        total_pages = (total_programs + per_page - 1) // per_page

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        programs = []  
        total_pages = 1

    finally:
        cursor.close()
        connection.close()

    return render_template('programs.html', programs=programs, page=page, total_pages=total_pages, search_query=query, search_field=field)

@views.route('/search_college', methods=['GET', 'POST'])
def search_college():
    query = request.form.get('search_query') or request.args.get('search_query', '')
    field = request.form.get('search_field') or request.args.get('search_field', '')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('views.colleges')) 

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)

        sql_query = """
            SELECT * FROM college 
            WHERE LOWER(code) LIKE %s 
            OR LOWER(name) LIKE %s
        """
        params = ('%' + query.lower() + '%',) * 2

        if field == "College Code":
            sql_query = "SELECT * FROM college WHERE LOWER(code) LIKE %s"
            params = ('%' + query.lower() + '%',)
        elif field == "College Name":
            sql_query = "SELECT * FROM college WHERE LOWER(name) LIKE %s"
            params = ('%' + query.lower() + '%',)

        cursor.execute(f"SELECT COUNT(*) AS total FROM ({sql_query}) AS total_query", params)
        total_colleges = cursor.fetchone()['total']

        cursor.execute(f"{sql_query} LIMIT %s OFFSET %s", params + (per_page, offset))
        colleges = cursor.fetchall()

        total_pages = (total_colleges + per_page - 1) // per_page

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        colleges = []  

    finally:
        cursor.close()
        connection.close()

    return render_template('colleges.html', colleges=colleges, page=page, total_pages=total_pages, search_query=query, search_field=field)
'''