from flask import render_template, url_for, redirect, flash
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    logout_user,
)
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from database import app, db, User, Flights, bcrypt, init_db
import os

init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegistrationForm(FlaskForm):
    email = EmailField(
        validators=[InputRequired(), Length(min=4, max=320), Email()],
        render_kw={"placeholder": "E-mail"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Senha"},
    )
    submit = SubmitField("Criar conta")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            flash("Usuário já existe.")
            raise ValidationError("Usuário já existe.")


class LoginForm(FlaskForm):
    email = EmailField(
        validators=[InputRequired(), Length(min=4, max=320), Email()],
        render_kw={"placeholder": "E-mail"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Senha"},
    )
    submit = SubmitField("Login")


class SearchMarketForm(FlaskForm):
    mercado = SelectField("Escolha um mercado", choices=[], coerce=str)
    start_date = DateField("Data de Início", format="%Y-%m-%d")
    end_date = DateField("Data de Fim", format="%Y-%m-%d")
    submit = SubmitField("Filtrar")


@app.route("/")
def home():
    return redirect("/login")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    # Seleciona apenas os mercados para popular o DropDown de mercados
    mercados = db.session.query(Flights.mercado).distinct().all()
    form = SearchMarketForm()
    form.mercado.choices = [(mercado[0], mercado[0]) for mercado in mercados]

    if form.validate_on_submit():
        selected_market = form.mercado.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        flights_query = Flights.query.filter(Flights.mercado == selected_market)
        if start_date:
            flights_query = flights_query.filter(Flights.data >= start_date)
        if end_date:
            flights_query = flights_query.filter(Flights.data <= end_date)
        flights = flights_query.all()

        x = [flight.data.strftime("%b %Y") for flight in flights]
        y = [flight.rpk for flight in flights]

        data = {"labels": x, "rpk": y, "mercado": selected_market}

        return render_template("dashboard.html.jinja", form=form, data=data)

    return render_template("dashboard.html.jinja", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
            else:
                flash("Login inválido. E-mail ou senha incorretos.")
                return redirect("/login")
        else:
            flash("Login inválido. E-mail ou senha incorretos.")
            return redirect("/login")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário criado.")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
