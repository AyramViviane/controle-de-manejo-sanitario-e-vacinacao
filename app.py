from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


#controledemanejo
manejos = []

def criar_manejo(dados):
    dados["id"] = len(manejos) + 1
    manejos.append(dados)
    return dados

def listar_manejos():
    return manejos

# Rota de Registro de Manejo
@app.route("/manejo", methods=["GET", "POST"])
def manejo():
    if request.method == "POST":
        criar_manejo({
            "animal": request.form.get("animal"),
            "tipo_manejo": request.form.get("tipo_manejo"),
            "data_manejo": request.form.get("data_manejo"),
            "produto": request.form.get("produto"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes")
        })
        return redirect(url_for("listagem"))
    return render_template("manejo.html")

# Atualize a rota de listagem existente para enviar também os manejos
@app.route("/listagem")
def listagem():
    return render_template("listagem.html", vacinacoes=listar_vacinacoes(),  manejos=listar_manejos())
    
# feature controle de vacinação

vacinacoes = []

def criar_vacinacao(dados):
    dados["id"] = len(vacinacoes) + 1
    vacinacoes.append(dados)
    return dados

def listar_vacinacoes():
    return vacinacoes

def buscar_vacinacao(id):
    return next((v for v in vacinacoes if v["id"] == id), None)

def atualizar_vacinacao(id, dados):
    registro = buscar_vacinacao(id)
    if registro:
        registro.update(dados)
    return registro

# Página inicial
@app.route("/")
def inicio():
    return render_template("index.html")

#Cadastro de Lotes

@app.route('/lotes', methods=['GET', 'POST'])
def lotes():
    if request.method == "POST":
        codigo = request.form.get("codigo")
        quantidade = request.form.get("quantidade")
        especie = request.form.get("especie")
        data_formacao = request.form.get("data_formacao")

        print("Novo lote cadastrado:")
        print(f"Código: {codigo}")
        print(f"Quantidade de animais: {quantidade}")
        print(f"Espécie: {especie}")
        print(f"Data de formação: {data_formacao}")

        return redirect(url_for("listagem"))

    return render_template("lotes.html")


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
        criar_vacinacao({
            "animal": request.form.get("animal"),
            "vacina": request.form.get("vacina"),
            "lote": request.form.get("lote"),
            "fabricante": request.form.get("fabricante"),
            "data_aplicacao": request.form.get("data_aplicacao"),
            "proxima_dose": request.form.get("proxima_dose"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes"),
        })

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html")


# Edição de um registro de vacinação
@app.route("/vacinacao/atualizar/<int:id>", methods=["GET", "POST"])
def atualizar_vacinacao_route(id):

    registro = buscar_vacinacao(id)

    if registro is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        atualizar_vacinacao(id, {
            "animal": request.form.get("animal"),
            "vacina": request.form.get("vacina"),
            "lote": request.form.get("lote"),
            "fabricante": request.form.get("fabricante"),
            "data_aplicacao": request.form.get("data_aplicacao"),
            "proxima_dose": request.form.get("proxima_dose"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes"),
        })

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html", registro=registro)
# Listagem
# Listagem
@app.route("/listagemvacina")
def listagemvacina():
    return render_template("listagemvacina.html", vacinacoes=listar_vacinacoes())

# Atualização
@app.route("/atualizar")
def atualizar():
    return render_template("atualizar.html")


if __name__ == "__main__":
    app.run(debug=True)
