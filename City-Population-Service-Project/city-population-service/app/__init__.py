from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Connect to database when app starts
    from app.db import db_client
    with app.app_context():
        if not db_client.connect():
            app.logger.error("Failed to connect to MySQL database. Service may not function correctly.")
    
    return app