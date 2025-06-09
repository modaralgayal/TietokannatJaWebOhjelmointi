import sqlite3

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/homepage")
def homepage():
    messages = db.query("SELECT content FROM messages")
    count = len(messages)
    message = "Page has " + str(count) + " messages"
    return render_template("homepage.html", message=message, messages=messages)


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql_command = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql_command, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/homepage")
    else:
        return "ERROR: Invalid username or password"


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql_command = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql_command, [username, password_hash])
    except sqlite3.IntegrityError:
        return "ERROR: user already exists"

    return "User created"


@app.route("/new")
def new():
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    if len(content) > 0:
        db.execute("INSERT INTO messages (content) VALUES (?)", [content])
        return redirect("/")
    return redirect("/")


@app.route("/result", methods=["POST"])
def result():
    message = request.form["content"]
    return render_template("result.html", message=message)


@app.route("/form")
def form():
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
