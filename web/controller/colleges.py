from flask import Blueprint, render_template, request, flash, redirect, url_for
from web.models.colleges import get_colleges, add_college, update_college, delete_college, search_colleges, count_colleges
import mysql.connector

colleges_blueprint = Blueprint('colleges_blueprint', __name__)

@colleges_blueprint.route('/colleges', methods=['GET', 'POST'])
def colleges():
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    colleges = []
    total_colleges = 0
    total_pages = 1

    colleges, total_colleges, total_pages = get_colleges(offset, per_page)

    if request.method == 'POST':
        action = request.form.get('action')
        college_code = request.form.get('code')
        college_name = request.form.get('name')
        original_college_code = request.form.get('originalCollegeCode')

        if not college_code or not college_name:
            flash('Both college code and name are required.', category='danger')
        else:
            try:
                if action == 'add':
                    add_college(college_code, college_name)
                    flash('College added successfully!', category='success')
                    return redirect(url_for('colleges_blueprint.colleges', page=1))

                elif action == 'edit':
                    update_college(college_code, college_name, original_college_code)
                    flash('College updated successfully!', category='success')
                    return redirect(url_for('colleges_blueprint.colleges', page=page))

            except ValueError as err:
                flash(f"{err}", category='danger')
            except mysql.connector.Error as err:
                flash(f"Database error: {err}", category='danger')

    return render_template('colleges.html',colleges=colleges,page=page,total_pages=total_pages)

@colleges_blueprint.route('/colleges/delete/<code>', methods=['POST'])
def delete_college_route(code):
    try:
        delete_college(code)
        flash("College deleted successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Error: {err}", "danger")

    return redirect(url_for('colleges_blueprint.colleges'))

@colleges_blueprint.route('/search_college', methods=['GET', 'POST'])
def search_college():
    query = request.form.get('search_query') or request.args.get('search_query', '')
    field = request.form.get('search_field') or request.args.get('search_field', '')
    page = request.args.get('page', 1, type=int)
    per_page = 13
    offset = (page - 1) * per_page

    if not query:
        return redirect(url_for('colleges_blueprint.colleges'))

    colleges = search_colleges(query, field, offset, per_page)

    total_colleges = count_colleges(query, field)
    total_pages = (total_colleges + per_page - 1) // per_page

    return render_template('colleges.html',colleges=colleges,page=page,total_pages=total_pages,search_query=query,search_field=field)
