# Código usado apenas para tratar os dados fornecidos pelo arquivo .csv e popular a tabela com as informações

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from os import environ
import pandas as pd


app = Flask(__name__)

DATABASE_URL = "yordbURL"  # Inserir o nome da base de dados aqui
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SECRET_KEY"] = "ultramegasecretkey"

db = SQLAlchemy(app)


class Flights(db.Model):
    __tablename__ = "voos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    mercado = db.Column(db.String(10))
    rpk = db.Column(db.Float)


def populate_db():
    csv_url = "https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Dados%20Estat%C3%ADsticos%20do%20Transporte%20A%C3%A9reo/Dados_Estatisticos.csv"
    df = pd.read_csv(csv_url, sep=";", header=1)

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


populate_db()
