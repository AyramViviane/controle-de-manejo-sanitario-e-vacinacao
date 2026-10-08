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
  """Obtém a conexão com a base de dados SQLite."""
  db = getattr(g, "_database", None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Permite aceder às colunas pelo nome
  return db


@app.teardown_appcontext
def close_connection(exception):
  """Fecha a conexão com a base de dados ao terminar a requisição."""
  db = getattr(g, "_database", None)
  if db is not None:
    db.close()


def init_db():
  """Cria todas as tabelas com a estrutura completa."""
  with app.app_context():
    db = get_db()
    cursor = db.cursor()

    # 1. Tabela de Utilizadores
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL
            )
        """)

    # 2. Tabela de Animais
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificacao TEXT NOT NULL,
                especie TEXT,
                raca TEXT,
                data_nascimento TEXT
            )
        """)

    # 3. Tabela de Lotes
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_lote TEXT,
                nome TEXT,
                descricao TEXT,
                quantidade_animais INTEGER,
                especie TEXT,
                data_formacao TEXT
            )
        """)

    # 4. Tabela de Vacinações
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacinacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal TEXT,
                lote_id INTEGER,
                vacina_id INTEGER,
                vacina TEXT,
                data_vacinacao TEXT,
                data_aplicacao TEXT,
                proxima_dose TEXT,
                status TEXT,
                responsavel TEXT
            )
        """)

    # Admin padrão
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

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    if cursor.fetchone():
      flash("O nome de utilizador já existe.")
      return redirect(url_for("register"))

    senha_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO usuarios (username, senha, perfil) VALUES (?, ?, ?)",
        (username, senha_hash, "app_user"),
    )
    db.commit()

    flash("Conta criada com sucesso!")
    return redirect(url_for("login"))

  return render_template("registrar.html")


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("login"))


# --- ROTAS PRINCIPAIS ---


# --- ROTA PRINCIPAL (DASHBOARD) ---


@app.route('/')
@login_required
def inicio():
  db = get_db()
  cursor = db.cursor()

  # 1. Contar o número de animais
  cursor.execute('SELECT COUNT(*) FROM animais')
  total_animais = cursor.fetchone()[0]

  # 2. Contar o número de vacinações
  cursor.execute('SELECT COUNT(*) FROM vacinacao')
  total_vacinacoes = cursor.fetchone()[0]

  # 3. Contar o número de lotes
  cursor.execute('SELECT COUNT(*) FROM lotes')
  total_lotes = cursor.fetchone()[0]

  # 4. Soma total de todos os registos do sistema
  total_registros = total_animais + total_vacinacoes + total_lotes

  # Enviar os dados contados para o template HTML
  return render_template(
      'index.html',
      total_animais=total_animais,
      total_vacinacoes=total_vacinacoes,
      total_lotes=total_lotes,
      total_registros=total_registros,
  )

@app.route("/lotes", methods=["GET", "POST"])
@login_required
def lotes():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    codigo = (
        request.form.get("codigo")
        or request.form.get("codigo_lote")
        or "LOTE-001"
    )
    quantidade = request.form.get("quantidade") or request.form.get(
        "quantidade_animais"
    )
    especie = request.form.get("especie")
    data_formacao = request.form.get("data_formacao") or str(date.today())

    cursor.execute(
        """
            INSERT INTO lotes (codigo_lote, nome, quantidade_animais, especie, data_formacao) 
            VALUES (?, ?, ?, ?, ?)
        """,
        (codigo, codigo, quantidade, especie, data_formacao),
    )
    db.commit()
    return redirect(url_for("listagem"))

  return render_template("lotes.html")


@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    identificacao = request.form.get("identificacao")
    especie = request.form.get("especie")
    raca = request.form.get("raca")
    data_nascimento = request.form.get("data_nascimento")

    cursor.execute(
        """
            INSERT INTO animais (identificacao, especie, raca, data_nascimento)
            VALUES (?, ?, ?, ?)
        """,
        (identificacao, especie, raca, data_nascimento),
    )
    db.commit()
    return redirect(url_for("listagem"))

  return render_template("cadastro.html")


@app.route("/vacinacao", methods=["GET", "POST"])
@login_required
def vacinacao():
  db = get_db()
  cursor = db.cursor()

  if request.method == "POST":
    animal = request.form.get("animal")
    nome_vacina = request.form.get("vacina")
    data_vacinacao = request.form.get("data_aplicacao") or request.form.get(
        "data_vacinacao"
    )
    proxima_dose = request.form.get("proxima_dose")
    responsavel = request.form.get("responsavel")

    cursor.execute(
        """
            INSERT INTO vacinacao (animal, vacina, data_vacinacao, data_aplicacao, proxima_dose, responsavel)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            animal,
            nome_vacina,
            data_vacinacao,
            data_vacinacao,
            proxima_dose,
            responsavel,
        ),
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

  cursor.execute("SELECT * FROM animais")
  animais = [dict(row) for row in cursor.fetchall()]

  cursor.execute("SELECT * FROM lotes")
  lotes = [dict(row) for row in cursor.fetchall()]

  cursor.execute("SELECT * FROM vacinacao")
  vacinacoes = [dict(row) for row in cursor.fetchall()]

  for v in vacinacoes:
    v["status"] = status_vacina(v.get("proxima_dose"))

  return render_template(
      "listagem.html", animais=animais, vacinacoes=vacinacoes, lotes=lotes
  )


# --- ROTAS DE AÇÃO (REMOÇÕES E ATUALIZAÇÕES) ---


@app.route("/animais/remover/<int:id>", methods=["POST"])
@login_required
def remover_animal_route(id):
  db = get_db()
  cursor = db.cursor()
  cursor.execute("DELETE FROM animais WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("listagem"))


@app.route("/lotes/remover/<int:id>", methods=["POST"])
@login_required
def remover_lote_route(id):
  db = get_db()
  cursor = db.cursor()
  cursor.execute("DELETE FROM lotes WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("listagem"))


@app.route("/vacinacao/remover/<int:id>", methods=["POST"])
@login_required
def remover_vacinacao_route(id):
  db = get_db()
  cursor = db.cursor()
  cursor.execute("DELETE FROM vacinacao WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("listagem"))


# ROTA QUE FALTAVA PARA CORRIGIR O ERRO:
@app.route("/vacinacao/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar_vacinacao_route(id):
  proxima_dose = request.form.get("proxima_dose")
  status = request.form.get("status")

  db = get_db()
  cursor = db.cursor()
  cursor.execute(
      """
        UPDATE vacinacao 
        SET proxima_dose = ?, status = ? 
        WHERE id = ?
    """,
      (proxima_dose, status, id),
  )
  db.commit()
  return redirect(url_for("listagem"))


if __name__ == "__main__":
  if not os.path.exists(DATABASE):
    init_db()

  app.run(debug=True)