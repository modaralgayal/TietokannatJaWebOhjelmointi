from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    words = ["apina", "banaani", "cembalo"]
    return render_template("index.html", message="Tervetuloa!", items=words)


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
