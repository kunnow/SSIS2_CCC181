from flask import Flask
import mysql.connector
import cloudinary
import cloudinary.uploader
import cloudinary.api

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
    secure = True
    )

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app