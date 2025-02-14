from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_login import UserMixin
import pandas as pd
from os import environ


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("POSTGRES_DB_URL")
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
        populate_db()


def populate_db():
    df = pd.read_csv("Dados_Estatisticos.csv", sep=";", header=1)

    filtered_df = df[
        (df["EMPRESA_SIGLA"] == "GLO")
        & (df["GRUPO_DE_VOO"] == "REGULAR")
        & (df["NATUREZA"] == "DOMÉSTICA")
    ]

    filtered_df.loc[:, "mercado"] = filtered_df.apply(
        lambda row: "".join(
            sorted(
                [row["AEROPORTO_DE_ORIGEM_SIGLA"], row["AEROPORTO_DE_DESTINO_SIGLA"]]
            )
        ),
        axis=1,
    )

    filtered_df["data"] = pd.to_datetime(
        df["ANO"].astype(str) + "-" + df["MES"].astype(str).str.zfill(2) + "-01"
    )

    filtered_df = filtered_df[["data", "mercado", "RPK"]]
    filtered_df.rename(
        columns={"RPK": "rpk"},
        inplace=True,
    )

    with app.app_context():

        data = filtered_df.to_dict(orient="records")

        flights = [Flights(**row) for row in data]

        db.session.bulk_save_objects(flights)
        db.session.commit()
