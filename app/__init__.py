from flask import Flask
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "your_very_secret_and_secure_key_12345"
    app.config['UPLOAD_FOLDER'] = "static/img"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main
    from app.admin.routes import admin

    app.register_blueprint(main)
    app.register_blueprint(admin)

    from app.api import api
    app.register_blueprint(api)

    return app
