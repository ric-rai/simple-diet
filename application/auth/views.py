from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user

from application import app, db
from application.auth.models import User
from application.auth.forms import LoginForm, RegisterForm


@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("auth/login.html", form=LoginForm())

    form = LoginForm(request.form)
    if not form.validate():
        return render_template("auth/login.html", form=form)

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        return render_template("auth/login.html", form=form, error="Väärä käyttäjätunnus tai salasana")

    login_user(user)
    return redirect(url_for("overview"))


@app.route("/auth/logout")
def auth_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/auth/register", methods=["GET", "POST"])
def auth_register():
    if request.method == "GET":
        return render_template("auth/register.html", form=RegisterForm())

    form = RegisterForm(request.form)
    if not form.validate():
        return render_template("auth/register.html", form=form)

    user = User(form.username.data, form.password.data, form.name.data, form.email.data)

    db.session().add(user)
    db.session().commit()

    login_user(user)
    return redirect(url_for("index"))
