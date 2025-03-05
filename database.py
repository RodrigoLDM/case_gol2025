from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_login import UserMixin
from os import environ

app = Flask(__name__)

DATABASE_URL = environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SECRET_KEY"] = "ultramegasecretkey"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(510), nullable=False)


class Flights(db.Model):
    __tablename__ = "voos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    mercado = db.Column(db.String(10))
    rpk = db.Column(db.Float)


def init_db():
    with app.app_context():
        db.create_all()
