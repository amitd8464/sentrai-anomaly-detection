import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# load the .env so SECRET_KEY still comes from there
dotenv_path = Path(__file__).parents[1].parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # 1) Secret key from .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

    # 2) Force an absolute SQLite path
    #    backend/ folder
    project_root = Path(__file__).parents[2]  
    data_dir     = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    db_file = data_dir / 'user_logs.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3) CORS & init
    CORS(app)
    db.init_app(app)

    # 4) Create tables & register routes
    with app.app_context():
        from backend.app.api.routes import api_bp
        from backend.app.models.log  import UserLog
        db.create_all()
        app.register_blueprint(api_bp, url_prefix='/api')

    return app
