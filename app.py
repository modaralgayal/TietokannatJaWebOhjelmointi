import math
import sqlite3
from os import abort

from flask import Flask, make_response, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db
import forum
import users

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    thread_count = forum.thread_count()
    page_count = math.ceil(thread_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    threads = forum.get_threads(page, page_size)
    return render_template(
        "index.html", page=page, page_count=page_count, threads=threads
    )


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            return "VIRHE: väärä tiedostomuoto"

        image = file.read()
        if len(image) > 100 * 1024:
            return "ERROR: Image is too large"

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))


@app.route("/image/<int:user_id>")
def show_image(user_id):
    require_login()
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("index.html", query=query, results=results)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    require_login()
    user = users.get_user(user_id)
    if not user:
        abort(404)
    messages = users.get_messages(user_id)
    return render_template("user.html", user=user, messages=messages)


@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    require_login()
    message = forum.get_message(message_id)
    print(message["id"])
    print(message["user_id"])
    print(session["user_id"])
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
    require_login()
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
    require_login()
    item = forum.get_thread(thread_id)
    type = "thread"

    if request.method == "GET":
        return render_template("remove.html", item=item, type=type)

    if request.method == "POST":
        if "cancel" in request.form:
            return redirect("/")
        if "continue" in request.form:
            success = forum.remove_thread(thread_id)
            if not success:
                print("Cannot delete thread — likely has messages")
                return "Cannot delete thread — likely has messages", 400
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
