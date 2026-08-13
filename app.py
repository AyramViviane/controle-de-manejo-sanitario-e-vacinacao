from flask import Flask, render_template

# feature controle de vacinação


from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Página inicial
@app.route("/")
def inicio():
    return render_template("index.html")


# Cadastro de animal
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        identificacao = request.form.get("identificacao")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        sexo = request.form.get("sexo")
        data_nascimento = request.form.get("data_nascimento")

        print("Novo animal cadastrado:")
        print(f"Identificação: {identificacao}")
        print(f"Espécie: {especie}")
        print(f"Raça: {raca}")
        print(f"Sexo: {sexo}")
        print(f"Data de nascimento: {data_nascimento}")

        return redirect(url_for("listagem"))

    return render_template("cadastro.html")


# Registro de vacinação
@app.route("/vacinacao", methods=["GET", "POST"])
def vacinacao():

    if request.method == "POST":

        animal = request.form.get("animal")
        vacina = request.form.get("vacina")
        lote = request.form.get("lote")
        fabricante = request.form.get("fabricante")
        data_aplicacao = request.form.get("data_aplicacao")
        proxima_dose = request.form.get("proxima_dose")
        dose = request.form.get("dose")
        responsavel = request.form.get("responsavel")
        observacoes = request.form.get("observacoes")

        print("Registro de vacinação:")
        print(f"Animal: {animal}")
        print(f"Vacina: {vacina}")
        print(f"Lote: {lote}")
        print(f"Fabricante: {fabricante}")
        print(f"Data da aplicação: {data_aplicacao}")
        print(f"Próxima dose: {proxima_dose}")
        print(f"Dose: {dose}")
        print(f"Responsável: {responsavel}")
        print(f"Observações: {observacoes}")

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html")


# Listagem
@app.route("/listagem")
def listagem():
    return render_template("listagem.html")


# Atualização
@app.route("/atualizar")
def atualizar():
    return render_template("atualizar.html")


if __name__ == "__main__":
    app.run(debug=True)
