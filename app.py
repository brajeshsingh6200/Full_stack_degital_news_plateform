import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.environ.get("NEWS_API_KEY")
if not api_key or api_key == "default_key":
    logging.warning(f"NEWS_API_KEY is missing or set to default_key. NewsAPI will not work. Current value: {api_key}")
else:
    logging.info(f"NEWS_API_KEY loaded successfully: {api_key[:6]}... (hidden)")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///news_portal.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default admin user if not exists
    from models import User
    from werkzeug.security import generate_password_hash
    
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@newsportal.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default admin user created (username: admin, password: admin123)")

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
