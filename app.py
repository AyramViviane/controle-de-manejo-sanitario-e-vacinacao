from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/listagem")
def listagem():
    return render_template("listagem.html")


@app.route("/atualizar")
def atualizar():
    return render_template("atualizar.html")


if __name__ == "__main__":
    app.run(debug=True)