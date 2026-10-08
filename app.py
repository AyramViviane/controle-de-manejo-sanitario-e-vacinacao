from datetime import date
import os
import sqlite3
from flask import Flask, flash, g, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-super-secreta-agro-san-2026"
DATABASE = "database.db"

# --- CONFIGURAÇÃO DA BASE DE DADOS ---


def get_db():
  """Obtém a conexão com a base de dados SQLite para o contexto atual."""
  db = getattr(g, "_database", None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Permite aceder aos campos por nome
  return db


@app.teardown_appcontext
def close_connection(exception):
  """Fecha a conexão com a base de dados no final de cada requisição."""
  db = getattr(g, "_database", None)
  if db is not None:
    db.close()


def init_db():
  """Cria as tabelas com base no schema.sql e garante utilizador com senha em hash."""
  with app.app_context():
    db = get_db()
    with open("schema.sql", mode="r", encoding="utf-8") as f:
      db.cursor().executescript(f.read())
    db.commit()

    # Garantir que o admin padrão do schema tenha senha em hash seguro
    cursor = db.cursor()
    senha_admin_hash = generate_password_hash("AdminSecure2026*")
    cursor.execute(
        """
        INSERT OR REPLACE INTO usuarios (id, username, senha, perfil) 
        VALUES (1, 'admin_db', ?, 'admin')
    """,
        (senha_admin_hash,),
    )
    db.commit()


# --- CONFIGURAÇÃO DO FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "Por favor, faça login para aceder a esta página."
)


class User(UserMixin):

  def __init__(self, id, username, password, perfil):
    self.id = id
    self.username = username
    self.password = password
    self.perfil = perfil


@login_manager.user_loader
def load_user(user_id):
  db = get_db()
  cursor = db.cursor()
  cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
  user_data = cursor.fetchone()
  if user_data:
    return User(
        user_data["id"],
        user_data["username"],
        user_data["senha"],
        user_data["perfil"],
    )
  return None


# --- FUNÇÃO AUXILIAR: ESTADO DA VACINA ---
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


# --- ROTAS DE AUTENTICAÇÃO ---


@app.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("inicio"))

  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    user_data = cursor.fetchone()

    # Validação segura utilizando estritamente check_password_hash
    if user_data and check_password_hash(user_data["senha"], password):
      user = User(
          user_data["id"],
          user_data["username"],
          user_data["senha"],
          user_data["perfil"],
      )
      login_user(user)
      return redirect(url_for("inicio"))

    flash("Utilizador ou palavra-passe incorretos.")

  return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for("inicio"))

  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    perfil = "app_user"

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    if cursor.fetchone():
      flash("O nome de utilizador já existe.")
      return redirect(url_for("register"))

    # Criando o hash seguro da senha fornecida pelo utilizador
    senha_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO usuarios (username, senha, perfil) VALUES (?, ?, ?)",
        (username, senha_hash, perfil),
    )
    db.commit()

    flash("Conta criada com sucesso! Faça login.")
    return redirect(url_for("login"))

  return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("login"))


# --- ROTAS DA APLICAÇÃO (PROTEGIDAS) ---


@app.route("/")
@login_required
def inicio():
  return render_template("index.html")


@app.route("/lotes", methods=["GET", "POST"])
@login_required
def lotes():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    nome = request.form.get("codigo")
    quantidade = request.form.get("quantidade")
    descricao = request.form.get("especie")

    cursor.execute(
        "INSERT INTO lotes (nome, descricao, quantidade_animais) VALUES (?, ?,"
        " ?)",
        (nome, descricao, quantidade),
    )
    db.commit()
    return redirect(url_for("listagem"))

  return render_template("lotes.html")


@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():
  if request.method == "POST":
    return redirect(url_for("listagem"))
  return render_template("cadastro.html")


@app.route("/manejo", methods=["GET", "POST"])
@login_required
def manejo():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    lote_id = request.form.get("animal")
    tipo_manejo = request.form.get("tipo_manejo")
    data_manejo = request.form.get("data_manejo")
    observacoes = request.form.get("observacoes")

    cursor.execute(
        "INSERT INTO manejo_sanitario (lote_id, tipo_manejo, data_manejo,"
        " observacoes) VALUES (?, ?, ?, ?)",
        (lote_id, tipo_manejo, data_manejo, observacoes),
    )
    db.commit()
    return redirect(url_for("listagem"))

  cursor.execute("SELECT * FROM lotes")
  lotes_cadastrados = cursor.fetchall()
  return render_template("manejo.html", lotes=lotes_cadastrados)


@app.route("/vacinacao", methods=["GET", "POST"])
@login_required
def vacinacao():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    lote_id = request.form.get("animal")
    nome_vacina = request.form.get("vacina")
    fabricante = request.form.get("fabricante")
    data_vacinacao = request.form.get("data_aplicacao")
    proxima_dose = request.form.get("proxima_dose")

    cursor.execute(
        "INSERT INTO vacinas (nome_vacina, fabricante) VALUES (?, ?)",
        (nome_vacina, fabricante),
    )
    vacina_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO vacinacao (lote_id, vacina_id, data_vacinacao,"
        " proxima_dose) VALUES (?, ?, ?, ?)",
        (lote_id, vacina_id, data_vacinacao, proxima_dose),
    )
    db.commit()
    return redirect(url_for("listagem"))

  cursor.execute("SELECT * FROM lotes")
  lotes_cadastrados = cursor.fetchall()
  return render_template("vacinacao.html", lotes=lotes_cadastrados)


@app.route("/listagem")
@login_required
def listagem():
  db = get_db()
  cursor = db.cursor()

  cursor.execute("SELECT * FROM lotes")
  lotes = cursor.fetchall()

  cursor.execute("""
        SELECT v.*, vac.nome_vacina, l.nome as lote_nome 
        FROM vacinacao v 
        JOIN vacinas vac ON v.vacina_id = vac.id 
        JOIN lotes l ON v.lote_id = l.id
    """)
  vacinacoes = [dict(row) for row in cursor.fetchall()]

  for v in vacinacoes:
    v["status"] = status_vacina(v.get("proxima_dose"))

  cursor.execute("""
        SELECT m.*, l.nome as lote_nome 
        FROM manejo_sanitario m 
        JOIN lotes l ON m.lote_id = l.id
    """)
  manejos = cursor.fetchall()

  return render_template(
      "listagem.html",
      animais=lotes,
      vacinacoes=vacinacoes,
      manejos=manejos,
  )


if __name__ == "__main__":
  # Se o banco de dados não existir, cria e popula as tabelas com hash seguro
  if not os.path.exists(DATABASE):
    init_db()
    print(
        "Base de dados criada e populada com sucesso (com senhas em hash"
        " seguro)!"
    )

  app.run(debug=True)