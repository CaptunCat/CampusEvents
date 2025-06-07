from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
#from app.models import create_database


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_events.db'  # Using SQLite
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Used for form security


# Initialize SQLAlchemy
db = SQLAlchemy(app)
#csrf = CSRFProtect(app)  # Enable CSRF protection

migrate = Migrate(app, db)

from app import routes, models 
from app.models import User

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))