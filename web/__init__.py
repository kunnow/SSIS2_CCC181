from flask import Flask
import mysql.connector
from .route import views
import cloudinary
import cloudinary.uploader

from web.controller.students import students_blueprint
from web.controller.programs import programs_blueprint
from web.controller.colleges import colleges_blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12345687'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'shir1234'
    app.config['MYSQL_DB'] = 'ssis2'

    cloudinary.config(
        cloud_name = "dg8ofwmtu",
        api_key = "596471217998654",
        api_secret = "wHG8wuEhqhvEKe4E1m2kIm5lJ4s",
    )

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(students_blueprint, url_prefix='/')
    app.register_blueprint(programs_blueprint, url_prefix='/')
    app.register_blueprint(colleges_blueprint, url_prefix='/')

    return app