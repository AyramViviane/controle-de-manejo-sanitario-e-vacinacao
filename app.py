<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
=======
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
>>>>>>> d985ef316c84fd5080142a17f914133123df0735

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-super-secreta-agro-san-2026'

<<<<<<< HEAD
# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Banco de dados temporário em memória para usuários
users_db = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    if user_id in users_db:
        user = users_db[user_id]
        return User(user['id'], user['username'], user['password_hash'])
    return None

# --- ESTRUTURA DE VACINAÇÃO EXISTENTE ---
=======

#controle de animais
animais = []

def criar_animal(dados):
    dados["id"] = len(animais) + 1
    animais.append(dados)
    return dados

def listar_animais():
    return animais

def remover_animal(id):
    global animais
    animais[:] = [a for a in animais if a.get("id") != id]

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
    for v in vacinacoes:
        v["status"] = status_vacina(v.get("proxima_dose"))
    return render_template("listagem.html", animais=listar_animais(), vacinacoes=listar_vacinacoes(),  manejos=listar_manejos())
    
# feature controle de vacinação

>>>>>>> d985ef316c84fd5080142a17f914133123df0735
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

<<<<<<< HEAD

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = next((u for u in users_db.values() if u['username'] == username), None)

        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user)
            return redirect(url_for("inicio"))
        
        flash("Usuário ou senha incorretos.")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if any(u['username'] == username for u in users_db.values()):
            flash("Nome de usuário já existe.")
            return redirect(url_for('register'))

        user_id = str(len(users_db) + 1)
        users_db[user_id] = {
            'id': user_id,
            'username': username,
            'password_hash': generate_password_hash(password)
        }
        flash("Conta criada com sucesso! Faça login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# --- ROTAS DA APLICAÇÃO (PROTEGIDAS) ---

=======
def status_vacina(proxima_dose):
    if not proxima_dose:
        return None
    try:
        prox = date.fromisoformat(proxima_dose)
    except ValueError:
        return None

    hoje = date.today()

    if prox < hoje:
        return "atrasada"
    elif prox == hoje:
        return "hoje"
    else:
        return "em_dia"


# Página inicial
>>>>>>> d985ef316c84fd5080142a17f914133123df0735
@app.route("/")
@login_required
def inicio():
    return render_template("index.html")

@app.route('/lotes', methods=['GET', 'POST'])
@login_required
def lotes():
    if request.method == "POST":
        codigo = request.form.get("codigo")
        quantidade = request.form.get("quantidade")
        especie = request.form.get("especie")
        data_formacao = request.form.get("data_formacao")

        print("Novo lote cadastrado:", codigo, quantidade, especie, data_formacao)
        return redirect(url_for("listagem"))

    return render_template("lotes.html")

@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():
    if request.method == "POST":
<<<<<<< HEAD
        identificacao = request.form.get("identificacao")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        sexo = request.form.get("sexo")
        data_nascimento = request.form.get("data_nascimento")

        print("Novo animal cadastrado:", identificacao, especie, raca, sexo, data_nascimento)
=======

        criar_animal({
            "identificacao": request.form.get("identificacao"),
            "especie": request.form.get("especie"),
            "raca": request.form.get("raca"),
            "sexo": request.form.get("sexo"),
            "data_nascimento": request.form.get("data_nascimento"),
        })

>>>>>>> d985ef316c84fd5080142a17f914133123df0735
        return redirect(url_for("listagem"))

    return render_template("cadastro.html")

<<<<<<< HEAD
=======

# Remoção de um animal
@app.route("/animais/remover/<int:id>", methods=["POST"])
def remover_animal_route(id):
    remover_animal(id)
    return redirect(url_for("listagem"))


# Registro de vacinação
>>>>>>> d985ef316c84fd5080142a17f914133123df0735
@app.route("/vacinacao", methods=["GET", "POST"])
@login_required
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

@app.route("/vacinacao/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
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
<<<<<<< HEAD

@app.route("/listagem")
@login_required
def listagem():
    return render_template("listagem.html", vacinacoes=listar_vacinacoes())
=======
# Listagem
# Listagem
@app.route("/listagemvacina")
def listagemvacina():
    return render_template("listagemvacina.html", vacinacoes=listar_vacinacoes())
>>>>>>> d985ef316c84fd5080142a17f914133123df0735

@app.route("/atualizar")
@login_required
def atualizar():
    return render_template("atualizar.html")

if __name__ == "__main__":
    app.run(debug=True)