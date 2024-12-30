from flask import Blueprint, render_template, request, flash, redirect, url_for
from web.models.programs import get_programs, add_program, update_program, delete_program, check_college_exists, search_programs, count_programs
import mysql.connector

programs_blueprint = Blueprint('programs_blueprint', __name__)

@programs_blueprint.route('/programs', methods=['GET', 'POST'])
def programs():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    programs = []
    total_programs = 0
    total_pages = 1

    programs, total_programs, total_pages = get_programs(offset, per_page)

    if request.method == 'POST':
        action = request.form.get('action')
        course_code = request.form.get('courseCode')
        course_name = request.form.get('courseName')
        college_code = request.form.get('collegeCode')
        original_course_code = request.form.get('originalCourseCode')

        if len(course_code) == 0 or len(course_name) == 0 or len(college_code) == 0:
            flash('All fields are required.', category='danger')
        else:
            if not check_college_exists(college_code):
                flash('The College Code does not exist.', category='danger')
            else:
                try:
                    if action == 'add':
                        add_program(course_code, course_name, college_code)
                        flash('Program added successfully!', category='success')
                        return redirect(url_for('programs_blueprint.programs', page=1))

                    elif action == 'edit':
                        update_program(course_code, course_name, college_code, original_course_code)
                        flash('Program updated successfully!', category='success')
                        return redirect(url_for('programs_blueprint.programs', page=page))

                except ValueError as err:
                    flash(f"{err}", category='danger')
                except mysql.connector.Error as err:
                    flash(f"Database error: {err}", category='danger')

    return render_template('programs.html',programs=programs,page=page,total_pages=total_pages)

@programs_blueprint.route('/programs/delete/<course_code>', methods=['POST'])
def delete_program_route(course_code):
    try:
        delete_program(course_code)
        flash('Program deleted successfully.', category='success')
    except mysql.connector.Error as err:
        flash(f"Error deleting program: {err}", category='danger')

    return redirect(url_for('programs_blueprint.programs'))

@programs_blueprint.route('/search_program', methods=['GET', 'POST'])
def search_program():
    query = request.form.get('search_query') or request.args.get('search_query', '')
    field = request.form.get('search_field') or request.args.get('search_field', '')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('programs_blueprint.programs'))

    programs = search_programs(query, field, offset, per_page)

    total_programs = count_programs(query, field)
    total_pages = (total_programs + per_page - 1) // per_page

    return render_template('programs.html',programs=programs,page=page,total_pages=total_pages,search_query=query,search_field=field)

