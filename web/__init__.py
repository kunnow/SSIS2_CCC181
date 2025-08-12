from flask import Flask
import mysql.connector
from .route import views
import cloudinary
import cloudinary.uploader

from web.controller.students import students_blueprint
from web.controller.programs import programs_blueprint
from web.controller.colleges import colleges_blueprint
from config import SECRET_KEY, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, CLOUD_NAME, API_KEY, API_SECRET

def create_app():
    app = Flask(__name__)

    print("Cloudinary credentials:")
    print("CLOUD_NAME =", CLOUD_NAME)
    print("API_KEY =", API_KEY)
    print("API_SECRET =", API_SECRET)
    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB

    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET
    )

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(students_blueprint, url_prefix='/')
    app.register_blueprint(programs_blueprint, url_prefix='/')
    app.register_blueprint(colleges_blueprint, url_prefix='/')

    return app