from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'bbd99f33e380782fbb88f805'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from market import routes  # import routes *after* app/db created