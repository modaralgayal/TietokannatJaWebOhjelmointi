import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    db.commit()
    result = db.execute("SELECT COUNT(*) FROM visits").fetchone()
    count = result[0]
    db.close()
    message = "Page has been loaded " + str(count) + " times"
    return render_template("index.html", message=message)


@app.route("/result", methods=["POST"])
def result():
    message = request.form["message"]
    extras = request.form.getlist("extra")
    pizza = request.form["pizza"]
    return render_template("result.html", message=message, extras=extras, pizza=pizza)


@app.route("/form")
def form():
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
