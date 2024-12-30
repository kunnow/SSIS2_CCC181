from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import cloudinary.uploader
import cloudinary
from web.models.students import get_students, add_student, update_student, delete_student_by_id, get_student_by_id, search_students, count_students, is_valid_image

students_blueprint = Blueprint('students_blueprint', __name__)

@students_blueprint.route('/students', endpoint='students', methods=['GET', 'POST'])
def students():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    students = []
    total_students = 0
    total_pages = 1

    students, total_students, total_pages = get_students(offset, per_page)

    if request.method == 'POST':
        image = request.files.get('image_url')
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
                image_url = None
                if image:
                    if is_valid_image(image):
                        upload_result = cloudinary.uploader.upload(image)
                        image_url = upload_result.get("url")
                    else:
                        flash("Invalid image file. Only JPG, JPEG, and PNG files are allowed.", category='danger')
                        return redirect(url_for('students_blueprint.students'))

                if action == "add":
                    existing_student = get_student_by_id(student_id)
                    if existing_student:
                        flash('Student ID already exists. Please use a different ID.', category='danger')
                    else:
                        add_student(image_url, student_id, firstName, lastName, yearLevel, gender, course)
                        flash('Student added successfully.', category='success')

                elif action == "edit":
                    update_student(image_url, firstName, lastName, yearLevel, gender, course, student_id)
                    flash('Student updated successfully.', category='success')

            except ValueError as err:
                flash(str(err), category='danger')
            except Exception as err:
                flash(f"Error: {err}", category='danger')

    return render_template('students.html', students=students, page=page, total_pages=total_pages)

@students_blueprint.route('/students/delete/<student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        delete_student_by_id(student_id)
        flash('Student deleted successfully.', category='success')
    except Exception as err:
        flash(f"Error: {err}", category='danger')

    return redirect(url_for('students_blueprint.students'))

@students_blueprint.route('/search_student', methods=['GET', 'POST'])
def search_student():
    query = request.form.get('search_query', '').strip() or request.args.get('search_query', '').strip()
    field = request.form.get('search_field') or request.args.get('search_field')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('students_blueprint.students'))

    students = search_students(query, field, offset, per_page)

    total_students = count_students(query, field)
    total_pages = (total_students + per_page - 1) // per_page

    return render_template('students.html',students=students,page=page,total_pages=total_pages,search_query=query,search_field=field)

