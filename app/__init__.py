from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'WebFinUp'

db = SQLAlchemy(app)

from app import models

migrate = Migrate(app, db)

var = [True]

from app import routes
