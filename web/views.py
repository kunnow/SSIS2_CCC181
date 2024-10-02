from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import mysql.connector

views = Blueprint('views', __name__)

@views.route("/")
def sidebar():
    return render_template('base.html')

@views.route('/students', endpoint='students', methods=['GET', 'POST'])
def students():
    students = []

    if request.method == 'POST':
        student_id = request.form.get('id')
        firstName = request.form.get('firstname')
        lastName = request.form.get('lastname')
        yearLevel = request.form.get('year')
        gender = request.form.get('gender')
        course = request.form.get('course')

        if len(firstName) == 0:
            flash('Invalid first name.', category='error')
        elif len(lastName) == 0:
            flash('Invalid last name.', category='error')
        elif not yearLevel.isdigit() or int(yearLevel) not in range(1, 5):
            flash('Invalid Year Level. Must be between 1 and 4.', category='error')
        else:
            try:
                connection = mysql.connector.connect(
                    host=current_app.config['MYSQL_HOST'],
                    user=current_app.config['MYSQL_USER'],
                    password=current_app.config['MYSQL_PASSWORD'],
                    database=current_app.config['MYSQL_DB']
                )
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM student WHERE id = %s", (student_id,))
                existing_student = cursor.fetchone()

                if existing_student:  
                    query = """UPDATE student 
                               SET firstname = %s, lastname = %s, year = %s, gender = %s, course = %s 
                               WHERE id = %s"""
                    cursor.execute(query, (firstName, lastName, yearLevel, gender, course, student_id))
                    flash('Student updated successfully.', category='success')
                else: 
                    query = """INSERT INTO student (id, firstname, lastname, year, gender, course) 
                               VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (student_id, firstName, lastName, yearLevel, gender, course))
                    flash('Student added successfully.', category='success')

                connection.commit()

            except mysql.connector.Error as err:
                flash(f"Error: {err}", category='error')

            finally:
                cursor.close()
                connection.close()

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error: {err}", category='error')
        students = []

    finally:
        cursor.close()
        connection.close()

    return render_template('students.html', students=students)

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
        flash(f"Error: {err}", category='error')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('views.students'))  

@views.route('/programs', endpoint='programs')
def students():
    return render_template('programs.html')

@views.route('/colleges', methods=['GET'])
def colleges():
    colleges = []
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM college")
        colleges = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error: {err}", "error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('colleges.html', colleges=colleges)

@views.route('/colleges/add', methods=['POST'])
def add_college():
    code = request.form.get('code')
    name = request.form.get('name')

    if not code or not name:
        flash("All fields are required!", "error")
        return redirect(url_for('views.colleges'))

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        query = "INSERT INTO college (code, name) VALUES (%s, %s)"
        cursor.execute(query, (code, name))
        connection.commit()
        flash("College added successfully!", "success")

    except mysql.connector.Error as err:
        connection.rollback() 
        flash(f"Error: {err}", "error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('views.colleges'))

@views.route('/colleges/edit/<code>', methods=['POST'])
def edit_college(code):
    new_code = request.form.get('code') 
    name = request.form.get('name')

    if not new_code or not name:
        flash("Both code and name are required!", "error")
        return redirect(url_for('views.colleges'))

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        print(f"New code: {new_code}, Old code: {code}, New name: {name}")


        if new_code != code:
            print(f"Updating related_table: college_code = {new_code} WHERE college_code = {code}") 
            cursor.execute("UPDATE related_table SET college_code = %s WHERE college_code = %s", (new_code, code))
            connection.commit()
            print(f"Related table update: Rows affected = {cursor.rowcount}")

        query = "UPDATE college SET code = %s, name = %s WHERE code = %s"
        print(f"Executing query: {query} with values: {new_code}, {name}, {code}")  
        cursor.execute(query, (new_code, name, code))
        connection.commit()
        print(f"College update: Rows affected = {cursor.rowcount}") 

        if cursor.rowcount == 0:
            flash("No college found with the provided code!", "error")
        else:
            flash("College updated successfully!", "success")

    except mysql.connector.Error as err:
        if connection:
            connection.rollback() 
        flash(f"Database Error: {err}", "error")

    except Exception as e:
        flash(f"Unexpected error: {e}", "error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('views.colleges'))

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
        flash(f"Error: {err}", "error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('views.colleges'))
