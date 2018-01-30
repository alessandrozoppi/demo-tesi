import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_ask import Ask

app = Flask(__name__)
ask = Ask(app, '/')
db = SQLAlchemy(app)

app.config.from_object('config')

basedir = os.path.abspath(os.path.dirname(__file__))

from app import routes, models
