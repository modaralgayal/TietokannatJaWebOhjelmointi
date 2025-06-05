import sqlite3

from flask import Flask, redirect, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    messages = db.execute("SELECT content FROM messages").fetchall()
    count = len(messages)
    db.close()
    message = "Page has " + str(count) + " messages"
    return render_template("index.html", message=message, messages=messages)


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
