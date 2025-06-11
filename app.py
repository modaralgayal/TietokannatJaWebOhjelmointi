import sqlite3
from os import abort

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db
import forum

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    threads = forum.get_threads()
    return render_template("index.html", threads=threads)


@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("index.html", query=query, results=results)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    messages = users.get_messages(user_id)
    return render_template("user.html", user=user, messages=messages)


@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    message = forum.get_message(message_id)
    if message["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("edit.html", message=message)

    if request.method == "POST":
        content = request.form["content"]
        forum.update_message(message["id"], content)
        return redirect("/thread/" + str(message["thread_id"]))


@app.route("/remove/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    item = forum.get_message(message_id)
    if not item:
        abort(404)
    type = "message"

    if request.method == "GET":
        return render_template("remove.html", item=item, type=type)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_message(item["id"])
        return redirect("/thread/" + str(item["thread_id"]))


@app.route("/remove_thread/<int:thread_id>", methods=["GET", "POST"])
def remove_thread(thread_id):
    item = forum.get_thread(thread_id)
    type = "thread"

    if request.method == "GET":
        return render_template("remove.html", item=item, type=type)

    if request.method == "POST":
        if "continue" in request.form:
            try:
                forum.remove_thread(thread_id)
            except:
                "Cannot delete threads with messages in them", 401
        return redirect("/")


@app.route("/new_thread", methods=["POST"])
def new_thread():
    require_login()
    title = request.form["title"]
    content = request.form["content"]
    user_id = session["user_id"]

    thread_id = forum.add_thread(title, content, user_id)
    return redirect("/thread/" + str(thread_id))


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = forum.get_thread(thread_id)
    if not thread:
        abort(404)
    messages = forum.get_messages(thread_id)
    return render_template("thread.html", thread=thread, messages=messages)


@app.route("/new_message", methods=["POST"])
def new_message():
    require_login()

    content = request.form["content"]
    user_id = session["user_id"]
    thread_id = request.form["thread_id"]

    try:
        forum.add_message(content, user_id, thread_id)
    except sqlite3.IntegrityError:
        abort(403)

    return redirect("/thread/" + str(thread_id))


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql_command = "SELECT id, username, password_hash FROM users WHERE username = ?"
    user = db.query(sql_command, [username])

    # Check if user was found
    if not user:
        return "ERROR: Invalid username or password", 401

    user_id = user[0][0]
    username = user[0][1]
    password_hash = user[0][2]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    else:
        return "ERROR: Invalid username or password", 401


@app.route("/create_user", methods=["POST"])
def create_user():
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

    return redirect("/")


@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")


@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
