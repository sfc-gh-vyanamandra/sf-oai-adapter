from flask import Flask
from config import Config
from extensions import db, bootstrap
from routes.main import main_bp, load_valid_jwt
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        load_valid_jwt()

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/v1")

    return app

