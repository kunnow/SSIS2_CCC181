from flask import Flask
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12345687'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'shir1234'
    app.config['MYSQL_DB'] = 'ssis2'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app