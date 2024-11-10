from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from EASIEST.fixation import *
#postgresql://zywbkaiy:wL61f1mm1tXdNwci1Q_XTwpAbpddUi7Z@flora.db.elephantsql.com/zywbkaiy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nope@localhost/EASIEST'
app.config['SECRET_KEY'] = '15535b773a539ebcd6fc10cab12b5aed'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from EASIEST import routes

with app.app_context():
    db.create_all()






