import sqlite3

from flask import Flask, redirect, render_template, request
from werkzeug.security import generate_password_hash

app = Flask(__name__)


@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    messages = db.execute("SELECT content FROM messages").fetchall()
    count = len(messages)
    db.close()
    message = "Page has " + str(count) + " messages"
    return render_template("index.html", message=message, messages=messages)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    db = sqlite3.connect("database.db")
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
        db = sqlite3.connect("database.db")
        db.execute("INSERT INTO messages (content) VALUES (?)", [content])
        db.commit()
        db.close()
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
