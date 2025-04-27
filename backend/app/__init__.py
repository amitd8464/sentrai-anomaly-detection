import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# load the .env so SECRET_KEY still comes from there

db = SQLAlchemy()

def create_app():
    dotenv_path = Path(__file__).parents[1].parent / 'backend' / '.env'
    print(dotenv_path)
    load_dotenv(dotenv_path=dotenv_path)
    
    app = Flask(__name__, instance_relative_config=True)

    # 1) Secret key and DB setup
    project_root = Path(__file__).parents[2]
    data_dir = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    db_file = data_dir / 'user_logs.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'dev')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    # 2) Inside app context
    with app.app_context():
        from backend.app.models.log import UserLog  # ✅ IMPORT UserLog FIRST
        db.create_all()                             # ✅ CREATE TABLES RIGHT AFTER
        from backend.app.api.routes import api_bp   # ✅ IMPORT ROUTES AFTERWARDS
        app.register_blueprint(api_bp, url_prefix='/api')
        from backend.app.api.anomaly_routes import anomaly_bp
        app.register_blueprint(anomaly_bp, url_prefix='/anomaly')


    return app
