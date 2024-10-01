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

@views.route('/colleges', endpoint='colleges')
def students():
    return render_template('colleges.html')