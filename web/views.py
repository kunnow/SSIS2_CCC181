from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route("/")
def home():
    return render_template('base.html')

@views.route('/students', endpoint='students')
def students():
    return render_template('students.html')

@views.route('/programs', endpoint='programs')
def students():
    return render_template('programs.html')

@views.route('/colleges', endpoint='colleges')
def students():
    return render_template('colleges.html')